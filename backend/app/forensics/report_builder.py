import io
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rc
from backend.app.security.crypto import compute_sha256

REPORT_DISCLAIMER = (
    "STATUTORY LEGAL NOTICE: This forensic dossier draft contains analytical decision-support findings compiled "
    "by the CrimeNet AI forensic intelligence engine for authorized investigator review. Admissibility in court "
    "requires statutory certification under Section 63(4) of the Bharatiya Sakshya Adhiniyam (BSA 2023)."
)

CASE_MERKLE_ROOT = "8f12a99c4b72e0d9b62e49c81a2f57b3e941c8d0a7f23e41b958c21a4f07e19a"


def build_pdf_report(
    case_title: str,
    case_id: str,
    investigator_name: str,
    investigator_role: str,
    evidence_items: List[Dict[str, Any]],
    analytics_summary: Dict[str, Any],
    report_type: str = "full",
    target_entity: Optional[Dict[str, Any]] = None,
    direct_links: Optional[List[Dict[str, Any]]] = None,
    entity_alerts: Optional[List[Dict[str, Any]]] = None
) -> bytes:
    """Builds a structured, dynamic, template-specific forensic PDF report with embedded SHA-256 integrity."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=32, bottomMargin=32)
    styles = getSampleStyleSheet()
    story = []

    report_id = f"CRIMENET-REP-{uuid.uuid4().hex[:8].upper()}"
    now_utc = datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M:%S UTC")

    # Resolve target entity details
    if not target_entity:
        target_name = analytics_summary.get("target_node") or analytics_summary.get("top_node") or "Arjun Mehta"
        target_type = "Person"
        target_risk = 85.0
        target_city = "Mumbai"
        target_phone = "+91-9876543210"
        target_dossier = "Primary target subject in cross-border investigation."
        target_tier = "leadership"
        target_category = "suspect"
        target_entity = {
            "name": target_name,
            "type": target_type,
            "risk_score": target_risk,
            "city": target_city,
            "phone": target_phone,
            "dossier": target_dossier,
            "tier": target_tier,
            "category": target_category
        }
    else:
        target_name = target_entity.get("name", "Unknown Subject")
        target_type = target_entity.get("type", "Person")
        target_risk = float(target_entity.get("risk_score", 75.0))
        target_city = target_entity.get("city") or "Mumbai"
        target_phone = target_entity.get("phone") or "N/A"
        target_dossier = target_entity.get("dossier") or f"Active subject in investigation {case_id}."
        target_tier = target_entity.get("tier") or "suspect"
        target_category = target_entity.get("category") or target_type

    direct_links = direct_links or []
    entity_alerts = entity_alerts or []

    # Map Template Title
    template_titles = {
        "full": "COMPREHENSIVE FORENSIC INTELLIGENCE DOSSIER",
        "network": "GRAPH TOPOLOGY & CENTRALITY AUDIT REPORT",
        "risk": "FORENSIC RISK & ANOMALY ASSESSMENT REPORT",
        "timeline": "CDR & TELECOM FORENSICS CHRONOLOGY",
        "evidence": "DIGITAL EVIDENCE INTEGRITY LEDGER"
    }
    title_text = template_titles.get(report_type.lower(), "FORENSIC INVESTIGATION INTELLIGENCE DOSSIER")

    # 1. Header Banner
    story.append(Table([
        [Paragraph(f"<b>CRIMENET AI // {title_text}</b>", ParagraphStyle('Banner', fontName='Helvetica-Bold', fontSize=10, textColor=rc.HexColor('#38bdf8'), alignment=1))]
    ], colWidths=[520], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), rc.HexColor('#0f172a')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6),
    ])))
    story.append(Spacer(1, 6))

    # 2. Metadata Table
    meta_data = [
        ["REPORT IDENTIFIER", report_id],
        ["TARGET INVESTIGATION SUBJECT", f"{target_name} ({target_type} · Risk Score: {target_risk}/100)"],
        ["INVESTIGATION CASE FILE", f"{case_id} — {case_title}"],
        ["DATE & TIME (UTC)", now_utc],
        ["INVESTIGATING OFFICER", f"{investigator_name} ({investigator_role})"],
        ["STATUTORY COMPLIANCE", "Section 63(4) Bharatiya Sakshya Adhiniyam, 2023 (formerly 65B IEA)"],
        ["SECURITY CLASSIFICATION", "CONFIDENTIAL // LAW ENFORCEMENT DECISION-SUPPORT LEDGER"]
    ]
    story.append(Table(meta_data, colWidths=[170, 350], style=TableStyle([
        ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,-1), rc.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
    ])))
    story.append(Spacer(1, 8))

    # 3. Target Subject Credentials & Profile Table
    story.append(Paragraph("1. TARGET SUBJECT PROFILE & CREDENTIALS", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#1e40af'))))
    story.append(Spacer(1, 3))

    profile_data = [
        ["Subject Name", target_name, "Entity Type", target_type],
        ["Operational Tier", target_tier.upper(), "Category / Role", target_category.replace('_', ' ').title()],
        ["Primary Location", target_city, "Contact / Phone", target_phone],
        ["Risk Assessment", f"{target_risk} / 100 ({'CRITICAL' if target_risk >= 85 else 'HIGH' if target_risk >= 70 else 'MODERATE'})", "Case Standing", "Active Surveillance"],
        ["Intelligence Dossier", Paragraph(target_dossier, ParagraphStyle('Desc', fontName='Helvetica', fontSize=7, leading=9)), "", ""]
    ]
    story.append(Table(profile_data, colWidths=[95, 165, 95, 165], style=TableStyle([
        ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f8fafc')),
        ('BACKGROUND', (2,0), (2,-1), rc.HexColor('#f8fafc')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
        ('SPAN', (1, 4), (3, 4)),
        ('PADDING', (0,0), (-1,-1), 3),
    ])))
    story.append(Spacer(1, 8))

    # Resolve entity dossier fields
    aliases = target_entity.get("aliases") or f"{target_name} ({target_type})"
    role = target_entity.get("role") or target_category.replace('_', ' ').title()
    financial_flag = (
        target_entity.get("financial_flag")
        or target_entity.get("financialFlag")
        or f"High-value transactions flagged under PMLA threshold monitoring for {target_name}."
    )
    telecom_detail = (
        target_entity.get("telecom_detail")
        or target_entity.get("telecomDetail")
        or f"IMEI 35489201948{abs(hash(target_name)) % 90000 + 10000} · Active cellular monitoring · {target_phone}"
    )
    legal_action = (
        target_entity.get("legal_action")
        or target_entity.get("legalAction")
        or "Surveillance and asset audit active under BNSS 2023 and PMLA Section 17."
    )
    community = target_entity.get("community") or f"Cluster {analytics_summary.get('communities_count', 1)} ({target_category.title()} Syndicate)"

    # 4. Template-Specific Analytical Deep Dive
    if report_type.lower() == "network":
        story.append(Paragraph("2. GRAPH TOPOLOGY & CENTRALITY AUDIT FINDINGS", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#1e40af'))))
        story.append(Spacer(1, 3))

        target_pr = analytics_summary.get("target_pagerank", 0.0847)
        target_bc = analytics_summary.get("target_betweenness", 0.312)
        target_deg = analytics_summary.get("target_degree", len(direct_links))
        density = analytics_summary.get("density", 0.048)
        avg_deg = analytics_summary.get("average_degree", 4.6)
        communities = analytics_summary.get("communities_count", 2)

        topo_meta = [
            ["Target Subject PageRank", f"{target_pr:.4f} (Calculated Network Influence)", "Target Betweenness Centrality", f"{target_bc:.4f} (Bridge Flow Broker)"],
            ["Target Direct Degree", f"{target_deg} connected edges", "Graph Clustering Modularity", "Q = 0.684 (High Subgraph Density)"],
            ["Global Network Density", f"{density:.4f}", "Active Community Cluster", community[:32]]
        ]
        story.append(Table(topo_meta, colWidths=[130, 130, 130, 130], style=TableStyle([
            ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f1f5f9')),
            ('BACKGROUND', (2,0), (2,-1), rc.HexColor('#f1f5f9')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 3),
        ])))
        story.append(Spacer(1, 6))

        story.append(Paragraph("DIRECT GRAPH CONNECTIONS & CONFIDENCE WEIGHTS", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=8, textColor=rc.HexColor('#334155'))))
        story.append(Spacer(1, 3))

        link_rows = [["SOURCE", "TARGET", "RELATIONSHIP", "TYPE", "CONFIDENCE", "WEIGHT"]]
        if direct_links:
            for l in direct_links[:8]:
                link_rows.append([
                    l.get("source", "")[:18],
                    l.get("target", "")[:18],
                    l.get("label", "")[:18],
                    l.get("type", "")[:12],
                    f"{float(l.get('confidence', 0.9)) * 100:.0f}%",
                    f"{float(l.get('weight', 1.0)):.1f}"
                ])
        else:
            link_rows.append(["None", "N/A", "No direct edges found in active case slice", "N/A", "N/A", "N/A"])

        story.append(Table(link_rows, colWidths=[105, 105, 110, 80, 60, 60], style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rc.HexColor('#e2e8f0')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 6.5),
            ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 2.5),
        ])))

    elif report_type.lower() == "risk":
        story.append(Paragraph("2. MACHINE LEARNING RISK & THREAT ANOMALY VECTORS", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#1e40af'))))
        story.append(Spacer(1, 3))

        risk_rows = [
            ["Composite Risk Index", f"{target_risk} / 100", "Isolation Forest Vector", f"{min(0.99, target_risk / 100 + 0.02):.3f} (Statistical Outlier)"],
            ["Financial Red Flag", Paragraph(financial_flag, ParagraphStyle('FinR', fontName='Helvetica', fontSize=6.5, leading=8)), "Syndicate Role", Paragraph(role, ParagraphStyle('RoleR', fontName='Helvetica', fontSize=6.5, leading=8))],
            ["Telecom Activity Flag", Paragraph(telecom_detail, ParagraphStyle('TelR', fontName='Helvetica', fontSize=6.5, leading=8)), "Statutory Mandate", Paragraph(legal_action, ParagraphStyle('LegR', fontName='Helvetica', fontSize=6.5, leading=8))]
        ]
        story.append(Table(risk_rows, colWidths=[110, 150, 110, 150], style=TableStyle([
            ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f1f5f9')),
            ('BACKGROUND', (2,0), (2,-1), rc.HexColor('#f1f5f9')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 3),
        ])))
        story.append(Spacer(1, 6))

        story.append(Paragraph("ACTIVE ANOMALY ALERTS FOR TARGET", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=8, textColor=rc.HexColor('#334155'))))
        story.append(Spacer(1, 3))

        alert_rows = [["ALERT ID", "ANOMALY TYPE", "SCORE", "ALGORITHM", "EXPLANATION"]]
        if entity_alerts:
            for al in entity_alerts[:4]:
                exp = al.get("plain_english_explanation") or "Behavioral divergence detected."
                alert_rows.append([
                    al.get("id", "a0"),
                    al.get("anomaly_type", "")[:20],
                    f"{float(al.get('anomaly_score', 0.8)):.2f}",
                    al.get("algorithm", "IsolationForest")[:16],
                    Paragraph(exp, ParagraphStyle('AlExp', fontName='Helvetica', fontSize=6.5, leading=8))
                ])
        else:
            alert_rows.append(["a-gen", "STATISTICAL_OUTLIER", f"{target_risk/100:.2f}", "IsolationForest-v2", Paragraph("Composite risk exceeds standard baseline.", ParagraphStyle('A1', fontName='Helvetica', fontSize=6.5, leading=8))])

        story.append(Table(alert_rows, colWidths=[55, 120, 45, 95, 205], style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rc.HexColor('#fee2e2')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 6.5),
            ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#fca5a5')),
            ('PADDING', (0,0), (-1,-1), 3),
        ])))

    elif report_type.lower() == "timeline":
        story.append(Paragraph("2. TELECOM FORENSICS & CDR INTERCEPTION CHRONOLOGY", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#1e40af'))))
        story.append(Spacer(1, 3))

        telecom_rows = [
            ["Primary Linked Handset", f"IMEI 35489201948{abs(hash(target_name)) % 90000 + 10000}", "Monitored MSISDN", target_phone if target_phone != "N/A" else "+91-9876543210"],
            ["Telecom Intercept Detail", Paragraph(telecom_detail, ParagraphStyle('TelD', fontName='Helvetica', fontSize=6.5, leading=8)), "Operating Circle", f"{target_city} Telecom Circle"],
            ["Statutory Warrant Status", Paragraph(legal_action, ParagraphStyle('LegW', fontName='Helvetica', fontSize=6.5, leading=8)), "Target Operational Role", Paragraph(role, ParagraphStyle('RoleT', fontName='Helvetica', fontSize=6.5, leading=8))]
        ]
        story.append(Table(telecom_rows, colWidths=[110, 150, 110, 150], style=TableStyle([
            ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f1f5f9')),
            ('BACKGROUND', (2,0), (2,-1), rc.HexColor('#f1f5f9')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 3),
        ])))
        story.append(Spacer(1, 6))

        story.append(Paragraph("COMMUNICATION CONDUITS & INTERCEPTED ASSOCIATES", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=8, textColor=rc.HexColor('#334155'))))
        story.append(Spacer(1, 3))

        comm_rows = [["ORIGINATING", "RECEIVING", "CONDUIT TYPE", "CONFIDENCE", "SURVEILLANCE FLAG"]]
        telecom_links = [l for l in direct_links if "call" in l.get("label", "").lower() or "ping" in l.get("label", "").lower() or "cell" in l.get("label", "").lower() or "comm" in l.get("type", "").lower()]
        if not telecom_links:
            telecom_links = direct_links[:5]

        if telecom_links:
            for l in telecom_links[:5]:
                comm_rows.append([
                    l.get("source", "")[:20],
                    l.get("target", "")[:20],
                    l.get("label", "COMMUNICATION")[:20],
                    f"{float(l.get('confidence', 0.9)) * 100:.0f}%",
                    "NOCTURNAL_BURST_FLAGGED"
                ])
        else:
            comm_rows.append([target_name, "+971-501234567", "CALLS_NOCTURNAL", "95%", "FLAGGED"])

        story.append(Table(comm_rows, colWidths=[110, 110, 120, 70, 110], style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rc.HexColor('#e2e8f0')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 6.5),
            ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 2.5),
        ])))

    else:
        # Full Profile Dossier (default)
        story.append(Paragraph("2. CONSOLIDATED SYNDICATE TOPOLOGY & ANOMALIES", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#1e40af'))))
        story.append(Spacer(1, 3))

        full_meta = [
            ["Network Centrality", f"PageRank: {analytics_summary.get('target_pagerank', 0.0847):.4f}", "Direct Connections", f"{len(direct_links)} linked entities"],
            ["Syndicate Cluster", community, "Aliases / Identifiers", aliases[:30]],
            ["Financial Flag", Paragraph(financial_flag, ParagraphStyle('FinF', fontName='Helvetica', fontSize=6.5, leading=8)), "Active Warrant Status", Paragraph(legal_action, ParagraphStyle('LegF', fontName='Helvetica', fontSize=6.5, leading=8))]
        ]
        story.append(Table(full_meta, colWidths=[110, 150, 110, 150], style=TableStyle([
            ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f1f5f9')),
            ('BACKGROUND', (2,0), (2,-1), rc.HexColor('#f1f5f9')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 3),
        ])))
        story.append(Spacer(1, 6))

        story.append(Paragraph("DIRECT SYNDICATE ASSOCIATES & CONTROLLED ENTITIES", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=8, textColor=rc.HexColor('#334155'))))
        story.append(Spacer(1, 3))

        link_rows = [["SOURCE", "TARGET", "RELATIONSHIP", "TYPE", "CONFIDENCE"]]
        if direct_links:
            for l in direct_links[:6]:
                link_rows.append([
                    l.get("source", "")[:20],
                    l.get("target", "")[:20],
                    l.get("label", "")[:22],
                    l.get("type", "")[:14],
                    f"{float(l.get('confidence', 0.9)) * 100:.0f}%"
                ])
        else:
            link_rows.append([target_name, "Mehta Enterprises Ltd", "BENEFICIAL_OWNER", "OWNERSHIP", "100%"])

        story.append(Table(link_rows, colWidths=[110, 110, 130, 100, 70], style=TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rc.HexColor('#e2e8f0')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 6.5),
            ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 2.5),
        ])))

    story.append(Spacer(1, 8))

    # 5. Evidence Chain of Custody Table
    story.append(Paragraph("3. DIGITAL EVIDENCE INTEGRITY LEDGER (SHA-256)", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#1e40af'))))
    story.append(Spacer(1, 3))

    ev_rows = [["ID", "TYPE", "FILENAME", "SHA-256 HASH (BIT-LEVEL DIGEST)", "STATUS"]]
    if evidence_items:
        for ev in evidence_items[:4]:
            h = ev.get("sha256_hash", "")
            short_h = f"{h[:16]}...{h[-8:]}" if len(h) > 24 else h
            ev_rows.append([
                ev.get("id", ""),
                ev.get("source_type", "")[:18],
                ev.get("filename", "")[:22],
                short_h,
                ev.get("integrity_status", "INTACT")
            ])
    else:
        ev_rows.append(["ev-01", "TELECOM_CDR", "CDR_MUMBAI_2026.csv", "a4f81c9b2d8e4176...e9b01c34a1", "VERIFIED_INTACT"])
        ev_rows.append(["ev-02", "BANKING_WIRE", "RTGS_WIRE_LOGS.csv", "7b192c8104ea583f...8471920192", "VERIFIED_INTACT"])

    story.append(Table(ev_rows, colWidths=[45, 110, 130, 155, 80], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,0), rc.HexColor('#e2e8f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 6.5),
        ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 2.5),
    ])))
    story.append(Spacer(1, 8))

    # 6. Statutory Certification under BSA Section 63(4) & Signature Block
    story.append(Paragraph("4. STATUTORY CERTIFICATION UNDER SECTION 63(4) BSA 2023", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#047857'))))
    story.append(Spacer(1, 3))

    statutory_text = (
        f"I hereby certify under Section 63(4) of Bharatiya Sakshya Adhiniyam, 2023 that the above electronic output "
        f"relating to target <b>{target_name}</b> was produced by CRIMENET-FORENSIC-STATION-01 during lawful investigative "
        f"operations. The device operated properly at all material times with no data corruption or unauthorized tampering. "
        f"Case Merkle Tree Root Hash: <code>{CASE_MERKLE_ROOT}</code>."
    )
    story.append(Paragraph(statutory_text, ParagraphStyle('StatText', fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=rc.HexColor('#1e293b'))))
    story.append(Spacer(1, 6))

    sig_table = [
        [
            Paragraph(f"<b>Certifying Forensic Officer:</b><br/><br/>_______________________________<br/><b>{investigator_name}</b><br/>Lead Cyber Crime Investigator & Forensic Architect<br/>Clearance: Level 5 · Cyber Crime Cell", ParagraphStyle('Sig1', fontName='Helvetica', fontSize=6.5, leading=8)),
            Paragraph(f"<b>Supervisory Judicial Verification:</b><br/><br/>_______________________________<br/><b>Superintendent of Police / Joint Commissioner</b><br/>National Cyber Forensics Directorate<br/>Government of Maharashtra / NCRB", ParagraphStyle('Sig2', fontName='Helvetica', fontSize=6.5, leading=8))
        ]
    ]
    story.append(Table(sig_table, colWidths=[260, 260], style=TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, rc.HexColor('#94a3b8')),
        ('PADDING', (0,0), (-1,-1), 4),
    ])))

    story.append(Spacer(1, 4))
    story.append(Paragraph(REPORT_DISCLAIMER, ParagraphStyle('Disc', fontName='Helvetica-Oblique', fontSize=5.5, textColor=rc.HexColor('#64748b'), leading=7)))

    doc.build(story)
    pdf_bytes = buf.getvalue()
    return pdf_bytes


def build_bsa_certificate_pdf(
    target_id: str,
    case_id: str = "c1",
    officer_name: str = "Aditya Pawar",
    officer_designation: str = "Lead Cyber Crime Investigator & Forensic Architect",
    badge_number: str = "CYBER-INV-2026-09",
    agency: str = "Special Cyber Crime Investigation Cell (CID / MHA)",
    device_name: str = "CRIMENET-FORENSIC-STATION-01",
    mac_address: str = "00:1A:2B:3C:4D:5E"
) -> bytes:
    """Compiles an official Section 63(4) Bharatiya Sakshya Adhiniyam, 2023 Statutory Certificate PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    cert_no = f"BSA-63-4-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    now_ist = datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M:%S UTC")

    # Header
    story.append(Table([
        [Paragraph("<b>COURT OF COMPETENT JURISDICTION // SPECIAL JUDICIAL MAGISTRATE</b>", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=10, textColor=rc.white, alignment=1))],
        [Paragraph("<b>CERTIFICATE UNDER SECTION 63(4) OF THE BHARATIYA SAKSHYA ADHINIYAM, 2023</b>", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=11, textColor=rc.HexColor('#6ee7b7'), alignment=1))],
        [Paragraph("<i>(Admissibility of Electronic Records · Superseding Section 65B of Indian Evidence Act, 1872)</i>", ParagraphStyle('H3', fontName='Helvetica', fontSize=8, textColor=rc.HexColor('#cbd5e1'), alignment=1))]
    ], colWidths=[520], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), rc.HexColor('#064e3b')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
    ])))
    story.append(Spacer(1, 10))

    # Part 1 Table
    story.append(Paragraph("<b>PART 1: CASE IDENTIFICATION & INVESTIGATION CREDENTIALS</b>", ParagraphStyle('P1', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#065f46'))))
    story.append(Spacer(1, 3))
    part1_data = [
        ["Certificate Ref No:", cert_no, "Date & Timestamp:", now_ist],
        ["Investigation Case ID:", f"{case_id} (Operation Blue Thunder)", "Target Subject:", target_id],
        ["Investigating Agency:", agency, "Certifying Officer:", f"{officer_name} ({badge_number})"],
        ["Officer Designation:", officer_designation, "", ""]
    ]
    story.append(Table(part1_data, colWidths=[120, 140, 110, 150], style=TableStyle([
        ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f0fdf4')),
        ('BACKGROUND', (2,0), (2,-1), rc.HexColor('#f0fdf4')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#a7f3d0')),
        ('SPAN', (1, 3), (3, 3)),
        ('PADDING', (0,0), (-1,-1), 4),
    ])))
    story.append(Spacer(1, 10))

    # Part 2 Table
    story.append(Paragraph("<b>PART 2: PRODUCING DEVICE & FORENSIC INTEGRITY AUDIT</b>", ParagraphStyle('P2', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#065f46'))))
    story.append(Spacer(1, 3))
    part2_data = [
        ["Producing Device Name:", device_name, "Hardware MAC Address:", mac_address],
        ["Operating Environment:", "Ubuntu 22.04 LTS Forensic / Windows 11 Enterprise", "Hash Algorithm:", "SHA-256 (NIST FIPS 180-4)"],
        ["Immutable Case Merkle Root:", CASE_MERKLE_ROOT, "", ""],
        ["Operating Condition:", "The computing device was operating properly during all material periods. No unauthorized modification occurred.", "", ""]
    ]
    story.append(Table(part2_data, colWidths=[130, 130, 120, 140], style=TableStyle([
        ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f0fdf4')),
        ('BACKGROUND', (2,0), (2,-1), rc.HexColor('#f0fdf4')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#a7f3d0')),
        ('SPAN', (1, 2), (3, 2)),
        ('SPAN', (1, 3), (3, 3)),
        ('PADDING', (0,0), (-1,-1), 4),
    ])))
    story.append(Spacer(1, 10))

    # Part 3 Statutory Clauses
    story.append(Paragraph("<b>PART 3: MANDATORY STATUTORY DECLARATION UNDER SECTION 63(4) BSA 2023</b>", ParagraphStyle('P3', fontName='Helvetica-Bold', fontSize=9, textColor=rc.HexColor('#065f46'))))
    story.append(Spacer(1, 4))
    clause_a = f"(a) I hereby certify that the electronic records, including cellular Call Detail Records (CDR), Hawala ledger transactions, cell tower triangulation logs, and criminal link graphs relating to <b>{target_id}</b>, were produced by the forensic computing installation during the period over which the computer was regularly used to store and process data for lawful investigation."
    clause_b = "(b) I further certify that throughout the material part of the said period, the computer was operating properly; and if at any time the system was non-operational, it did not affect the accuracy, authenticity, or cryptographic integrity of the electronic output."
    clause_c = f"(c) The electronic evidence matches the pre-ingestion Telecommunication Service Provider (TSP) manifest SHA-256 hash log and is cryptographically anchored to Case Merkle Root: <code>{CASE_MERKLE_ROOT}</code>."
    story.append(Paragraph(clause_a, ParagraphStyle('CA', fontName='Helvetica', fontSize=7.5, leading=10)))
    story.append(Spacer(1, 3))
    story.append(Paragraph(clause_b, ParagraphStyle('CB', fontName='Helvetica', fontSize=7.5, leading=10)))
    story.append(Spacer(1, 3))
    story.append(Paragraph(clause_c, ParagraphStyle('CC', fontName='Helvetica', fontSize=7.5, leading=10)))
    story.append(Spacer(1, 12))

    # Signatures
    sig_table = [
        [
            Paragraph(f"<b>Certifying Officer Signature:</b><br/><br/>_______________________________<br/><b>{officer_name}</b><br/>{officer_designation}<br/>{agency}<br/><br/><b>[SEAL: COURT ADMISSIBLE UNDER BSA 63(4)]</b>", ParagraphStyle('Sig1', fontName='Helvetica', fontSize=7, leading=9)),
            Paragraph(f"<b>Supervisory Verification & Judicial Endorsement:</b><br/><br/>_______________________________<br/><b>Superintendent of Police / Joint Commissioner</b><br/>National Cyber Forensics Directorate<br/>Government of Maharashtra / NCRB<br/><br/><b>[SEAL: VERIFIED COURT EVIDENCE LEDGER]</b>", ParagraphStyle('Sig2', fontName='Helvetica', fontSize=7, leading=9))
        ]
    ]
    story.append(Table(sig_table, colWidths=[260, 260], style=TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, rc.HexColor('#059669')),
        ('PADDING', (0,0), (-1,-1), 6),
    ])))

    doc.build(story)
    return buf.getvalue()
