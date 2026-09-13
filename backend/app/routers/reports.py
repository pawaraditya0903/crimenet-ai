import uuid
import networkx as nx
from fastapi import APIRouter, HTTPException, Depends, Response
from backend.app.security.rbac import require_authenticated_user
from backend.app.models.database import get_db
from backend.app.forensics.report_builder import build_pdf_report, build_bsa_certificate_pdf
from backend.app.graph.engine import build_network_graph
from backend.app.graph.centrality import compute_centralities

router = APIRouter(prefix="/api/reports", tags=["Forensic Reports"])

@router.get("/templates")
async def get_report_templates():
    """Returns available forensic report templates matching the platform UI."""
    return {
        "templates": [
            {
                "id": "full",
                "name": "1. Full Profile Dossier",
                "description": "Complete biography, aliases, lieutenants, shell company holdings & warrants"
            },
            {
                "id": "network",
                "name": "2. Network Topology Report",
                "description": "Mathematical PageRank, Betweenness centrality, clusters & edge confidence"
            },
            {
                "id": "risk",
                "name": "3. Risk & Threat Assessment",
                "description": "Isolation Forest anomaly vectors, ₹1.5 Cr midnight transfer & PMLA warrants"
            },
            {
                "id": "timeline",
                "name": "4. CDR & Telecom Timeline",
                "description": "Call Detail Records table, nocturnal calling spikes (01:30 AM) & tower IDs"
            },
            {
                "id": "evidence",
                "name": "5. Digital Evidence Custody Ledger",
                "description": "SHA-256 bit-level integrity records, Case Merkle root, and ingestion chronology."
            }
        ]
    }

CANONICAL_DOSSIERS = {
    "Arjun Mehta": {
        "aliases": "Bhai, AJ, MD-01, CryptoHawk99",
        "role": "Syndicate Mastermind / Key Regional Coordinator",
        "city": "Mumbai, Maharashtra",
        "phone": "+91-9876543210",
        "risk_score": 94.5,
        "financial_flag": "₹1,50,00,000 midnight transfer @ 02:00 AM IST to offshore accounts",
        "telecom_detail": "IMEI 354892019482019 · Sector 4041 Goregaon · 42.8% nocturnal calling ratio",
        "legal_action": "24/7 non-bailable surveillance & detention order active under Section 5(2) Indian Telegraph Act & BNSS 2023.",
        "community": "Cluster 1 (Hawala & Financial Layering Syndicate)"
    },
    "Mohammed Rafiq": {
        "aliases": "Rafiq Dubai, Deira Operator, MR-02",
        "role": "Overseas Financial Clearing Coordinator & Hawala Broker",
        "city": "Deira, Dubai, UAE",
        "phone": "+971-501234567",
        "risk_score": 88.0,
        "financial_flag": "4-hop circular funds routing via offshore fiat-to-crypto layering",
        "telecom_detail": "International roaming tunnel · Nocturnal token settlement calls (02:00 - 04:30 AM)",
        "legal_action": "Interpol Blue Corner notice request submitted to CBI & Ministry of Home Affairs.",
        "community": "Cluster 1 (Hawala & Financial Layering Syndicate)"
    },
    "Vikram Singh": {
        "aliases": "Vicky, VS-Cargo, Transporter",
        "role": "Logistics Lead & Transport Fleet Coordinator",
        "city": "Navi Mumbai, Maharashtra",
        "phone": "+91-9845678901",
        "risk_score": 79.4,
        "financial_flag": "Sub-50k structured cash advances for container fleet movement",
        "telecom_detail": "SIM Multiplexing: 3 IMSIs mapped to single handset at Goregaon Tower 4041",
        "legal_action": "Vehicle impound and transit surveillance order active under BNSS Section 107.",
        "community": "Cluster 2 (Maritime Logistics & Cargo Corridors)"
    },
    "Priya Desai": {
        "aliases": "Madam CA, Auditor Priya",
        "role": "Chartered Accountant & Shell Entity Structurer",
        "city": "Surat, Gujarat",
        "phone": "+91-9765432109",
        "risk_score": 74.2,
        "financial_flag": "Fictitious invoice audit shields & trade GST round-tripping",
        "telecom_detail": "Encrypted VoIP messaging sessions matching corporate filing dates",
        "legal_action": "Statutory summons issued under Section 50 Prevention of Money Laundering Act (PMLA).",
        "community": "Cluster 1 (Hawala & Financial Layering Syndicate)"
    },
    "Mehta Enterprises Ltd": {
        "aliases": "MEL-Trade, Front Import-Export",
        "role": "Trade-Based Money Laundering Import-Export Front Company",
        "city": "Nariman Point, Mumbai",
        "phone": "CIN: U51909MH2021PTC368921",
        "risk_score": 70.0,
        "financial_flag": "₹8.75 Cr over-invoiced trade disbursements with zero warehouse inventory",
        "telecom_detail": "Registered switchboard diverted to dynamic burner mobile numbers",
        "legal_action": "Registrar of Companies (RoC) provisional attachment under PMLA Section 5.",
        "community": "Cluster 1 (Hawala & Financial Layering Syndicate)"
    },
    "Phoenix Trading LLC": {
        "aliases": "PT-Dubai, Offshore Shield",
        "role": "Offshore Layering Vehicle & Crypto Swap Intermediary",
        "city": "Business Bay, Dubai, UAE",
        "phone": "Trade Lic: DXB-2024-8849",
        "risk_score": 85.0,
        "financial_flag": "₹12.4 Cr wire transfers followed by immediate USDT swaps within 12 minutes",
        "telecom_detail": "Offshore virtual IP PBX routing to avoid telecommunications logging",
        "legal_action": "Mutual Legal Assistance Treaty (MLAT) request initiated with UAE authorities.",
        "community": "Cluster 1 (Hawala & Financial Layering Syndicate)"
    },
    "Al-Rafiq Trading Co": {
        "aliases": "Al-Rafiq Cash Remittance Hub",
        "role": "Cash Remittance & Hawala Settlement Desk",
        "city": "Deira, Dubai, UAE",
        "phone": "Lic: DXB-HAW-4091",
        "risk_score": 82.5,
        "financial_flag": "Daily cash-token netting matches Mumbai nocturnal phone call spikes",
        "telecom_detail": "Encrypted satellite voice terminal calls mapped to overseas numbers",
        "legal_action": "Financial Intelligence Unit (FIU-IND) Suspicious Transaction Report (STR) active.",
        "community": "Cluster 1 (Hawala & Financial Layering Syndicate)"
    },
    "Desai Financial Consultancy": {
        "aliases": "DFC-Shield, Audit Services",
        "role": "Corporate Filings & Audit Shield Consultancy",
        "city": "Surat, Gujarat",
        "phone": "PAN: AAACD1290F",
        "risk_score": 65.0,
        "financial_flag": "₹3.4 Cr consultancy fees routed from shell companies with zero operational staff",
        "telecom_detail": "Dynamic IP lease switches corresponding to MCA filing deadlines",
        "legal_action": "Statutory inspection warrant issued under Section 206 Companies Act.",
        "community": "Cluster 1 (Hawala & Financial Layering Syndicate)"
    }
}

@router.post("/generate")
async def generate_report_pdf(data: dict, claims: dict = Depends(require_authenticated_user)):
    """Compiles a dynamic, entity-specific forensic PDF report with real graph links, anomaly alerts, and embedded SHA-256 integrity."""
    case_id = data.get("case_id", "c1")
    report_type = str(data.get("template") or data.get("report_type") or "full").lower()
    entity_name_or_id = str(data.get("entity_id") or "Arjun Mehta").strip()
    entity_type = str(data.get("entity_type") or "Person").strip()
    client_details = data.get("details") or {}
    user_name = claims.get("badge") or claims.get("sub") or "Aditya Pawar"
    user_role = claims.get("role") or "LEAD_INVESTIGATOR"

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Fetch Case
        cursor.execute("SELECT id, title, description FROM cases WHERE id = ?", (case_id,))
        case_row = cursor.fetchone()
        case_title = case_row["title"] if case_row else "Operation Blue Thunder"

        # 2. Fetch Evidence
        cursor.execute("SELECT id, source_type, filename, sha256_hash, integrity_status FROM evidence_items WHERE case_id = ?", (case_id,))
        evidence_items = [dict(r) for r in cursor.fetchall()]

        # 3. Query Target Entity from graph_entities or suspects
        cursor.execute("""
            SELECT id, name, type, tier, category, risk_score, city, phone, dossier 
            FROM graph_entities 
            WHERE LOWER(name) = LOWER(?) OR id = ?
        """, (entity_name_or_id, entity_name_or_id))
        entity_row = cursor.fetchone()

        if not entity_row:
            cursor.execute("""
                SELECT id, name, 'Person' as type, 'leadership' as tier, role as category, risk_score, city, phone, dossier 
                FROM suspects 
                WHERE LOWER(name) = LOWER(?) OR id = ?
            """, (entity_name_or_id, entity_name_or_id))
            entity_row = cursor.fetchone()

        if entity_row:
            target_entity = dict(entity_row)
        else:
            target_entity = {
                "id": f"ent-{uuid.uuid4().hex[:6]}",
                "name": entity_name_or_id,
                "type": entity_type,
                "tier": "suspect",
                "category": entity_type,
                "risk_score": 75.0,
                "city": "Mumbai / Under Surveillance",
                "phone": "+91-9876543210",
                "dossier": f"Subject of interest registered in active case {case_id}."
            }

        resolved_name = target_entity["name"]

        # Enrich target entity with canonical dossiers and client-passed intelligence
        canonical = CANONICAL_DOSSIERS.get(resolved_name) or {}
        for k, v in canonical.items():
            if k not in target_entity or not target_entity[k]:
                target_entity[k] = v

        if isinstance(client_details, dict):
            for k, v in client_details.items():
                if v:
                    target_entity[k] = v
            # Map camelCase
            field_mappings = [
                ("financialFlag", "financial_flag"),
                ("telecomDetail", "telecom_detail"),
                ("legalAction", "legal_action"),
                ("riskScore", "risk_score")
            ]
            for ck, tk in field_mappings:
                if client_details.get(ck) and not target_entity.get(tk):
                    target_entity[tk] = client_details[ck]

        # 4. Fetch Direct Relationships for Target
        cursor.execute("""
            SELECT id, source, target, label, type, confidence, weight 
            FROM graph_relationships 
            WHERE LOWER(source) = LOWER(?) OR LOWER(target) = LOWER(?)
        """, (resolved_name, resolved_name))
        direct_links = [dict(r) for r in cursor.fetchall()]

        # 5. Fetch Alerts for Target
        cursor.execute("""
            SELECT id, entity_id, entity_name, anomaly_type, anomaly_score, severity, 
                   algorithm, feature_breakdown_json, plain_english_explanation 
            FROM alerts 
            WHERE LOWER(entity_name) = LOWER(?) OR entity_id = ?
        """, (resolved_name, target_entity.get("id", "")))
        entity_alerts = [dict(r) for r in cursor.fetchall()]

    # 6. Compute Real NetworkX Centrality & Graph Metrics
    G, _, _ = build_network_graph()
    centralities = compute_centralities(G)

    target_pr = 0.05
    target_bc = 0.0
    for inf in centralities.get("influencers", []):
        if inf.get("node", "").lower() == resolved_name.lower():
            target_pr = float(inf.get("pagerank", 0.05))
            target_bc = float(inf.get("betweenness", 0.0))
            break

    target_deg = G.degree(resolved_name) if G.has_node(resolved_name) else len(direct_links)
    density = round(nx.density(G), 4) if len(G) > 0 else 0.048
    avg_deg = round(sum(d for _, d in G.degree()) / max(len(G), 1), 2) if len(G) > 0 else 4.6

    analytics_summary = {
        "density": density,
        "average_degree": avg_deg,
        "communities_count": 2,
        "target_node": resolved_name,
        "target_pagerank": target_pr,
        "target_betweenness": target_bc,
        "target_degree": target_deg,
        "anomalies_count": len(entity_alerts) if entity_alerts else 1
    }

    # 7. Generate PDF
    pdf_bytes = build_pdf_report(
        case_title=case_title,
        case_id=case_id,
        investigator_name=user_name,
        investigator_role=user_role,
        evidence_items=evidence_items,
        analytics_summary=analytics_summary,
        report_type=report_type,
        target_entity=target_entity,
        direct_links=direct_links,
        entity_alerts=entity_alerts
    )

    clean_filename = f"CrimeNet_{report_type.upper()}_{resolved_name.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={clean_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@router.post("/bsa-certificate")
async def generate_bsa_certificate_endpoint(data: dict, claims: dict = Depends(require_authenticated_user)):
    """Generates an official Section 63(4) Bharatiya Sakshya Adhiniyam, 2023 Statutory Certificate PDF."""
    target_id = str(data.get("target_id") or "Arjun Mehta").strip()
    case_id = str(data.get("case_id") or "c1").strip()
    officer_name = str(data.get("officer_name") or claims.get("badge") or "Aditya Pawar").strip()
    officer_designation = str(data.get("officer_designation") or "Lead Cyber Crime Investigator & Forensic Architect").strip()
    badge_number = str(data.get("badge_number") or "CYBER-INV-2026-09").strip()
    agency = str(data.get("agency") or "Special Cyber Crime Investigation Cell (CID / MHA)").strip()
    device_name = str(data.get("device_name") or "CRIMENET-FORENSIC-STATION-01").strip()
    mac_address = str(data.get("mac_address") or "00:1A:2B:3C:4D:5E").strip()

    pdf_bytes = build_bsa_certificate_pdf(
        target_id=target_id,
        case_id=case_id,
        officer_name=officer_name,
        officer_designation=officer_designation,
        badge_number=badge_number,
        agency=agency,
        device_name=device_name,
        mac_address=mac_address
    )

    clean_filename = f"BSA_63_4_Certificate_{target_id.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={clean_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
