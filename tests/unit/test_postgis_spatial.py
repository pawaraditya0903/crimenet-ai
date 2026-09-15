"""
CrimeNet AI - PostGIS & Geospatial Spatial Analysis Unit Tests
Tests spatial distance calculation (PostGIS ST_Distance / Haversine fallback),
spatiotemporal co-location filtering within investigative thresholds (d <= 1.5km, Δt <= 15 min),
and compliance with statutory advisory disclaimers.
"""

import pytest
import math
from backend.app.services.spatial_service import (
    SpatialService,
    haversine_distance_meters,
    SPATIOTEMPORAL_DISCLAIMER
)

def test_haversine_and_spatial_distance_calculation():
    """Verify high-precision distance calculation between known landmarks in Mumbai."""
    # Gateway of India (18.9220, 72.8347) to Nariman Point (18.9256, 72.8242)
    lat1, lon1 = 18.9220, 72.8347
    lat2, lon2 = 18.9256, 72.8242

    dist_haversine = haversine_distance_meters(lat1, lon1, lat2, lon2)
    dist_service = SpatialService.calculate_distance_meters(lat1, lon1, lat2, lon2)

    # Distance between Gateway and Nariman Point is approximately 1.17 km (1100m - 1250m)
    assert 1100.0 <= dist_haversine <= 1250.0
    assert 1100.0 <= dist_service <= 1250.0

    # Distance to identical point must be zero
    assert haversine_distance_meters(lat1, lon1, lat1, lon1) == 0.0
    assert SpatialService.calculate_distance_meters(lat1, lon1, lat1, lon1) == 0.0

def test_spatiotemporal_colocation_threshold_enforcement():
    """Verify that co-locations strictly obey the 1.5 km and 15-minute bounds."""
    colocations = SpatialService.find_spatiotemporal_colocations(
        max_distance_km=1.5,
        max_time_diff_minutes=15.0
    )

    # If test database has seeded coincident records, inspect their bounds
    for match in colocations:
        assert match["distance_meters"] <= 1500.0
        assert match["distance_km"] <= 1.5
        assert match["time_gap_minutes"] <= 15.0
        assert "disclaimer" in match
        assert match["disclaimer"] == SPATIOTEMPORAL_DISCLAIMER

def test_format_colocation_result_statutory_disclaimer():
    """Verify structured result contains statutory non-culpability warning and provenance."""
    sample_data = {
        "caller": "+919820011223",
        "call_id": "call-101",
        "tower_name": "Worli Sea Face Tower 4",
        "c_timestamp": "2026-03-12 14:00:00",
        "plate_number": "MH-01-AB-1234",
        "detection_id": "det-202",
        "cam_name": "Bandra-Worli Sealink Toll Plaza",
        "registered_owner": "Vikram Singhania",
        "owner_phone": "+919820011223",
        "a_timestamp": "2026-03-12 14:08:00"
    }

    formatted = SpatialService._format_colocation_result(sample_data, dist_m=650.0, time_diff_min=8.0)

    assert formatted["source_phone"] == "+919820011223"
    assert formatted["target_vehicle"] == "MH-01-AB-1234"
    assert formatted["distance_meters"] == 650.0
    assert formatted["distance_km"] == 0.65
    assert formatted["time_gap_minutes"] == 8.0
    assert formatted["confidence_score"] >= 0.88
    assert "SPATIOTEMPORAL INVESTIGATIVE NOTICE" in formatted["disclaimer"]
    assert "Δt <= 15 min" in formatted["disclaimer"]
    assert "d <= 1.5 km" in formatted["disclaimer"]
    assert "does NOT establish criminal conspiracy" in formatted["disclaimer"]

def test_timestamp_parsing_robustness():
    """Verify ISO-8601, UTC strings, and standard SQL datetime parsing."""
    t1 = SpatialService._parse_timestamp("2026-03-12 14:08:00")
    assert t1 is not None
    assert t1.year == 2026 and t1.month == 3 and t1.day == 12

    t2 = SpatialService._parse_timestamp("2026-03-12 14:08:00 UTC")
    assert t2 is not None
    assert t2.hour == 14 and t2.minute == 8

    t3 = SpatialService._parse_timestamp("2026-03-12T14:08:00Z")
    assert t3 is not None

    invalid = SpatialService._parse_timestamp("not-a-valid-timestamp")
    assert invalid is None
