"""
CrimeNet AI - Multi-Source Intelligence Ingestion & Entity Resolution Engine
Deconstructs, normalizes, and connects heterogeneous data streams:
1. Telecom Call Detail Records (CDR)
2. Core Banking & RTGS Financial Ledgers
3. Police First Information Reports (FIR)
4. Highway Automatic Number Plate Recognition (ANPR)
5. Digital Wallets, UPI & USDT Hawala Remittances

Generates verified intra-domain links and cross-domain identity & spatiotemporal links.
"""

import json
import math
import logging
import csv
import io
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.app.models.database import get_db
from backend.app.services.spatial_service import SpatialService
from backend.app.graph.sync import sync_entities_to_neo4j, sync_relationships_to_neo4j
from backend.app.database.connection import db_session_context
from backend.app.models.pg_models import TelecomRecord, ANPRRecord, BankingRecord, WalletRecord, FIRRecord

logger = logging.getLogger("crimenet.pipeline.ingestion")

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geographic coordinates in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)

def normalize_phone(phone: Optional[str]) -> str:
    """Normalizes phone numbers to standard searchable format."""
    if not phone:
        return ""
    clean = str(phone).strip().replace(" ", "").replace("-", "")
    if clean.startswith("+91"):
        return f"+91-{clean[3:]}"
    elif clean.startswith("+971"):
        return f"+971-{clean[4:]}"
    elif len(clean) == 10 and clean.isdigit():
        return f"+91-{clean}"
    return str(phone).strip()

def parse_iso_or_custom_timestamp(ts_str: str) -> Optional[datetime]:
    """Robust parser for varying timestamp formats across investigative logs."""
    if not ts_str:
        return None
    ts_str = str(ts_str).strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S UTC",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    return None

# ==============================================================================
# CURATED SYNTHETIC INVESTIGATIVE BENCHMARK DATASETS (5 DOMAINS)
# Interlocking syndicate scenario: Operation Blue Thunder
# ==============================================================================

SAMPLE_CDR_DATA: List[Dict[str, Any]] = [
    {"call_id": "CDR-2026-01", "caller": "+91-9876543210", "receiver": "+91-9845678901", "timestamp": "2026-03-12 01:34:10", "duration_sec": 342, "tower_id": "TOW-BANDRA-01", "tower_name": "Bandra-Worli Sea Link Tower", "imei": "354892019482019", "imsi": "404-45-891029", "lat": 19.0330, "lng": 72.8185, "call_type": "OUTBOUND_VOICE"},
    {"call_id": "CDR-2026-02", "caller": "+91-9845678901", "receiver": "+91-9765432109", "timestamp": "2026-03-12 01:52:05", "duration_sec": 185, "tower_id": "TOW-JUHU-4022", "tower_name": "Juhu North Base Station", "imei": "359182740192847", "imsi": "404-45-998811", "lat": 19.1075, "lng": 72.8263, "call_type": "OUTBOUND_VOICE"},
    {"call_id": "CDR-2026-03", "caller": "+91-9876543210", "receiver": "+971-501234567", "timestamp": "2026-03-12 02:14:40", "duration_sec": 512, "tower_id": "TOW-BANDRA-01", "tower_name": "Bandra-Worli Sea Link Tower", "imei": "354892019482019", "imsi": "404-45-891029", "lat": 19.0330, "lng": 72.8185, "call_type": "INTERNATIONAL_OUTBOUND"},
    {"call_id": "CDR-2026-04", "caller": "+91-9765432109", "receiver": "+91-9876543210", "timestamp": "2026-03-12 02:40:15", "duration_sec": 120, "tower_id": "TOW-AIRPORT-T2", "tower_name": "Sahar Airport T2 Sector 4", "imei": "351029384756102", "imsi": "404-45-776655", "lat": 19.0968, "lng": 72.8745, "call_type": "INBOUND_VOICE"},
    {"call_id": "CDR-2026-05", "caller": "+91-9876543210", "receiver": "+91-9822019283", "timestamp": "2026-03-12 03:05:00", "duration_sec": 45, "tower_id": "TOW-GOR-4041", "tower_name": "Goregaon East Industrial Tower", "imei": "354892019482019", "imsi": "404-45-891029", "lat": 19.1663, "lng": 72.8526, "call_type": "BURST_DISPATCH"}
]

SAMPLE_BANKING_DATA: List[Dict[str, Any]] = [
    {"txn_id": "TXN-RTGS-89101", "from_account": "ACC-891024", "from_name": "Mehta Enterprises Ltd", "to_account": "ACC-441209", "to_name": "Mule Account Hub A", "amount": 48500.0, "currency": "INR", "timestamp": "2026-03-12 01:45:00", "bank_name": "State Bank of India", "txn_type": "IMPS_MICRO_BURST", "narration": "Logistics invoice clearing 4912", "linked_phone": "+91-9876543210"},
    {"txn_id": "TXN-RTGS-89102", "from_account": "ACC-441209", "from_name": "Mule Account Hub A", "to_account": "ACC-992014", "to_name": "Phoenix Trading LLC", "amount": 450000.0, "currency": "INR", "timestamp": "2026-03-12 02:05:00", "bank_name": "HDFC Bank", "txn_type": "RTGS_WIRE", "narration": "Offshore consultancy advance", "linked_phone": "+91-9845678901"},
    {"txn_id": "TXN-RTGS-89103", "from_account": "ACC-110293", "from_name": "Priya Desai", "to_account": "ACC-771829", "to_name": "Desai Financial Consultancy", "amount": 125000.0, "currency": "INR", "timestamp": "2026-03-12 02:20:00", "bank_name": "ICICI Bank", "txn_type": "NEFT_SETTLEMENT", "narration": "Audit advisory fee Q1", "linked_phone": "+91-9765432109"},
    {"txn_id": "TXN-RTGS-89104", "from_account": "ACC-992014", "from_name": "Phoenix Trading LLC", "to_account": "ACC-CRYPTO-EXCH", "to_name": "Offshore Exchange Fiat Gateway", "amount": 980000.0, "currency": "INR", "timestamp": "2026-03-12 02:30:00", "bank_name": "Emirates NBD", "txn_type": "CROSS_BORDER_WIRE", "narration": "Digital asset escrow liquidity", "linked_phone": "+971-501234567"}
]

SAMPLE_FIR_DATA: List[Dict[str, Any]] = [
    {
        "fir_no": "FIR-2026-MUM-892",
        "police_station": "Bandra Cyber Crime Cell",
        "date": "2026-03-11",
        "ipc_sections": "Sections 420, 120B IPC, Sec 66D IT Act",
        "complainant": "Union Bank of India Fraud Monitoring Dept",
        "accused_name": "Arjun Mehta",
        "accused_role": "Syndicate Beneficiary",
        "suspect_phone": "+91-9876543210",
        "suspect_vehicle": "MH-02-DN-4912",
        "suspect_account": "ACC-891024",
        "incident_type": "ORGANIZED_FINANCIAL_DEFRAUDATION",
        "summary": "Coordinated unauthorized banking diversion routed via shell accounts and nocturnal communications."
    },
    {
        "fir_no": "FIR-2026-WOR-301",
        "police_station": "Worli Anti-Extortion Taskforce",
        "date": "2026-03-10",
        "ipc_sections": "Sections 384, 386, 120B IPC & MCOCA Sec 3",
        "complainant": "Apex Marine Logistics Consortium",
        "accused_name": "Vikram Singh",
        "accused_role": "Corridor Transit Enforcer",
        "suspect_phone": "+91-9845678901",
        "suspect_vehicle": "MH-04-KC-9011",
        "suspect_account": "ACC-441209",
        "incident_type": "EXTORTION_HAWALA_ROUTING",
        "summary": "Demands for protection payoffs channeled via Hawala middlemen and commercial vehicle logistics corridors."
    }
]

SAMPLE_ANPR_DATA: List[Dict[str, Any]] = [
    {
        "detection_id": "ANPR-BWSL-101",
        "plate_number": "MH-02-DN-4912",
        "camera_id": "CAM-BANDRA-TOLL-01",
        "location_name": "Bandra-Worli Sea Link Northbound Plaza",
        "timestamp": "2026-03-12 01:40:00",
        "lat": 19.0345,
        "lng": 72.8190,
        "vehicle_model": "Toyota Fortuner (Black)",
        "speed_kmh": 74.2,
        "registered_owner": "Arjun Mehta",
        "owner_phone": "+91-9876543210"
    },
    {
        "detection_id": "ANPR-JUHU-204",
        "plate_number": "MH-04-KC-9011",
        "camera_id": "CAM-JUHU-NORTH-04",
        "location_name": "Juhu Circle North Corridor",
        "timestamp": "2026-03-12 02:00:15",
        "lat": 19.1080,
        "lng": 72.8270,
        "vehicle_model": "Skoda Octavia (Silver)",
        "speed_kmh": 58.0,
        "registered_owner": "Vikram Singh",
        "owner_phone": "+91-9845678901"
    },
    {
        "detection_id": "ANPR-T2-309",
        "plate_number": "MH-01-AX-7700",
        "camera_id": "CAM-AIRPORT-T2-EXIT",
        "location_name": "Chhatrapati Shivaji Maharaj Airport T2 Departure Ramp",
        "timestamp": "2026-03-12 02:42:00",
        "lat": 19.0970,
        "lng": 72.8750,
        "vehicle_model": "Hyundai Creta (White)",
        "speed_kmh": 41.5,
        "registered_owner": "Priya Desai",
        "owner_phone": "+91-9765432109"
    }
]

SAMPLE_WALLET_DATA: List[Dict[str, Any]] = [
    {
        "wallet_txn_id": "WLT-UPI-00918",
        "sender_wallet": "WAL-UPI-ARJUN@OKAXIS",
        "sender_name": "Arjun Mehta",
        "receiver_wallet": "WAL-PAYTM-HAWALA01",
        "receiver_name": "Quick Cash Settlement Desk",
        "platform": "UPI_GPay",
        "amount": 95000.0,
        "timestamp": "2026-03-12 02:10:00",
        "sender_phone": "+91-9876543210",
        "receiver_phone": "+91-9822019283",
        "narration": "Cash token advance payment"
    },
    {
        "wallet_txn_id": "WLT-USDT-55410",
        "sender_wallet": "WAL-PAYTM-HAWALA01",
        "sender_name": "Quick Cash Settlement Desk",
        "receiver_wallet": "Crypto Tumbler Gateway",
        "receiver_name": "TRC20 Liquidity Pool",
        "platform": "USDT_TRC20",
        "amount": 3500.0,
        "timestamp": "2026-03-12 02:35:00",
        "sender_phone": "+91-9822019283",
        "receiver_phone": "+971-501234567",
        "narration": "Fiat-to-crypto off-ramp swap"
    },
    {
        "wallet_txn_id": "WLT-UPI-00919",
        "sender_wallet": "WAL-UPI-VIKRAM@PAYTM",
        "sender_name": "Vikram Singh",
        "receiver_wallet": "WAL-UPI-ARJUN@OKAXIS",
        "receiver_name": "Arjun Mehta",
        "platform": "UPI_Paytm",
        "amount": 42000.0,
        "timestamp": "2026-03-12 02:50:00",
        "sender_phone": "+91-9845678901",
        "receiver_phone": "+91-9876543210",
        "narration": "Corridor delivery reimbursement"
    }
]

# ==============================================================================
# PIPELINE INGESTION & CROSS-DOMAIN RESOLUTION ENGINE
# ==============================================================================

class MultiSourcePipeline:
    """Orchestrates parsing, entity normalization, intra-domain linkage,
    and cross-domain identity/spatiotemporal link synthesis.
    """

    @classmethod
    def parse_csv_content(cls, csv_text: str) -> List[Dict[str, Any]]:
        """Parses CSV string into standard dict records with header stripping."""
        reader = csv.DictReader(io.StringIO(csv_text.strip()))
        return [dict(row) for row in reader]

    @classmethod
    def process_and_link(
        cls,
        cdr_records: Optional[List[Dict[str, Any]]] = None,
        banking_records: Optional[List[Dict[str, Any]]] = None,
        fir_records: Optional[List[Dict[str, Any]]] = None,
        anpr_records: Optional[List[Dict[str, Any]]] = None,
        wallet_records: Optional[List[Dict[str, Any]]] = None,
        persist_to_db: bool = True
    ) -> Dict[str, Any]:
        """Main processing pipeline:
        1. Ingests and normalizes records from all 5 domains.
        2. Discovers entities (Persons, Phones, Accounts, Vehicles, Towers, Wallets, FIRs).
        3. Creates direct intra-domain edges (CALLED, WIRED, CHARGED, DETECTED, TRANSFERRED).
        4. Generates cross-domain links:
           - Phone KYC link (CDR ↔ Banking ↔ FIR ↔ ANPR ↔ Wallet)
           - Vehicle Suspect link (ANPR ↔ FIR ↔ Person)
           - Spatiotemporal Co-location link (CDR Tower ↔ ANPR Camera within 1.5km, 15min)
           - Fiat-to-Crypto Hawala bridge (Bank Wire ↔ Digital Wallet)
        5. Saves to SQLite and returns complete correlation intelligence.
        """
        cdr_records = cdr_records or []
        banking_records = banking_records or []
        fir_records = fir_records or []
        anpr_records = anpr_records or []
        wallet_records = wallet_records or []

        entities: Dict[str, Dict[str, Any]] = {}
        relationships: List[Dict[str, Any]] = []

        # Preload existing entities from SQLite to enable cross-domain correlation across sequential batch uploads
        if persist_to_db:
            try:
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, name, type, tier, category, risk_score, city, phone, dossier, metadata_json FROM graph_entities")
                    for row in cursor.fetchall():
                        r_name = str(row["name"]).strip()
                        if r_name:
                            m_json = {}
                            if "metadata_json" in row.keys() and row["metadata_json"]:
                                try:
                                    m_json = json.loads(row["metadata_json"])
                                except Exception:
                                    pass
                            entities[r_name] = {
                                "id": row["id"],
                                "name": r_name,
                                "type": row["type"],
                                "tier": row["tier"],
                                "category": row["category"],
                                "risk_score": float(row["risk_score"] or 50.0),
                                "city": row["city"] or "Mumbai",
                                "phone": row["phone"] or "",
                                "dossier": row["dossier"] or "",
                                "metadata": m_json
                            }
            except Exception as e:
                logger.warning(f"Could not preload existing entities for cross-domain link synthesis: {e}")

        def add_entity(name: str, ent_type: str, category: str = "general", risk_score: float = 50.0, city: str = "Mumbai", phone: str = "", dossier: str = "", metadata: Optional[Dict] = None):
            name_clean = str(name).strip()
            if not name_clean:
                return
            if name_clean not in entities:
                ent_hash = hashlib.sha256(name_clean.encode("utf-8")).hexdigest()[:12]
                ent_id = f"ent-{ent_type.lower()[:3]}-{ent_hash}"
                entities[name_clean] = {
                    "id": ent_id,
                    "name": name_clean,
                    "type": ent_type,
                    "tier": "operations" if risk_score > 70 else "general",
                    "category": category,
                    "risk_score": float(risk_score),
                    "city": city,
                    "phone": normalize_phone(phone),
                    "dossier": dossier,
                    "metadata": metadata or {}
                }
            else:
                # Merge phone / metadata
                if phone and not entities[name_clean]["phone"]:
                    entities[name_clean]["phone"] = normalize_phone(phone)
                if risk_score > entities[name_clean]["risk_score"]:
                    entities[name_clean]["risk_score"] = float(risk_score)

        def add_relationship(source: str, target: str, label: str, rel_type: str, confidence: float, weight: float, rationale: str, provenance: List[str]):
            s_clean = str(source).strip()
            t_clean = str(target).strip()
            if not s_clean or not t_clean or s_clean == t_clean:
                return
            
            # Check duplicate edge
            edge_key = f"{s_clean}->{t_clean}:{label}"
            for r in relationships:
                if f"{r['source']}->{r['target']}:{r['label']}" == edge_key:
                    r["weight"] += weight
                    r["confidence"] = max(r["confidence"], confidence)
                    r["provenance"] = list(set(r.get("provenance", []) + provenance))
                    return

            rel_hash = hashlib.sha256(edge_key.encode("utf-8")).hexdigest()[:12]
            rel_id = f"rel-{rel_hash}"
            relationships.append({
                "id": rel_id,
                "source": s_clean,
                "target": t_clean,
                "label": label,
                "type": rel_type,
                "confidence": round(float(confidence), 2),
                "weight": round(float(weight), 2),
                "rationale": rationale,
                "provenance": provenance
            })

        # ----------------------------------------------------------------------
        # 1. PROCESS CDR
        # ----------------------------------------------------------------------
        for r in cdr_records:
            caller = normalize_phone(r.get("caller"))
            receiver = normalize_phone(r.get("receiver"))
            tower_name = r.get("tower_name") or r.get("tower_id") or "CellTower Alpha"
            lat = float(r.get("lat") or 19.0760)
            lng = float(r.get("lng") or 72.8777)
            dur = float(r.get("duration_sec") or 60)

            add_entity(caller, "Phone", category="telecom", risk_score=75.0, phone=caller, dossier=f"Caller handset IMEI {r.get('imei', 'N/A')}")
            add_entity(receiver, "Phone", category="telecom", risk_score=70.0, phone=receiver, dossier="Target contact")
            add_entity(tower_name, "CellTower", category="infrastructure", risk_score=40.0, metadata={"lat": lat, "lng": lng, "tower_id": r.get("tower_id")})

            add_relationship(
                source=caller,
                target=receiver,
                label="CALLED",
                rel_type="COMMUNICATION",
                confidence=0.95,
                weight=round(dur / 60.0, 2),
                rationale=f"Voice call connection ({dur}s) recorded at {r.get('timestamp')}",
                provenance=["TELECOM_CDR"]
            )
            add_relationship(
                source=caller,
                target=tower_name,
                label="CONNECTS_TOWER",
                rel_type="GEOSPATIAL",
                confidence=0.92,
                weight=1.0,
                rationale=f"Cellular signal registered at {tower_name} (Tower {r.get('tower_id')})",
                provenance=["TELECOM_CDR"]
            )

        # ----------------------------------------------------------------------
        # 2. PROCESS BANKING
        # ----------------------------------------------------------------------
        for b in banking_records:
            from_acc = str(b.get("from_account", "")).strip()
            to_acc = str(b.get("to_account", "")).strip()
            from_name = str(b.get("from_name", from_acc)).strip()
            to_name = str(b.get("to_name", to_acc)).strip()
            amount = float(b.get("amount") or 0.0)
            phone = normalize_phone(b.get("linked_phone"))

            add_entity(from_name, "Organization" if "Ltd" in from_name or "LLC" in from_name else "Person", category="finance", risk_score=78.0, phone=phone, dossier=f"Originating account holder ({from_acc})")
            add_entity(from_acc, "FinancialAccount", category="bank_account", risk_score=72.0, dossier=f"{b.get('bank_name', 'Bank')} account")
            add_entity(to_name, "Organization" if "Ltd" in to_name or "LLC" in to_name else "Person", category="finance", risk_score=82.0, dossier=f"Beneficiary account holder ({to_acc})")
            add_entity(to_acc, "FinancialAccount", category="bank_account", risk_score=75.0, dossier="Destination account")

            # Ownership links
            add_relationship(from_name, from_acc, "HOLDS_ACCOUNT", "FINANCIAL", 0.99, 1.5, f"Verified bank account ownership ({from_acc})", ["BANKING_LEDGER"])
            add_relationship(to_name, to_acc, "HOLDS_ACCOUNT", "FINANCIAL", 0.99, 1.5, f"Verified bank account ownership ({to_acc})", ["BANKING_LEDGER"])

            # Transfer link
            add_relationship(
                source=from_acc,
                target=to_acc,
                label="FUNDS_TRANSFERRED",
                rel_type="FINANCIAL",
                confidence=0.98,
                weight=round(math.log10(max(amount, 10)), 2),
                rationale=f"Transfer of INR {amount:,.2f} via {b.get('txn_type', 'WIRE')} on {b.get('timestamp')}",
                provenance=["BANKING_LEDGER"]
            )

        # ----------------------------------------------------------------------
        # 3. PROCESS FIR
        # ----------------------------------------------------------------------
        for f in fir_records:
            fir_no = str(f.get("fir_no", "")).strip()
            accused = str(f.get("accused_name", "")).strip()
            complainant = str(f.get("complainant", "")).strip()
            suspect_phone = normalize_phone(f.get("suspect_phone"))
            suspect_vehicle = str(f.get("suspect_vehicle", "")).strip()
            suspect_account = str(f.get("suspect_account", "")).strip()

            add_entity(fir_no, "FIRCase", category="legal", risk_score=60.0, dossier=f"{f.get('police_station')} | IPC: {f.get('ipc_sections')}")
            if complainant:
                add_entity(complainant, "Organization" if "Bank" in complainant or "Corp" in complainant else "Person", category="victim", risk_score=20.0, dossier="Complainant")
                add_relationship(complainant, fir_no, "LODGED_FIR", "LEGAL", 1.0, 1.0, f"Lodged official police complaint {fir_no}", ["FIR_RECORDS"])

            if accused:
                add_entity(accused, "Person", category="suspect", risk_score=90.0, phone=suspect_phone, dossier=f"Named accused in {fir_no} under {f.get('ipc_sections')}")
                add_relationship(accused, fir_no, "NAMED_IN_FIR", "LEGAL", 1.0, 3.0, f"Accused under {f.get('ipc_sections')}", ["FIR_RECORDS"])

            if suspect_vehicle:
                add_entity(suspect_vehicle, "Vehicle", category="transport", risk_score=80.0, dossier=f"Vehicle cited in police investigation {fir_no}")
                if accused:
                    add_relationship(accused, suspect_vehicle, "OPERATES_VEHICLE", "TRANSPORT", 0.90, 1.8, f"Vehicle cited in FIR {fir_no}", ["FIR_RECORDS"])

            if suspect_account:
                add_entity(suspect_account, "FinancialAccount", category="mule_account", risk_score=85.0, dossier=f"Suspect account named in {fir_no}")
                add_relationship(fir_no, suspect_account, "FROZEN_UNDER_SECTION_102", "LEGAL", 0.95, 2.0, f"Account flagged in {fir_no}", ["FIR_RECORDS"])

        # ----------------------------------------------------------------------
        # 4. PROCESS ANPR
        # ----------------------------------------------------------------------
        for a in anpr_records:
            plate = str(a.get("plate_number", "")).strip()
            cam_name = a.get("location_name") or a.get("camera_id") or "ANPR Camera"
            owner = str(a.get("registered_owner", "")).strip()
            owner_phone = normalize_phone(a.get("owner_phone"))
            lat = float(a.get("lat") or 19.0760)
            lng = float(a.get("lng") or 72.8777)
            speed = float(a.get("speed_kmh") or 60.0)

            add_entity(plate, "Vehicle", category="transport", risk_score=75.0, phone=owner_phone, dossier=f"{a.get('vehicle_model', 'Vehicle')} (Reg Owner: {owner})")
            add_entity(cam_name, "CameraToll", category="infrastructure", risk_score=35.0, metadata={"lat": lat, "lng": lng, "camera_id": a.get("camera_id")})

            add_relationship(
                source=plate,
                target=cam_name,
                label="CAPTURED_AT_TOLL",
                rel_type="SURVEILLANCE",
                confidence=0.98,
                weight=1.5,
                rationale=f"Vehicle capture at {cam_name} ({speed} km/h) at {a.get('timestamp')}",
                provenance=["HIGHWAY_ANPR"]
            )

            if owner:
                add_entity(owner, "Person", category="suspect", risk_score=80.0, phone=owner_phone)
                add_relationship(owner, plate, "REGISTERED_OWNER", "OWNERSHIP", 0.99, 2.0, f"RTO registered vehicle owner of {plate}", ["HIGHWAY_ANPR"])

        # ----------------------------------------------------------------------
        # 5. PROCESS WALLETS & CRYPTO
        # ----------------------------------------------------------------------
        for w in wallet_records:
            sender_w = str(w.get("sender_wallet", "")).strip()
            receiver_w = str(w.get("receiver_wallet", "")).strip()
            s_name = str(w.get("sender_name", sender_w)).strip()
            r_name = str(w.get("receiver_name", receiver_w)).strip()
            platform = w.get("platform", "UPI")
            amount = float(w.get("amount") or 0.0)
            s_phone = normalize_phone(w.get("sender_phone"))
            r_phone = normalize_phone(w.get("receiver_phone"))

            add_entity(s_name, "Person", category="finance", risk_score=76.0, phone=s_phone, dossier=f"Wallet account holder ({sender_w})")
            add_entity(sender_w, "DigitalWallet", category="wallet", risk_score=74.0, dossier=f"{platform} wallet")
            add_entity(r_name, "Organization" if "Pool" in r_name or "Gateway" in r_name else "Person", category="finance", risk_score=85.0, phone=r_phone, dossier=f"Wallet receiver ({receiver_w})")
            add_entity(receiver_w, "DigitalWallet", category="wallet", risk_score=88.0, dossier=f"{platform} destination wallet")

            add_relationship(s_name, sender_w, "OWNS_WALLET", "FINANCIAL", 0.98, 1.5, f"Registered wallet handle ({platform})", ["DIGITAL_WALLET"])
            add_relationship(r_name, receiver_w, "OWNS_WALLET", "FINANCIAL", 0.98, 1.5, f"Registered wallet handle ({platform})", ["DIGITAL_WALLET"])

            add_relationship(
                source=sender_w,
                target=receiver_w,
                label="WALLET_TRANSFER",
                rel_type="CRYPTO" if "USDT" in platform or "TRC20" in platform else "FINANCIAL",
                confidence=0.97,
                weight=round(math.log10(max(amount, 10)), 2),
                rationale=f"Transfer of {amount:,.2f} ({platform}) on {w.get('timestamp')}",
                provenance=["DIGITAL_WALLET"]
            )

        # ======================================================================
        # CROSS-DOMAIN LINK GENERATION RULES
        # ======================================================================
        cross_domain_links_count = 0

        # RULE 1: Phone-Based Identity Correlation (CDR ↔ Banking ↔ FIR ↔ ANPR ↔ Wallet)
        phone_to_entities: Dict[str, List[Dict[str, Any]]] = {}
        for ent_name, ent_data in entities.items():
            ph = ent_data.get("phone")
            if ph and len(ph) >= 10:
                phone_to_entities.setdefault(ph, []).append(ent_data)

        for ph, matched_ents in phone_to_entities.items():
            if len(matched_ents) >= 2:
                for i in range(len(matched_ents)):
                    for j in range(i + 1, len(matched_ents)):
                        e1 = matched_ents[i]
                        e2 = matched_ents[j]
                        if e1["name"] != e2["name"] and e1["type"] != e2["type"]:
                            add_relationship(
                                source=e1["name"],
                                target=e2["name"],
                                label="CROSS_DOMAIN_IDENTITY",
                                rel_type="IDENTITY",
                                confidence=0.98,
                                weight=3.5,
                                rationale=f"Deterministic cross-domain link: {e1['type']} '{e1['name']}' and {e2['type']} '{e2['name']}' share verified phone identifier ({ph})",
                                provenance=["PHONE_IDENTITY_CORRELATION"]
                            )
                            cross_domain_links_count += 1

        # RULE 2: Vehicle-to-FIR Correlation (ANPR ↔ FIR Police Record)
        for a in anpr_records:
            plate = str(a.get("plate_number", "")).strip()
            for f in fir_records:
                fir_vehicle = str(f.get("suspect_vehicle", "")).strip()
                fir_no = str(f.get("fir_no", "")).strip()
                accused = str(f.get("accused_name", "")).strip()
                if plate and fir_vehicle and plate == fir_vehicle:
                    add_relationship(
                        source=plate,
                        target=fir_no,
                        label="SUSPECT_VEHICLE_CITED",
                        rel_type="FORENSIC_LINK",
                        confidence=0.99,
                        weight=3.2,
                        rationale=f"ANPR vehicle {plate} matches active police lookout in {fir_no} (Accused: {accused})",
                        provenance=["HIGHWAY_ANPR", "FIR_RECORDS"]
                    )
                    cross_domain_links_count += 1

        # RULE 3: Spatiotemporal Co-Location (CDR Cell Tower ↔ ANPR Toll Camera)
        for c in cdr_records:
            c_ts = parse_iso_or_custom_timestamp(c.get("timestamp"))
            c_lat = float(c.get("lat") or 0.0)
            c_lng = float(c.get("lng") or 0.0)
            c_caller = normalize_phone(c.get("caller"))

            if not c_ts or c_lat == 0.0 or c_lng == 0.0:
                continue

            for a in anpr_records:
                a_ts = parse_iso_or_custom_timestamp(a.get("timestamp"))
                a_lat = float(a.get("lat") or 0.0)
                a_lng = float(a.get("lng") or 0.0)
                a_plate = str(a.get("plate_number", "")).strip()
                a_owner_phone = normalize_phone(a.get("owner_phone"))

                if not a_ts or a_lat == 0.0 or a_lng == 0.0:
                    continue

                time_delta_min = abs((c_ts - a_ts).total_seconds()) / 60.0
                dist_m = SpatialService.calculate_distance_meters(c_lat, c_lng, a_lat, a_lng)
                dist_km = round(dist_m / 1000.0, 3)

                if dist_km <= 1.5 and time_delta_min <= 15.0:
                    tower_name = c.get("tower_name") or c.get("tower_id")
                    cam_name = a.get("location_name") or a.get("camera_id")
                    conf = 0.96 if c_caller == a_owner_phone else 0.88

                    add_relationship(
                        source=c_caller,
                        target=a_plate,
                        label="SPATIOTEMPORAL_CO_LOCATION",
                        rel_type="GEOSPATIAL",
                        confidence=conf,
                        weight=2.8,
                        rationale=f"Handset ping at {tower_name} coincides with vehicle {a_plate} at {cam_name} (Distance: {dist_m:.0f}m, Time gap: {time_delta_min:.1f} mins)",
                        provenance=["TELECOM_CDR", "HIGHWAY_ANPR"]
                    )
                    cross_domain_links_count += 1

        # RULE 4: Fiat-to-Wallet Hawala Gateway (Banking ↔ Digital Wallet)
        for b in banking_records:
            to_acc = str(b.get("to_account", ""))
            amount_bank = float(b.get("amount") or 0.0)
            b_phone = normalize_phone(b.get("linked_phone"))

            for w in wallet_records:
                w_phone = normalize_phone(w.get("sender_phone"))
                if b_phone and w_phone and b_phone == w_phone:
                    from_name = b.get("from_name", to_acc)
                    s_wallet = w.get("sender_wallet")
                    add_relationship(
                        source=from_name,
                        target=s_wallet,
                        label="HAWALA_ON_OFF_RAMP",
                        rel_type="FINANCIAL",
                        confidence=0.94,
                        weight=3.0,
                        rationale=f"Banking wire of INR {amount_bank:,.2f} followed by digital wallet dispersal via {w.get('platform')} linked to phone {b_phone}",
                        provenance=["BANKING_LEDGER", "DIGITAL_WALLET"]
                    )
                    cross_domain_links_count += 1

        # ----------------------------------------------------------------------
        # PERSISTENCE TO RELATIONAL SYSTEM OF RECORD & NEO4J PROJECTION
        # ----------------------------------------------------------------------
        if persist_to_db:
            with get_db() as conn:
                cursor = conn.cursor()
                for e in entities.values():
                    cursor.execute(
                        """INSERT INTO graph_entities (id, name, type, tier, category, risk_score, city, phone, dossier, metadata_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ON CONFLICT(name) DO UPDATE SET
                             risk_score = MAX(risk_score, excluded.risk_score),
                             phone = CASE WHEN phone = '' OR phone IS NULL THEN excluded.phone ELSE phone END,
                             dossier = CASE WHEN dossier = '' OR dossier IS NULL THEN excluded.dossier ELSE dossier END
                        """,
                        (e["id"], e["name"], e["type"], e["tier"], e["category"], e["risk_score"], e["city"], e["phone"], e["dossier"], json.dumps(e.get("metadata", {})))
                    )

                for r in relationships:
                    cursor.execute(
                        """INSERT OR REPLACE INTO graph_relationships (id, source, target, label, type, confidence, weight, metadata_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            r["id"],
                            r["source"],
                            r["target"],
                            r["label"],
                            r["type"],
                            r["confidence"],
                            r["weight"],
                            json.dumps({"rationale": r["rationale"], "provenance": r.get("provenance", [])})
                        )
                    )

            # Project updated topology into Neo4j Graph DB
            try:
                sync_entities_to_neo4j(list(entities.values()))
                sync_relationships_to_neo4j(relationships)
            except Exception as se:
                logger.warning("Neo4j projection sync during ingestion deferred: %s", se)

        return {
            "status": "PIPELINE_EXECUTED_SUCCESS",
            "counts": {
                "cdr_records": len(cdr_records),
                "banking_records": len(banking_records),
                "fir_records": len(fir_records),
                "anpr_records": len(anpr_records),
                "wallet_records": len(wallet_records),
                "total_records_ingested": len(cdr_records) + len(banking_records) + len(fir_records) + len(anpr_records) + len(wallet_records),
                "entities_resolved": len(entities),
                "total_links_generated": len(relationships),
                "cross_domain_links_discovered": cross_domain_links_count
            },
            "entities": list(entities.values()),
            "links": relationships
        }
