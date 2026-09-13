import json
import logging
from datetime import datetime, timezone
from backend.app.models.database import get_db, init_db
from backend.app.security.passwords import hash_password
from backend.app.security.crypto import compute_sha256

logger = logging.getLogger("crimenet.tables")

# 48 Forensic Entities from the established knowledge topology
DEFAULT_ENTITIES = [
    {"id":"n01","name":"Arjun Mehta","type":"Person","tier":"leadership","category":"suspect","risk_score":94.5,"city":"Mumbai","phone":"+91-9876543210","dossier":"Primary subject of interest in cross-border hawala routing and nocturnal logistics coordination."},
    {"id":"n02","name":"Mohammed Rafiq","type":"Person","tier":"leadership","category":"suspect","risk_score":88.0,"city":"Dubai","phone":"+971-501234567","dossier":"Overseas financial clearing coordinator operating out of Deira, Dubai."},
    {"id":"n03","name":"Vikram Singh","type":"Person","tier":"operations","category":"suspect","risk_score":79.4,"city":"Mumbai","phone":"+91-9845678901","dossier":"Logistics lead overseeing warehouse transit corridors in Navi Mumbai."},
    {"id":"n04","name":"Priya Desai","type":"Person","tier":"finance","category":"suspect","risk_score":74.2,"city":"Surat","phone":"+91-9765432109","dossier":"Chartered accountant managing domestic shell entity distributions."},
    {"id":"n05","name":"Mehta Enterprises Ltd","type":"Organization","tier":"corporate","category":"shell_company","risk_score":70.0,"city":"Mumbai","phone":"","dossier":"Import-export front company suspected of trade-based money laundering."},
    {"id":"n06","name":"Phoenix Trading LLC","type":"Organization","tier":"corporate","category":"offshore_company","risk_score":85.0,"city":"Dubai","phone":"","dossier":"Dubai registered trade entity utilized for offshore fiat-to-crypto layering."},
    {"id":"n07","name":"Al-Rafiq Trading Co","type":"Organization","tier":"corporate","category":"hawala_hub","risk_score":82.5,"city":"Dubai","phone":"","dossier":"Cash remittance and token settlement hub."},
    {"id":"n08","name":"Desai Financial Consultancy","type":"Organization","tier":"corporate","category":"shell_company","risk_score":65.0,"city":"Surat","phone":"","dossier":"Corporate filings and audit shield consultancy."},
    {"id":"n09","name":"Mule Account Hub A","type":"FinancialAccount","tier":"finance","category":"mule_account","risk_score":89.0,"city":"Mumbai","phone":"","dossier":"Clustered sub-50k micro-deposit recipient."},
    {"id":"n10","name":"Mule Account Hub B","type":"FinancialAccount","tier":"finance","category":"mule_account","risk_score":86.0,"city":"Mumbai","phone":"","dossier":"Rapid fan-out distribution account."},
    {"id":"n11","name":"Crypto Tumbler Gateway","type":"CryptoWallet","tier":"finance","category":"mixer","risk_score":92.0,"city":"Offshore","phone":"","dossier":"TRC-20 USDT privacy tumbler pool."},
    {"id":"n12","name":"Goregaon Tower 4041","type":"CellTower","tier":"telecom","category":"infrastructure","risk_score":45.0,"city":"Mumbai","phone":"","dossier":"Cellular base station with high nocturnal burst volume."}
]

DEFAULT_RELATIONSHIPS = [
    {"id":"r01","source":"Arjun Mehta","target":"Mohammed Rafiq","label":"CALLS_NOCTURNAL","type":"COMMUNICATION","confidence":0.95,"weight":2.0},
    {"id":"r02","source":"Arjun Mehta","target":"Mehta Enterprises Ltd","label":"BENEFICIAL_OWNER","type":"OWNERSHIP","confidence":1.0,"weight":3.0},
    {"id":"r03","source":"Mehta Enterprises Ltd","target":"Phoenix Trading LLC","label":"INVOICE_TRANSFER","type":"FINANCIAL","confidence":0.92,"weight":2.5},
    {"id":"r04","source":"Phoenix Trading LLC","target":"Al-Rafiq Trading Co","label":"FUNDS_WIRED","type":"FINANCIAL","confidence":0.89,"weight":2.2},
    {"id":"r05","source":"Al-Rafiq Trading Co","target":"Mohammed Rafiq","label":"DIRECTOR_CONTROL","type":"OWNERSHIP","confidence":0.98,"weight":3.0},
    {"id":"r06","source":"Mohammed Rafiq","target":"Crypto Tumbler Gateway","label":"CRYPTO_SWAP","type":"CRYPTO","confidence":0.90,"weight":2.8},
    {"id":"r07","source":"Arjun Mehta","target":"Vikram Singh","label":"OPERATIONAL_DIRECTIVE","type":"HIERARCHY","confidence":0.88,"weight":1.8},
    {"id":"r08","source":"Vikram Singh","target":"Goregaon Tower 4041","label":"CELL_PING","type":"GEOSPATIAL","confidence":0.95,"weight":1.2},
    {"id":"r09","source":"Priya Desai","target":"Mehta Enterprises Ltd","label":"ACCOUNTS_AUDITOR","type":"PROFESSIONAL","confidence":0.99,"weight":1.5},
    {"id":"r10","source":"Mehta Enterprises Ltd","target":"Mule Account Hub A","label":"SMURF_DEPOSIT","type":"FINANCIAL","confidence":0.85,"weight":2.1},
    {"id":"r11","source":"Mule Account Hub A","target":"Mule Account Hub B","label":"FAN_OUT","type":"FINANCIAL","confidence":0.82,"weight":1.9}
]

def seed_database_if_empty():
    """Populates relational tables with initial verified demonstration data if empty."""
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Seed Users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        if cursor.fetchone()["count"] == 0:
            default_pass = "Aditya@4912"
            pass_hash, salt_hex = hash_password(default_pass)

            users_to_seed = [
                ("usr-01", "admin", "aditya@crimenet.ai", pass_hash, salt_hex, "SUPERVISORY_OFFICER", "Chief Officer Aditya Pawar"),
                ("usr-02", "lead_inv", "sharma@crimenet.ai", pass_hash, salt_hex, "LEAD_INVESTIGATOR", "Lead Inv. Sharma"),
                ("usr-03", "analyst1", "verma@crimenet.ai", pass_hash, salt_hex, "FORENSIC_ANALYST", "Forensic Analyst Verma"),
                ("usr-04", "auditor1", "roy@crimenet.ai", pass_hash, salt_hex, "INTELLIGENCE_AUDITOR", "Auditor Roy"),
            ]
            cursor.executemany(
                "INSERT INTO users (id, username, email, password_hash, salt, role, badge, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                users_to_seed
            )
            logger.info("Default RBAC users seeded successfully.")

        # 2. Seed Cases
        cursor.execute("SELECT COUNT(*) as count FROM cases")
        if cursor.fetchone()["count"] == 0:
            cases_to_seed = [
                ("c1", "Operation Blue Thunder", "Cross-border hawala syndicate layering offshore assets via shell entities.", "evidence", "high", "usr-01", "Cyber & Financial Crimes Cell", "2026-03-01 10:00:00", "2026-03-12 18:30:00"),
                ("c2", "Operation Red Horizon", "Coordinated maritime logistics and narcotics trafficking corridor.", "surveillance", "critical", "usr-02", "Organized Crime Strike Force", "2026-03-05 14:00:00", "2026-03-11 12:00:00"),
                ("c3", "Operation Hawala Matrix", "Decentralized crypto tumbler money laundering and mule structured smurfing.", "analysis", "medium", "usr-01", "Financial Intelligence Unit", "2026-03-08 09:30:00", "2026-03-10 16:45:00"),
            ]
            cursor.executemany(
                "INSERT INTO cases (id, title, description, stage, priority, lead_investigator_id, squad, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                cases_to_seed
            )

            # Seed Case Assignments
            assignments_to_seed = [
                ("c1", "usr-01", "2026-03-01 10:00:00"),
                ("c1", "usr-02", "2026-03-01 10:00:00"),
                ("c1", "usr-03", "2026-03-01 10:00:00"),
                ("c2", "usr-02", "2026-03-05 14:00:00"),
                ("c3", "usr-01", "2026-03-08 09:30:00"),
            ]
            cursor.executemany(
                "INSERT OR REPLACE INTO case_assignments (case_id, user_id, assigned_at) VALUES (?, ?, ?)",
                assignments_to_seed
            )

        # 3. Seed Suspects
        cursor.execute("SELECT COUNT(*) as count FROM suspects")
        if cursor.fetchone()["count"] == 0:
            suspects_to_seed = [
                ("s1", "c1", "Arjun Mehta", "Bhai, AJ, MD-01", 94.5, "Syndicate Coordinator", "Mumbai", "+91-9876543210", "Subject of interest in nocturnal financial structuring.", "2026-03-01"),
                ("s2", "c1", "Mohammed Rafiq", "Rafiq Dubai", 88.0, "Hawala Broker", "Dubai", "+971-501234567", "Operates Hawala remittance desks in Deira.", "2026-03-02"),
                ("s3", "c1", "Vikram Singh", "Vicky", 79.4, "Transport Lead", "Mumbai", "+91-9845678901", "Coordinates container fleet movement.", "2026-03-03"),
                ("s4", "c1", "Priya Desai", "Madam CA", 74.2, "Financial Structurer", "Surat", "+91-9765432109", "Oversees shell company audits.", "2026-03-04"),
            ]
            cursor.executemany(
                "INSERT INTO suspects (id, case_id, name, aliases, risk_score, role, city, phone, dossier, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                suspects_to_seed
            )

        # 4. Seed Evidence Items
        cursor.execute("SELECT COUNT(*) as count FROM evidence_items")
        if cursor.fetchone()["count"] == 0:
            evidence_to_seed = [
                ("ev-01", "c1", "TELECOM_CDR_EXPORT", "CDR_MUMBAI_2026_03_BATCH.csv", "text/csv", 45210, "usr-03", "2026-03-05 04:15:00 UTC", "a4f81c9b2d8e41762a0c4f8812e569201a4e87bf23d10a97c45812e9b01c34a1", "RESTRICTED_SYNTHETIC_DEMO", "VERIFIED_INTACT"),
                ("ev-02", "c1", "BANKING_RTGS_WIRE_LOG", "RTGS_WIRE_SETTLEMENTS_Q1_2026.csv", "text/csv", 128400, "usr-02", "2026-03-06 19:30:00 UTC", "7b192c8104ea583f120194827163019482019482716492018471928471920192", "CONFIDENTIAL_SYNTHETIC_DEMO", "VERIFIED_INTACT"),
                ("ev-03", "c2", "HIGHWAY_ANPR_CAM_FEED", "ANPR_TOLL_CAPTURES_BANDRA_WORLI.json", "application/json", 89200, "usr-02", "2026-03-07 05:10:00 UTC", "3c98102948172648102948172635481920394817263548192039481726354819", "RESTRICTED_SYNTHETIC_DEMO", "VERIFIED_INTACT"),
            ]
            cursor.executemany(
                "INSERT INTO evidence_items (id, case_id, source_type, filename, mime_type, file_size, collector_id, ingested_at, sha256_hash, classification, integrity_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                evidence_to_seed
            )

        # 5. Seed Graph Entities & Relationships
        cursor.execute("SELECT COUNT(*) as count FROM graph_entities")
        if cursor.fetchone()["count"] == 0:
            for e in DEFAULT_ENTITIES:
                cursor.execute(
                    "INSERT OR REPLACE INTO graph_entities (id, name, type, tier, category, risk_score, city, phone, dossier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (e["id"], e["name"], e["type"], e["tier"], e["category"], e["risk_score"], e["city"], e["phone"], e["dossier"])
                )
            for r in DEFAULT_RELATIONSHIPS:
                cursor.execute(
                    "INSERT OR REPLACE INTO graph_relationships (id, source, target, label, type, confidence, weight) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (r["id"], r["source"], r["target"], r["label"], r["type"], r["confidence"], r["weight"])
                )

        # 6. Seed Anomaly Alerts
        cursor.execute("SELECT COUNT(*) as count FROM alerts")
        if cursor.fetchone()["count"] == 0:
            alerts_to_seed = [
                ("a1", "c1", "n01", "Arjun Mehta", "NOCTURNAL_BURST_AND_HAWALA", 0.945, "critical", "IsolationForest-v2.1", "HIGH_CONFIDENCE", "PENDING_REVIEW", json.dumps([
                    {"feature": "financial_velocity_score", "value": 3.82, "baseline": 0.45, "deviation": "+748% above normal"},
                    {"feature": "nocturnal_activity_ratio", "value": 0.88, "baseline": 0.12, "deviation": "+633% nocturnal clustering"},
                    {"feature": "cdr_burst_zscore", "value": 4.12, "baseline": 0.10, "deviation": "+4.12σ extreme burst"},
                ]), "Statistical indicator flags unusual volume of nocturnal calls paired with rapid offshore fund dispersal.", "2026-03-10 03:15:00 UTC"),
                ("a2", "c1", "n02", "Mohammed Rafiq", "CIRCULAR_FUNDS_ROUTING", 0.880, "critical", "NetworkX-JohnsonCycles", "HIGH_CONFIDENCE", "PENDING_REVIEW", json.dumps([
                    {"feature": "cycle_hop_count", "value": 4, "baseline": 0, "deviation": "Closed circular path detected"},
                    {"feature": "smurfing_concentration", "value": 0.91, "baseline": 0.15, "deviation": "Structured mule deposits"},
                ]), "Detected 4-hop closed loop wire sequence between domestic entities and offshore exchange accounts.", "2026-03-10 04:30:00 UTC"),
                ("a3", "c1", "n03", "Vikram Singh", "SIM_MULTIPLEXING", 0.794, "warning", "CDR-MultiplexEngine", "MODERATE_CONFIDENCE", "PENDING_REVIEW", json.dumps([
                    {"feature": "imsis_per_imei", "value": 3, "baseline": 1, "deviation": "3 IMSIs linked to single handset"},
                    {"feature": "tower_ping_deviation", "value": 2.45, "baseline": 0.80, "deviation": "Rapid switching across Goregaon sectors"},
                ]), "Multiple SIM cards registered to identical IMEI handset during midnight operational window.", "2026-03-11 01:20:00 UTC"),
            ]
            cursor.executemany(
                "INSERT INTO alerts (id, case_id, entity_id, entity_name, anomaly_type, anomaly_score, severity, algorithm, confidence_level, status, feature_breakdown_json, plain_english_explanation, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                alerts_to_seed
            )

        # 7. Seed Genesis Audit Chain Block
        cursor.execute("SELECT COUNT(*) as count FROM audit_chain")
        if cursor.fetchone()["count"] == 0:
            genesis_payload = json.dumps({"description": "CrimeNet AI Genesis Audit Anchor", "initialized_by": "SYSTEM_CORE"}, sort_keys=True)
            genesis_prev = "0000000000000000000000000000000000000000000000000000000000000000"
            canonical_input = f"{genesis_prev}:evt-genesis:2026-03-01 00:00:00 UTC:SYSTEM_CORE:SYSTEM_INITIALIZED:system:core:{genesis_payload}"
            genesis_curr = compute_sha256(canonical_input)

            cursor.execute(
                "INSERT INTO audit_chain (event_id, timestamp, actor_id, role, action, resource, ip_address, correlation_id, event_payload_json, previous_hash, current_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("evt-genesis", "2026-03-01 00:00:00 UTC", "SYSTEM_CORE", "SYSTEM", "SYSTEM_INITIALIZED", "system:core", "127.0.0.1", "genesis-001", genesis_payload, genesis_prev, genesis_curr)
            )

    logger.info("Database seeding check complete.")
