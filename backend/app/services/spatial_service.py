"""
CrimeNet AI - PostGIS Geospatial & Spatiotemporal Service
Performs database-level spatial computations using PostGIS functions:
ST_Distance, ST_DWithin, ST_MakePoint, and GiST spatial indexes.

Preserves the established investigative thresholds:
- Temporal threshold: Δt <= 15 minutes
- Spatial threshold: distance <= 1.5 km
Strictly enforces the rule: Co-location is an investigative lead requiring human review,
NOT legal proof of criminal association.
"""

import math
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import text
from backend.app.database.connection import db_session_context, get_engine
from backend.app.models.pg_models import CellTower, TelecomRecord, ANPRRecord, ANPRCamera

logger = logging.getLogger("crimenet.services.spatial")

SPATIOTEMPORAL_DISCLAIMER = (
    "SPATIOTEMPORAL INVESTIGATIVE NOTICE: Physical and temporal proximity indicates co-location "
    "within specified cellular sector and traffic sensor corridors (Δt <= 15 min, d <= 1.5 km). "
    "It constitutes an investigative signal requiring human validation and does NOT establish "
    "criminal conspiracy, direct contact, or culpability."
)

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formula fallback for SQLite testing environments."""
    R = 6371000.0  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

class SpatialService:
    @staticmethod
    def calculate_distance_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculates distance between two WGS-84 points using PostGIS geography or fallback."""
        engine = get_engine()
        if engine.dialect.name == "postgresql":
            sql = text("""
                SELECT ST_Distance(
                    ST_SetSRID(ST_MakePoint(:lng1, :lat1), 4326)::geography,
                    ST_SetSRID(ST_MakePoint(:lng2, :lat2), 4326)::geography
                ) as distance_meters;
            """)
            with engine.connect() as conn:
                try:
                    res = conn.execute(sql, {"lat1": lat1, "lng1": lng1, "lat2": lat2, "lng2": lng2}).scalar()
                    return round(float(res or 0.0), 1)
                except Exception as e:
                    logger.warning("PostGIS ST_Distance calculation failed (%s), using Haversine fallback.", e)
        
        return haversine_distance_meters(lat1, lng1, lat2, lng2)

    @classmethod
    def find_spatiotemporal_colocations(
        cls,
        max_distance_km: float = 1.5,
        max_time_diff_minutes: float = 15.0
    ) -> List[Dict[str, Any]]:
        """Identifies coincident cellular handset pings and vehicle ANPR sightings.
        Uses PostGIS ST_DWithin on spatial geography if PostgreSQL is active,
        or queries indexed coordinate columns with math filtering.
        """
        engine = get_engine()
        max_dist_meters = max_distance_km * 1000.0
        results: List[Dict[str, Any]] = []

        if engine.dialect.name == "postgresql":
            # Native PostGIS Spatial Co-Location Query
            sql = text("""
                SELECT 
                    c.caller,
                    c.call_id,
                    c.tower_name,
                    c.lat as c_lat,
                    c.lng as c_lng,
                    c.timestamp as c_timestamp,
                    a.plate_number,
                    a.detection_id,
                    a.location_name as cam_name,
                    a.registered_owner,
                    a.owner_phone,
                    a.lat as a_lat,
                    a.lng as a_lng,
                    a.timestamp as a_timestamp,
                    ROUND(ST_Distance(c.geom::geography, a.geom::geography)::numeric, 1) as distance_meters
                FROM cdr_records c
                JOIN anpr_records a
                  ON c.geom IS NOT NULL 
                 AND a.geom IS NOT NULL
                 AND ST_DWithin(c.geom::geography, a.geom::geography, :max_dist)
            """)
            with engine.connect() as conn:
                try:
                    rows = conn.execute(sql, {"max_dist": max_dist_meters}).fetchall()
                    for r in rows:
                        row_dict = dict(r._mapping)
                        # Parse timestamps to compute exact temporal delta
                        c_ts = cls._parse_timestamp(row_dict["c_timestamp"])
                        a_ts = cls._parse_timestamp(row_dict["a_timestamp"])
                        if c_ts and a_ts:
                            time_diff_min = abs((c_ts - a_ts).total_seconds()) / 60.0
                            if time_diff_min <= max_time_diff_minutes:
                                results.append(cls._format_colocation_result(row_dict, row_dict["distance_meters"], time_diff_min))
                    return results
                except Exception as e:
                    logger.warning("PostGIS spatiotemporal query fallback triggered: %s", e)

        # Relational fallback (queries stored CDR and ANPR records)
        with db_session_context() as session:
            cdrs = session.query(TelecomRecord).filter(TelecomRecord.lat.isnot(None), TelecomRecord.lng.isnot(None)).all()
            anprs = session.query(ANPRRecord).filter(ANPRRecord.lat.isnot(None), ANPRRecord.lng.isnot(None)).all()

            for c in cdrs:
                c_ts = cls._parse_timestamp(c.timestamp)
                if not c_ts or not c.lat or not c.lng:
                    continue

                for a in anprs:
                    a_ts = cls._parse_timestamp(a.timestamp)
                    if not a_ts or not a.lat or not a.lng:
                        continue

                    time_diff_min = abs((c_ts - a_ts).total_seconds()) / 60.0
                    if time_diff_min > max_time_diff_minutes:
                        continue

                    dist_m = haversine_distance_meters(c.lat, c.lng, a.lat, a.lng)
                    if dist_m <= max_dist_meters:
                        data = {
                            "caller": c.caller,
                            "call_id": c.call_id,
                            "tower_name": c.tower_name,
                            "c_timestamp": c.timestamp,
                            "plate_number": a.plate_number,
                            "detection_id": a.detection_id,
                            "cam_name": a.location_name,
                            "registered_owner": a.registered_owner,
                            "owner_phone": a.owner_phone,
                            "a_timestamp": a.timestamp
                        }
                        results.append(cls._format_colocation_result(data, dist_m, time_diff_min))

        return results

    @staticmethod
    def _format_colocation_result(d: Dict[str, Any], dist_m: float, time_diff_min: float) -> Dict[str, Any]:
        caller = d.get("caller", "")
        plate = d.get("plate_number", "")
        owner_phone = d.get("owner_phone", "")
        conf = 0.96 if caller == owner_phone else 0.88
        tower = d.get("tower_name") or "Cell Tower"
        cam = d.get("cam_name") or "Toll Plaza"

        return {
            "source_phone": caller,
            "target_vehicle": plate,
            "registered_owner": d.get("registered_owner", "Unknown"),
            "cellular_call_id": d.get("call_id"),
            "anpr_detection_id": d.get("detection_id"),
            "tower_location": tower,
            "camera_location": cam,
            "distance_meters": dist_m,
            "distance_km": round(dist_m / 1000.0, 3),
            "time_gap_minutes": round(time_diff_min, 1),
            "co_location_label": "SPATIOTEMPORAL_CO_LOCATION",
            "confidence_score": conf,
            "rationale": f"Handset ping at {tower} coincides with vehicle {plate} at {cam} (Distance: {dist_m:.0f}m, Time gap: {time_diff_min:.1f} mins)",
            "disclaimer": SPATIOTEMPORAL_DISCLAIMER
        }

    @staticmethod
    def _parse_timestamp(ts_str: Optional[str]) -> Optional[datetime]:
        if not ts_str:
            return None
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S UTC",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(ts_str.strip(), fmt)
            except ValueError:
                continue
        return None
