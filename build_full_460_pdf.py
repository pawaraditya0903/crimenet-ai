# build_full_460_pdf.py
# Compiles all 460 questions (Q1 to Q460) with 9 embedded high-resolution diagram images into a Master Defense PDF.

import os
import re
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Import all 5 question batches
import questions_batch1 as b1
import questions_batch2 as b2
import questions_batch3 as b3
import questions_batch4 as b4
import questions_batch5 as b5

PDF_OUTPUT_PATH = "CrimeNet_AI_460_Complete_Interview_Defense.pdf"
DIAGRAM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interview_diagrams")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 6.5)
        self.setFillColor(colors.HexColor('#64748B'))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(20, 825, "CRIMENET AI — 460 COMPLETE INTERVIEW DEFENSE MASTER ENCYCLOPEDIA")
            self.drawRightString(575, 825, "BHARATIYA SAKSHYA ADHINIYAM (BSA) 2023 COMPLIANT")
            self.setStrokeColor(colors.HexColor('#CBD5E1'))
            self.setLineWidth(0.5)
            self.line(20, 820, 575, 820)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor('#CBD5E1'))
        self.setLineWidth(0.5)
        self.line(20, 24, 575, 24)

        self.setFont("Helvetica-Bold", 6.5)
        self.setFillColor(colors.HexColor('#0F172A'))
        self.drawString(20, 14, "CONFIDENTIAL — STRICTLY ADVISORY DECISION SUPPORT — HUMAN-IN-THE-LOOP REQUIRED")
        self.drawRightString(575, 14, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def clean_xml(text):
    if not text:
        return ""
    text = str(text)
    # Replace bare &
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;)', '&amp;', text)
    # Replace bare < that is not part of formatting tags
    text = re.sub(r'<(?!/?(b|i|code|font)(\s+[^>]*)?>)', '&lt;', text)
    return text

def build_pdf():
    print("Gathering all 460 questions across all batches...")
    all_questions = (
        b1.BATCH1_QUESTIONS +
        b2.BATCH2_QUESTIONS +
        b3.BATCH3_QUESTIONS +
        b4.BATCH4_QUESTIONS +
        b5.BATCH5_QUESTIONS
    )

    total_q = len(all_questions)
    print(f"Total questions gathered: {total_q}")
    assert total_q == 460, f"Expected 460 questions, but found {total_q}!"

    # Verify sequential numbers
    numbers = [q[0] for q in all_questions]
    assert numbers == list(range(1, 461)), "Question numbers must be strictly consecutive 1 to 460!"
    print("Verification passed: Exactly 460 questions numbered 1 through 460.")

    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=20,
        rightMargin=20,
        topMargin=24,
        bottomMargin=26
    )

    printable_width = 555  # 595 - 40

    styles = getSampleStyleSheet()

    # Typography & Styles
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=17,
        textColor=colors.HexColor('#0F172A'), alignment=1, spaceAfter=2
    )
    sub_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=colors.HexColor('#0284C7'), alignment=1, spaceAfter=4
    )
    sec_h1 = ParagraphStyle(
        'SecH1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.white
    )
    sec_intro = ParagraphStyle(
        'SecIntro', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7.0, leading=9.0,
        textColor=colors.HexColor('#475569')
    )
    q_title = ParagraphStyle(
        'QTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=10.0,
        textColor=colors.HexColor('#0F172A'), spaceAfter=1.5
    )
    body_txt = ParagraphStyle(
        'BText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.0, leading=9.2,
        textColor=colors.HexColor('#1E293B')
    )
    spoken_txt = ParagraphStyle(
        'SText', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7.2, leading=9.6,
        textColor=colors.HexColor('#0F172A')
    )
    table_cell = ParagraphStyle(
        'TCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=6.8, leading=8.5,
        textColor=colors.HexColor('#1E293B')
    )
    table_cell_bold = ParagraphStyle(
        'TCellB', parent=table_cell,
        fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A')
    )
    table_head = ParagraphStyle(
        'THead', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.2, leading=9.0,
        textColor=colors.white
    )

    story = []

    def make_section_header(title_text, intro_text=""):
        p = Paragraph(f"<b>{title_text}</b>", sec_h1)
        t = Table([[p]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        elements = [t]
        if intro_text:
            elements.append(Spacer(1, 1.5))
            elements.append(Paragraph(clean_xml(intro_text), sec_intro))
        return elements

    def make_qa_card(num_str, q_text, spoken_ans, intuition_ans, tech_math="", code_loc="", trap_warning=""):
        flow = []
        flow.append(Paragraph(f"<b>Q{clean_xml(num_str)}: {clean_xml(q_text)}</b>", q_title))
        flow.append(Paragraph(f"<b>Oral Defense:</b> \"{clean_xml(spoken_ans)}\"", spoken_txt))
        flow.append(Spacer(1, 1))
        flow.append(Paragraph(f"<b>Intuitive Concept:</b> {clean_xml(intuition_ans)}", body_txt))
        if tech_math:
            flow.append(Spacer(1, 1))
            flow.append(Paragraph(f"<b>Technical Formulation:</b> <font face='Courier' size='6.2'>{clean_xml(tech_math)}</font>", body_txt))
        if code_loc:
            flow.append(Spacer(1, 1))
            flow.append(Paragraph(f"<b>Code Location:</b> <font color='#0284C7'>{clean_xml(code_loc)}</font>", body_txt))
        if trap_warning:
            flow.append(Spacer(1, 1))
            flow.append(Paragraph(f"<b>Panel Trap Warning:</b> <font color='#DC2626'>{clean_xml(trap_warning)}</font>", body_txt))

        t = Table([[flow]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 2.2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
            ('LEFTPADDING', (0,0), (-1,-1), 4.5),
            ('RIGHTPADDING', (0,0), (-1,-1), 4.5),
        ]))
        return t

    def make_image_diagram(filename, caption, width=500, height=210):
        img_path = os.path.join(DIAGRAM_DIR, filename)
        if os.path.exists(img_path):
            img = Image(img_path, width=width, height=height)
            cap = Paragraph(
                f"<b>Graphical Flowchart / Architecture Diagram:</b> <i>{clean_xml(caption)}</i>",
                ParagraphStyle('Cap', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.0, leading=8.5, textColor=colors.HexColor('#0369A1'), alignment=1)
            )
            t = Table([[img], [cap]], colWidths=[printable_width])
            t.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0,0), (-1,-1), 2.5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ]))
            return t
        else:
            return Paragraph(f"[Diagram Image: {filename}]", body_txt)

    # ══════════════════════════════════════════════════════════════════════
    # HEADER BANNER & EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("CRIMENET AI — COMPLETE 460-QUESTION TECHNICAL INTERVIEW DEFENSE ENCYCLOPEDIA", title_style))
    story.append(Paragraph("Exhaustive Oral Defense, Mathematical Proofs, Code Citations & High-Resolution Graphical Flowcharts", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=1, spaceAfter=3))

    meta_table = Table([
        [Paragraph("<b>Author / Lead:</b> Aditya Pawar", body_txt),
         Paragraph("<b>Benchmark:</b> NCFB-2026 (10,000 Rows)", body_txt),
         Paragraph("<b>Precision:</b> 96.7% (464/480)", body_txt)],
        [Paragraph("<b>Architecture:</b> React + FastAPI + SQLite", body_txt),
         Paragraph("<b>Validation:</b> 5-Fold CV (0.2% Gap)", body_txt),
         Paragraph("<b>Legal:</b> Section 63 BSA 2023", body_txt)],
        [Paragraph("<b>Tests:</b> 17/17 Passing Pytests", body_txt),
         Paragraph("<b>Latency:</b> P99 ≤ 420ms", body_txt),
         Paragraph("<b>Deployment:</b> Vercel + Render", body_txt)]
    ], colWidths=[printable_width/3.0]*3)
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 4))

    # SECTION DEFINITIONS & FLOWCHART PLACEMENT
    # Map section boundaries and corresponding diagram
    sections = [
        (1, 50, "SECTION 1: CORE PROJECT, PROBLEM STATEMENT & ARCHITECTURE",
         "Foundational overview of CrimeNet AI, criminal syndicate intelligence, technology stack choices, and 5-tier architecture.",
         "architecture_flowchart.png", "System Architecture: 5-Tier Forensic Stack & Request-Response Flow"),

        (51, 80, "SECTION 2: INGESTION & FORENSIC DATA PIPELINE",
         "Multi-sensor ingestion protocols, CDR cleaning, banking ledger ETL, and cryptographic SHA-256 hash sealing.",
         "forensic_data_pipeline.png", "End-to-End Forensic Data Pipeline: Ingestion, ETL, Graph Crunching, ML & Merkle Sealing"),

        (81, 130, "SECTION 3: GRAPH THEORY, PAGERANK & CENTRALITY ANALYSIS",
         "NetworkX topological algorithms, PageRank power iterations, Betweenness bridging centralities, and criminal hierarchy discovery.",
         "pagerank_vs_betweenness.png", "Graph Centrality Duality: Exposing the Kingpin (PageRank) vs Broker (Betweenness)"),

        (131, 170, "SECTION 4: MACHINE LEARNING & ISOLATION FOREST PIPELINE",
         "Scikit-Learn LiveIsolationForestPipeline, 200 isolation trees, path length average anomaly scoring, and c(n) normalization.",
         "isolation_forest_tree.png", "Isolation Forest Architecture: Path Length Duality for Anomaly Isolation"),

        (171, 200, "SECTION 5: STATISTICAL DISTANCES, MAHALANOBIS & MULTIMODAL FEATURES",
         "Multidimensional feature engineering, 5 forensic dimensions, covariance inversion, and Mahalanobis distance geometry.",
         "mahalanobis_ellipse.png", "Mahalanobis Distance Geometry: Feature Correlation & Chi-Square Ellipses"),

        (201, 235, "SECTION 6: EVALUATION METRICS, CONFUSION MATRIX & 5-FOLD CROSS-VALIDATION",
         "NCFB-2026 synthetic benchmark, 5-fold stratified cross-validation, 96.7% precision/recall derivation, and 0.2% generalization gap.",
         None, None),

        (236, 255, "SECTION 7: CELLULAR TRILATERATION, HATA PATH LOSS & GDOP MATHEMATICS",
         "Cell tower RSSI path loss modeling, Weighted Least Squares (WLS) coordinate estimation, and Geometric Dilution of Precision (GDOP).",
         "telecom_trilateration_gdop.png", "Cellular Trilateration: 3-Tower WLS Intersection & GDOP 1.14 Covariance Bound"),

        (256, 275, "SECTION 8: FINANCIAL HAWALA FORENSICS & BENFORD'S LAW CHI-SQUARE",
         "Statistical forensic accounting, Benford logarithmic first-digit distributions, and Chi-Square goodness-of-fit hypothesis testing.",
         "benford_law_distribution.png", "Benford's Law Chi-Square Test: Detecting Manipulated Hawala Accounts"),

        (276, 295, "SECTION 9: CRYPTOGRAPHY, MERKLE TREES & SECTION 63 BSA LAW",
         "SHA-256 binary Merkle trees, chain-of-custody verification, electronic record admissibility, and Section 63 BSA compliance.",
         "merkle_tree_ledger.png", "SHA-256 Binary Merkle Tree: Chain of Custody & Tamper Detection"),

        (296, 315, "SECTION 10: RESPONSIBLE AI, HUMAN-IN-THE-LOOP & ADVISORY ALERTS",
         "Ethical AI principles, strictly advisory alerts, officer sign-off verification, demographic bias elimination, and audit logs.",
         "hitl_alert_lifecycle.png", "Responsible AI Framework: Human-in-the-Loop Advisory Review Lifecycle"),

        (316, 345, "SECTION 11: DATABASE ARCHITECTURE, SQLITE WAL & FASTAPI BACKEND",
         "Database schema design, Write-Ahead Logging (WAL) concurrency, Pydantic v2 schemas, REST endpoints, and security middleware.",
         None, None),

        (346, 370, "SECTION 12: FRONTEND ARCHITECTURE, REACT 19, CYTOSCAPE CANVAS & MAPBOX",
         "Single Page Application architecture, Cytoscape.js HTML5 canvas rendering, fcose physics layout, Mapbox GL WebGL vector tiles.",
         None, None),

        (371, 395, "SECTION 13: AUTOMATED TESTING & 17/17 PYTEST VERIFICATION SUITE",
         "Test suite engineering, pytest fixtures, in-memory SQLite isolation, tamper tests, collinear fallbacks, and 100% test pass rate.",
         None, None),

        (396, 420, "SECTION 14: PERFORMANCE ENGINEERING, 420ms LATENCY & SCALING ROADMAP",
         "P99 latency budget breakdown, sparse matrix accelerations, in-memory caching, and scaling roadmap to 100 million records.",
         None, None),

        (421, 440, "SECTION 15: 'SHOW ME THE CODE' LINE-BY-LINE DEFENSE & IMPLEMENTATION WALKTHROUGH",
         "Direct line-by-line verification of backend algorithms, mathematical helpers, endpoints, scripts, and frontend components.",
         None, None),

        (441, 460, "SECTION 16: HOSTILE PANEL DEFENSE, EDGE CASES & CHAMPIONSHIP PITCH",
         "Decisive oral answers to difficult panel traps, deep learning trade-offs, adversarial poisoning defenses, and winning pitch.",
         None, None),
    ]

    # Index all questions by question number for rapid access
    q_dict = {q[0]: q for q in all_questions}

    for start_q, end_q, sec_title, sec_desc, diagram_img, diagram_cap in sections:
        story.extend(make_section_header(sec_title, sec_desc))
        story.append(Spacer(1, 2))

        # Insert diagram at the top of the section if defined
        if diagram_img:
            story.append(make_image_diagram(diagram_img, diagram_cap, width=500, height=205))
            story.append(Spacer(1, 3))

        # Add questions in this range
        for q_num in range(start_q, end_q + 1):
            if q_num in q_dict:
                num, q_text, sp, int_a, math, code, trap = q_dict[q_num]
                story.append(make_qa_card(str(num), q_text, sp, int_a, math, code, trap))
                story.append(Spacer(1, 1.5))

        story.append(Spacer(1, 4))

    # ══════════════════════════════════════════════════════════════════════
    # FINAL RECAP TABLE: 10 COMMANDMENTS
    # ══════════════════════════════════════════════════════════════════════
    story.extend(make_section_header("FINAL SUMMARY: THE 10 COMMANDMENTS FOR INTERVIEW DAY",
                                     "Essential mathematical formulas, baseline benchmarks, and golden oral defense rules."))
    story.append(Spacer(1, 2))

    recap_final = [
        [Paragraph("#", table_head), Paragraph("Concept", table_head), Paragraph("Formula / Metric", table_head), Paragraph("Oral Defense Summary", table_head)],
        [Paragraph("1", table_cell_bold), Paragraph("Benchmark Dataset", table_cell), Paragraph("10,000 rows, 480 anomalies (4.8%)", table_cell), Paragraph("\"Evaluated on our synthetic NCFB-2026 benchmark stored in backend/data/.\"", table_cell)],
        [Paragraph("2", table_cell_bold), Paragraph("Precision & Recall", table_cell), Paragraph("Prec: 96.7%, Rec: 96.7%, F1: 0.967", table_cell), Paragraph("\"464 TP, 16 FP, 16 FN, 9504 TN from 5-Fold Stratified CV on our 10k benchmark.\"", table_cell)],
        [Paragraph("3", table_cell_bold), Paragraph("Generalization Gap", table_cell), Paragraph("0.2% (|Train 96.8% - Val 96.6%|)", table_cell), Paragraph("\"A 0.2% generalization gap safely beats the 3.0% industry threshold.\"", table_cell)],
        [Paragraph("4", table_cell_bold), Paragraph("Isolation Forest", table_cell), Paragraph("200 trees, contamination=0.048", table_cell), Paragraph("\"Runs Scikit-Learn IsolationForest in LiveIsolationForestPipeline in ~220ms.\"", table_cell)],
        [Paragraph("5", table_cell_bold), Paragraph("Mahalanobis Distance", table_cell), Paragraph("D_M = sqrt((x-mu)^T * pinv(Cov) * (x-mu))", table_cell), Paragraph("\"Inverts covariance using Moore-Penrose pseudoinverse np.linalg.pinv().\"", table_cell)],
        [Paragraph("6", table_cell_bold), Paragraph("PageRank vs Betweenness", table_cell), Paragraph("PageRank: PR(u); Betweenness: g(v)", table_cell), Paragraph("\"PageRank exposes the kingpin boss; Betweenness exposes the broker courier.\"", table_cell)],
        [Paragraph("7", table_cell_bold), Paragraph("Cellular Accuracy", table_cell), Paragraph("±12.4m = GDOP(1.14) * 10.8m", table_cell), Paragraph("\"A theoretical simulated covariance bound, NOT a field drive-test result.\"", table_cell)],
        [Paragraph("8", table_cell_bold), Paragraph("Benford's Law", table_cell), Paragraph("Chi-Square = 41.22 vs 15.51 (df=8)", table_cell), Paragraph("\"Proves statistical accounting manipulation with 99.1% confidence, not legal guilt.\"", table_cell)],
        [Paragraph("9", table_cell_bold), Paragraph("Section 63 BSA Law", table_cell), Paragraph("SHA-256 Binary Merkle Root", table_cell), Paragraph("\"Establishes post-ingestion technical integrity; court determines search legality.\"", table_cell)],
        [Paragraph("10", table_cell_bold), Paragraph("Responsible AI", table_cell), Paragraph("HITL advisory review + audit log", table_cell), Paragraph("\"Strictly advisory alerts requiring signed badge review; zero autonomous action.\"", table_cell)]
    ]
    t_recap_f = Table(recap_final, colWidths=[printable_width*0.05, printable_width*0.25, printable_width*0.32, printable_width*0.38])
    t_recap_f.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_recap_f)
    story.append(Spacer(1, 4))

    concl_p = Paragraph(
        "<b>🎓 FINAL CANDIDATE CHECKLIST:</b> "
        "• To inspect the ML model: open <code>backend/app/main.py</code> line 2100. "
        "• To run the benchmark: execute <code>python backend/scripts/run_offline_benchmark.py</code>. "
        "• To run the test suite: execute <code>python -m pytest backend/tests/test_responsible_ai.py -v</code> (17/17 pass). "
        "• Live web application: <font color='#0284C7'>https://crimenet-ai-two.vercel.app</font>. "
        "• Defend with pride: you built an end-to-end, mathematically grounded, legally compliant system!",
        body_txt
    )
    t_c = Table([[concl_p]], colWidths=[printable_width])
    t_c.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#10B981')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_c)

    print(f"Building PDF document with {len(story)} flowable elements...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"COMPLETE 460-QUESTION DEFENSE PDF SUCCESSFULLY GENERATED AT: {PDF_OUTPUT_PATH}")

if __name__ == '__main__':
    build_pdf()
