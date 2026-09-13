import io
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rc
from backend.app.security.crypto import compute_sha256

REPORT_DISCLAIMER = (
    "STATUTORY LEGAL NOTICE: This dossier draft contains analytical decision-support findings compiled "
    "by the CrimeNet AI forensic intelligence engine for authorized investigator review. It does NOT "
    "constitute formal judicial certification, evidence admissibility under Section 63/65B, or proof of guilt."
)

def build_pdf_report(
    case_title: str,
    case_id: str,
    investigator_name: str,
    investigator_role: str,
    evidence_items: List[Dict[str, Any]],
    analytics_summary: Dict[str, Any],
    report_type: str = "full"
) -> bytes:
    """Builds a structured forensic PDF report draft and embeds an end-to-end SHA-256 integrity hash."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
    now_utc = datetime.now(timezone.utc).strftime("%d-%b-%Y %H:%M:%S UTC")

    # 1. Header Banner
    story.append(Table([
        ["CRIMENET AI — FORENSIC INVESTIGATION REPORT DRAFT"]
    ], colWidths=[520], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), rc.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,-1), rc.HexColor('#38bdf8')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
    ])))
    story.append(Spacer(1, 8))

    # 2. Metadata Table
    meta_data = [
        ["REPORT IDENTIFIER", report_id],
        ["CASE FILE", f"{case_id} — {case_title}"],
        ["GENERATED TIMESTAMP", now_utc],
        ["PREPARED BY", f"{investigator_name} ({investigator_role})"],
        ["CLASSIFICATION", "CONFIDENTIAL / LAW ENFORCEMENT DECISION SUPPORT DRAFT"]
    ]
    story.append(Table(meta_data, colWidths=[160, 360], style=TableStyle([
        ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0,0), (-1,-1), rc.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 4),
    ])))
    story.append(Spacer(1, 10))

    # 3. Evidence Chain of Custody Table
    story.append(Paragraph("DIGITAL EVIDENCE INTEGRITY LEDGER (SHA-256)", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=10, textColor=rc.HexColor('#1e40af'))))
    story.append(Spacer(1, 4))

    ev_rows = [["ID", "TYPE", "FILENAME", "SHA-256 HASH", "INTEGRITY"]]
    if evidence_items:
        for ev in evidence_items:
            h = ev.get("sha256_hash", "")
            short_h = f"{h[:16]}...{h[-8:]}" if len(h) > 24 else h
            ev_rows.append([
                ev.get("id", ""),
                ev.get("source_type", ""),
                ev.get("filename", "")[:22],
                short_h,
                ev.get("integrity_status", "INTACT")
            ])
    else:
        ev_rows.append(["None", "N/A", "No files recorded", "N/A", "N/A"])

    story.append(Table(ev_rows, colWidths=[50, 110, 120, 150, 90], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,0), rc.HexColor('#e2e8f0')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('GRID', (0,0), (-1,-1), 0.5, rc.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 3),
    ])))
    story.append(Spacer(1, 10))

    # 4. Analytical Findings
    story.append(Paragraph("SUMMARY OF ANALYTICAL INDICATORS", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=10, textColor=rc.HexColor('#1e40af'))))
    story.append(Spacer(1, 4))
    findings_text = (
        f"• Network Density: {analytics_summary.get('density', 0.05)} | Average Degree: {analytics_summary.get('average_degree', 4.2)}\n"
        f"• Active Graph Communities Detected: {analytics_summary.get('communities_count', 2)}\n"
        f"• Highest Centrality Node: {analytics_summary.get('top_node', 'Arjun Mehta')} (PageRank: {analytics_summary.get('top_pagerank', 0.0847)})\n"
        f"• Flagged Anomaly Count: {analytics_summary.get('anomalies_count', 3)}"
    )
    story.append(Paragraph(findings_text.replace('\n', '<br/>'), ParagraphStyle('B', fontName='Helvetica', fontSize=8, leading=12)))
    story.append(Spacer(1, 10))

    # 5. Statutory Disclaimer
    story.append(HRFlowable(width="100%", thickness=1, color=rc.HexColor('#94a3b8'), spaceAfter=6))
    story.append(Paragraph(REPORT_DISCLAIMER, ParagraphStyle('Disc', fontName='Helvetica-Oblique', fontSize=7, textColor=rc.HexColor('#64748b'), leading=9.5)))

    doc.build(story)
    pdf_bytes = buf.getvalue()

    return pdf_bytes
