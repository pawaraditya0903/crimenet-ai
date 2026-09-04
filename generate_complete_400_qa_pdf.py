import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = os.path.normpath(r"c:\Users\Aditya\Downloads\SIH 2026\CrimeNet_AI_Complete_Interview_QnA.pdf")

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
            self.draw_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        if self._pageNumber > 1:
            self.drawString(36, A4[1] - 28, "CRIMENET AI — COMPLETE 400+ INTERVIEW QUESTION DEFENSE ENCYCLOPEDIA")
            self.drawRightString(A4[0] - 36, A4[1] - 28, "TECHNICAL PANEL & VIVA MANUAL")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, A4[1] - 32, A4[0] - 36, A4[1] - 32)
            
        self.setFont("Helvetica", 8)
        self.drawString(36, 22, "CrimeNet AI Interview Encyclopedia • Simple English & Mathematical Precision")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(A4[0] - 36, 22, page_str)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 32, A4[0] - 36, 32)
        
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=34,
        rightMargin=34,
        topMargin=40,
        bottomMargin=40
    )
    printable_width = A4[0] - 68

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'MainTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#0F172A'), spaceAfter=2
    )
    sub_style = ParagraphStyle(
        'MainSub', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=13, textColor=colors.HexColor('#0284C7'), spaceAfter=8
    )
    sec_h1 = ParagraphStyle(
        'SecH1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.white, spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    q_title = ParagraphStyle(
        'QTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.8, leading=12, textColor=colors.HexColor('#0369A1'), spaceBefore=5, spaceAfter=2, keepWithNext=True
    )
    body_txt = ParagraphStyle(
        'BText', parent=styles['Normal'], fontName='Helvetica', fontSize=7.8, leading=11, textColor=colors.HexColor('#1E293B'), spaceAfter=2
    )
    spoken_txt = ParagraphStyle(
        'SText', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.8, leading=11, textColor=colors.HexColor('#0F172A')
    )
    code_txt = ParagraphStyle(
        'CText', parent=styles['Normal'], fontName='Courier', fontSize=7.0, leading=9.0, textColor=colors.HexColor('#0F172A')
    )
    table_cell = ParagraphStyle(
        'TCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.2, leading=9.2, textColor=colors.HexColor('#1E293B')
    )
    table_cell_bold = ParagraphStyle(
        'TCellB', parent=table_cell, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A')
    )
    table_head = ParagraphStyle(
        'THead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.white
    )

    story = []

    def make_section_header(title_text):
        p = Paragraph(f"<b>{title_text}</b>", sec_h1)
        t = Table([[p]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    def make_qa_card(q_num_text, spoken_ans, intuition_ans, tech_math="", code_loc="", trap_warning=""):
        flow = []
        flow.append(Paragraph(f"<b>{q_num_text}</b>", q_title))
        flow.append(Paragraph(f"<b>🗣️ Spoken Answer (Simple English):</b><br/>\"{spoken_ans}\"", spoken_txt))
        flow.append(Spacer(1, 2))
        flow.append(Paragraph(f"<b>💡 Simple Intuition (Why this makes sense):</b> {intuition_ans}", body_txt))
        if tech_math:
            flow.append(Spacer(1, 1.5))
            flow.append(Paragraph(f"<b>🔬 Technical / Mathematical Proof:</b> <font face='Courier' size='6.8'>{tech_math}</font>", body_txt))
        if code_loc:
            flow.append(Spacer(1, 1.5))
            flow.append(Paragraph(f"<b>📂 Code Reference:</b> <font color='#0284C7'>{code_loc}</font>", body_txt))
        if trap_warning:
            flow.append(Spacer(1, 1.5))
            flow.append(Paragraph(f"<b>⚠️ Trap Warning:</b> <font color='#DC2626'>{trap_warning}</font>", body_txt))

        t = Table([[flow]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    def make_diagram_card(diagram_ascii, caption):
        p_diag = Paragraph(diagram_ascii.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_txt)
        p_cap = Paragraph(f"<b>Whiteboard Sketch:</b> <i>{caption}</i>", ParagraphStyle('Cap', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#0369A1'), spaceBefore=2))
        t = Table([[ [p_diag, p_cap] ]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    def make_recap_box(must_mem, traps, codes, wb_sketch, rapid_ans):
        rows = [
            [Paragraph("Category", table_head), Paragraph("Summary & Defense Directives", table_head)],
            [Paragraph("<b>3 Must Memorize</b>", table_cell_bold), Paragraph("<br/>".join([f"• {m}" for m in must_mem]), table_cell)],
            [Paragraph("<b>3 Trap Checks</b>", table_cell_bold), Paragraph("<br/>".join([f"⚠️ {t}" for t in traps]), table_cell)],
            [Paragraph("<b>3 Code Targets</b>", table_cell_bold), Paragraph("<br/>".join([f"🔍 {c}" for c in codes]), table_cell)],
            [Paragraph("<b>Whiteboard Plan</b>", table_cell_bold), Paragraph(wb_sketch, table_cell)],
            [Paragraph("<b>1-Sentence Rapid</b>", table_cell_bold), Paragraph(f"<i>\"{rapid_ans}\"</i>", table_cell)]
        ]
        t = Table(rows, colWidths=[printable_width*0.25, printable_width*0.75])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        return t

    # ══════════════════════════════════════════════════════════════════════
    # HEADER / COVER
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("CRIMENET AI — COMPLETE 400+ INTERVIEW QUESTION DEFENSE ENCYCLOPEDIA", title_style))
    story.append(Paragraph("Question-by-Question Simple English Answers, Mathematical Proofs, Whiteboard Flowcharts & Code References", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=1, spaceAfter=5))

    meta_table = Table([
        [
            Paragraph("<b>Candidate:</b> Aditya Pawar", table_cell),
            Paragraph("<b>Role:</b> Full-Stack & AI/ML Engineer", table_cell),
            Paragraph("<b>Stack:</b> React 19, FastAPI, NetworkX, SQLite", table_cell)
        ],
        [
            Paragraph("<b>Live Demo:</b> <font color='#0284C7'>crimenet-ai-two.vercel.app</font>", table_cell),
            Paragraph("<b>Benchmark:</b> NCFB-2026 (10,000 synthetic rows)", table_cell),
            Paragraph("<b>Offline Precision:</b> 96.7% (5-Fold Stratified CV)", table_cell)
        ]
    ], colWidths=[printable_width*0.35, printable_width*0.35, printable_width*0.3])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 5))

    # Ground Rules Callout
    rule_p = Paragraph(
        "<b>⚠️ ABSOLUTE INTERVIEW PANEL DEFENSE DIRECTIVES:</b><br/>"
        "1. <b>Never claim synthetic data is real police data:</b> Real telecom intercepts and bank logs are strictly protected under Section 5(2) Indian Telegraph Act and DPDP Act 2023.<br/>"
        "2. <b>Never claim 96.7% precision is guaranteed in production:</b> 96.7% is the measured precision on our synthetic NCFB-2026 benchmark under 5-Fold Stratified Cross-Validation.<br/>"
        "3. <b>Isolation Forest is unsupervised during training:</b> Model receives ZERO labels during .fit(X). Labels are held out as an evaluation test oracle.<br/>"
        "4. <b>±12.4m is a theoretical geometric covariance uncertainty radius:</b> Derived from Hata path loss and GDOP 1.14, NOT an empirical field drive-test measurement.<br/>"
        "5. <b>Merkle trees prove post-ingestion technical integrity:</b> Lawful seizure and admissibility require valid court warrants.<br/>"
        "6. <b>Zero autonomous enforcement:</b> AI outputs are advisory alerts requiring human badge signoff; the system never arrests or freezes accounts autonomously.",
        body_txt
    )
    t_rule = Table([[rule_p]], colWidths=[printable_width])
    t_rule.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#EF4444')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_rule)
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 1: PROJECT & PROBLEM STATEMENT
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 1 — PROJECT & PROBLEM STATEMENT"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What is CrimeNet AI and what problem does it solve?",
        "CrimeNet AI is an investigative decision-support platform that unifies four disconnected data silos—telecom Call Detail Records, hawala banking ledgers, highway toll cameras, and dark-web intercepts—into an interactive 48-node knowledge graph. It solves the massive problem of investigative data silos where officers spend months manually cross-referencing spreadsheets to uncover syndicate kingpins and laundering loops.",
        "Think of a jigsaw puzzle where police have 10 pieces, banks have 10 pieces, and toll cameras have 10 pieces. CrimeNet AI puts all 30 pieces on one table and connects them using graph theory and anomaly detection.",
        "Relational SQL databases degrade polynomially (O(N^k)) when performing 5+ table JOINs across millions of rows to trace proxy links. CrimeNet uses adjacency graph pointers for constant-time neighbor traversal.",
        "backend/app/main.py: startup_event() & knowledge graph builder",
        "Never say it replaces police officers; it is an advisory decision-support system."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. Why did you build this project and what is the main objective?",
        "I built CrimeNet AI to eliminate investigative blind spots in complex financial fraud and organized narcotics syndicates. The main objective is to accelerate syndicate link analysis from months to seconds by automating multi-sensor data fusion, kingpin centrality scoring, circular money-trail detection, and court-compliant cryptographic evidence logging.",
        "Criminals deliberately spread their actions across different channels (calling on one SIM, paying through another bank, traveling on highways). CrimeNet joins those dots automatically.",
        "Objectives: (1) Graph fusion across multi-sensor streams; (2) Unsupervised anomaly detection via Isolation Forest + Mahalanobis distance; (3) SHA-256 Merkle tree evidence locking compliant with Section 63 BSA 2023.",
        "backend/app/main.py",
        "Do not claim the objective is 'autonomous crime prevention'; it is 'investigative decision support'."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. Who are the target users and what makes CrimeNet AI different from existing systems?",
        "The target users are cybercrime investigators, economic offense wings, intelligence analysts, and forensic auditors. Unlike legacy police databases (e.g. CCTNS) which are static SQL search forms where you search by one name at a time, CrimeNet AI is graph-native and multi-modal, discovering hidden multi-hop proxy connections and mathematical anomalies automatically.",
        "Traditional police software is like a phonebook where you must already know the name you want to look up. CrimeNet AI is like a social network map that highlights the hidden boss who never makes direct phone calls.",
        "Differentiators: (1) Integrated 4-sensor multi-modal graph; (2) Unsupervised ML + Mahalanobis scoring; (3) Real-time radio trilateration; (4) Cryptographic Merkle tree audit trails.",
        "src/App.tsx, backend/app/main.py",
        "Never insult existing police systems; acknowledge that CCTNS is a case-management system while CrimeNet is an analytical link-analysis engine."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. Is this a real production police system, and does it use real police data?",
        "No. CrimeNet AI is a high-fidelity prototype and research benchmark platform. It does NOT use real citizen police data. Under Section 5(2) of the Indian Telegraph Act, the Digital Personal Data Protection (DPDP) Act 2023, and commercial banking secrecy statutes, releasing actual citizen CDRs or bank account records in an open repository is strictly illegal. We evaluated on our synthetic National Cyber Forensic Benchmark (NCFB-2026).",
        "Privacy laws strictly prohibit publishing real phone calls and bank transactions on GitHub. We used mathematically calibrated synthetic data that mimics real criminal patterns.",
        "Data distributions: Log-normal financial transactions (mu=9.2, sigma=1.8), Power-law telecom degree distributions (gamma=2.4), Poisson vehicle toll arrivals (lambda=4.2).",
        "backend/data/ncfb_2026_benchmark_10k.csv",
        "CRITICAL TRAP: Never bluff that you have secret access to police databases. Panels will immediately disqualify you."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q5. Explain the project in 30 seconds, 1 minute, and WITHOUT using the word 'AI'.",
        "30-Sec: In organized crime, kingpins hide behind layers of burner SIMs and mule accounts. CrimeNet AI fuses multi-sensor logs into an interactive knowledge graph, using PageRank, tuned Isolation Forest with 96.7% precision on our 10k benchmark, and 3-tower radio trilateration to expose syndicate bosses and circular Hawala loops in seconds, locking evidence with SHA-256 Merkle trees.<br/>1-Min: Add the decoupled React 19/FastAPI stack, Explainable AI baselines, and Human-in-the-Loop review.<br/>Without 'AI': CrimeNet is a forensic data fusion platform. It converts tabular logs into a mathematical relational network, applies graph matrix algorithms (PageRank, Betweenness) to uncover hubs, uses statistical tree partitioning and Mahalanobis distance to isolate statistical outliers, and solves non-linear radio path-loss equations across cell towers.",
        "Without AI, it is pure discrete mathematics, linear algebra, graph theory, and cryptographic hashing.",
        "Graph theory + Tree-based statistical partitioning + Covariance matrix inversion + Cryptographic hashing.",
        "backend/app/main.py",
        "Keep the elevator pitch crisp and confident."
    ))
    story.append(Spacer(1, 3))

    diag_arch = (
        "+-----------------------------------------------------------------------------+\n"
        "|                         CLIENT APPLICATION HUD (React 19)                   |\n"
        "|  Cytoscape.js Link Graph  |  Mapbox ANPR Radar  |  Alert Centre HITL Review  |\n"
        "+--------------------------------------+--------------------------------------+\n"
        "                                       | HTTPS REST + WebSocket Telemetry\n"
        "                                       v\n"
        "+-----------------------------------------------------------------------------+\n"
        "|                           FASTAPI BACKEND SERVICES                          |\n"
        "|  Auth/RBAC (PBKDF2)  |  Graph Math (NetworkX)  |  Live Isolation Forest ML  |\n"
        "|  Radio Trilateration |  Kalman Kinematics     |  Merkle Tree Ledger (BSA)  |\n"
        "+--------------------------------------+--------------------------------------+\n"
        "                                       | SQL CRUD + Encrypted Logs\n"
        "                                       v\n"
        "+-----------------------------------------------------------------------------+\n"
        "|                      PERSISTENCE & SECURITY STORAGE                         |\n"
        "|  SQLite (crimenet.db) | .env Secret Vault | master_security.json (PBKDF2)   |\n"
        "+-----------------------------------------------------------------------------+"
    )
    story.append(make_diagram_card(diag_arch, "CrimeNet AI 5-Tier Decoupled Production Architecture"))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "CrimeNet AI fuses 4 silos (CDR, banking, toll cameras, dark web) into a 48-node knowledge graph.",
            "It is an investigative decision-support prototype evaluated on synthetic NCFB-2026 data.",
            "Real police data cannot be distributed due to Section 5(2) Telegraph Act & DPDP Act 2023."
        ],
        traps=[
            "Did you test on real criminals? -> No, tested on synthetic NCFB-2026 forensic benchmark.",
            "Can AI arrest someone? -> No, strictly advisory alerts; zero autonomous enforcement.",
            "Biggest limitation? -> Requires structured sensor feeds; cannot ingest handwritten paper diaries."
        ],
        codes=[
            "backend/app/main.py: startup_event() & graph setup",
            "backend/data/ncfb_2026_benchmark_10k.csv: 10k rows",
            "src/App.tsx: React 19 HUD routing"
        ],
        wb_sketch="Draw: Multi-Sensor Ingestion -> In-Memory Knowledge Graph -> Advisory Alert HUD (HITL).",
        rapid_ans="CrimeNet AI connects multi-sensor investigative silos into an interactive graph to uncover syndicate leaders and Hawala loops in seconds."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 2: SYSTEM ARCHITECTURE & TECH STACK
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 2 — SYSTEM ARCHITECTURE & TECHNOLOGY SELECTION"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. Explain your complete system architecture and request-response cycle.",
        "CrimeNet AI uses a decoupled 5-tier architecture. The frontend is built with React 19, TypeScript, and Cytoscape.js, communicating via HTTPS REST with a high-throughput FastAPI backend in Python 3.14. When a user requests graph analysis, the request hits FastAPI with a Bearer JWT. FastAPI validates the token and 4-tier RBAC permissions, queries in-memory NetworkX and Scikit-Learn pipelines, and pulls or persists evidence records in SQLite3, returning JSON payloads in under 420ms (P99).",
        "Frontend is the steering wheel and dashboard; FastAPI is the engine; NetworkX and Isolation Forest are the turbochargers; SQLite is the lockbox in the trunk.",
        "ASGI async event loop -> JWT bearer auth middleware -> NetworkX in-memory graph -> Scikit-Learn inference -> SQLite commit -> JSON response.",
        "backend/app/main.py, src/api.ts",
        "Do not say frontend queries the SQLite database directly; all access goes through FastAPI REST APIs."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. Why React, TypeScript, and Vite?",
        "React 19 was selected for its component-based architecture and reactive virtual DOM, allowing high-frequency telemetry updates without full page re-renders. TypeScript provides strict compile-time type safety across 48 node interfaces, eliminating runtime 'undefined is not a function' errors in the field. Vite 8 replaces slow Webpack bundling with native ES modules, achieving 417ms production build rollups and instant Hot Module Replacement during development.",
        "TypeScript is a spellchecker for code that stops errors before running. Vite is a super-fast build engine that turns development waiting into instant feedback.",
        "Vite leverages esbuild (written in Go) for pre-bundling dependencies 10-100x faster than JavaScript-based bundlers.",
        "package.json, tsconfig.json, vite.config.ts",
        "Do not confuse TypeScript with a runtime language; it compiles down to standard JavaScript."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. Why FastAPI, Python, SQLite, and NetworkX?",
        "FastAPI delivers high-performance async I/O via Starlette and Pydantic validation, while providing direct native access to Python's scientific ecosystem (NumPy, Scikit-Learn, NetworkX). Python is the uncontested standard for data science and graph analytics. SQLite3 provides zero-configuration embedded ACID storage with zero network latency on standalone forensic laptops. NetworkX was chosen because it provides mathematically deterministic, peer-reviewed implementations of PageRank, Betweenness Centrality, and Johnson's cycles in memory.",
        "FastAPI is like an express highway for data; Python gives access to every scientific math library; SQLite is a file database that requires zero installation; NetworkX runs graph math in RAM.",
        "FastAPI runs on Uvicorn ASGI; NetworkX stores graph adjacency as nested Python dictionaries: dict-of-dicts-of-dicts for O(1) neighbor lookups.",
        "backend/app/main.py, backend/requirements.txt",
        "Do not say SQLite is for web-scale 100M users; explain it was chosen for zero-config forensic laptop appliances."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. Why Cytoscape.js, Mapbox GL, and Recharts?",
        "Cytoscape.js is a specialized, hardware-accelerated HTML5 canvas graph engine built for large-scale relational link analysis, supporting physics-based force-directed layouts (fcose) without browser lag. Mapbox GL uses WebGL to render vector tiles and geospatial coordinates with GPU hardware acceleration, essential for plotting ANPR toll camera radars and cellular tower radiuses. Recharts provides declarative, responsive SVG charting for forensic velocity and Benford distributions.",
        "Cytoscape handles the social network map; Mapbox handles the geographical police map; Recharts handles the financial charts.",
        "Cytoscape renders nodes on HTML5 Canvas rather than individual DOM SVG elements, avoiding memory exhaustion when rendering hundreds of edges.",
        "src/components/NetworkGraph.tsx, src/components/MapRadar.tsx",
        "Avoid using D3 for complex graphs; D3 requires re-implementing node dragging and physics from scratch."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q5. How would you scale this architecture to handle 50 million records?",
        "To scale to 50 million records: (1) Replace embedded SQLite with PostgreSQL or TimescaleDB using range-based partitioning on timestamp columns; (2) Migrate the in-memory NetworkX graph to a distributed graph cluster like Neo4j or Amazon Neptune; (3) Ingest streaming telecommunications data via Apache Kafka; and (4) Decouple the ML inference engine into an asynchronous Celery/Redis worker cluster with horizontal autoscaling.",
        "An in-memory graph works great for a local syndicate case in RAM. For national-level billions of calls, you must partition the data across cloud database clusters and message queues.",
        "Scale roadmap: SQLite -> PostgreSQL (pg_partman) -> Neo4j Enterprise (Cypher cluster) -> Kafka streams -> Celery/Triton inference.",
        "backend/app/main.py",
        "Do not claim you need Kubernetes and Hadoop for an MVP; explain the exact migration stages."
    ))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "FastAPI provides native async loop and direct interoperability with NumPy/NetworkX/Scikit-Learn.",
            "Cytoscape.js uses hardware-accelerated HTML5 Canvas for physics-based force-directed graph layouts.",
            "SQLite provides zero-config embedded storage for forensic field laptops."
        ],
        traps=[
            "Why not microservices? -> Overkill for a local forensic prototype; introduces latency and complexity.",
            "What happens if backend crashes? -> React frontend catches Axios errors and displays offline banner.",
            "Why not PostgreSQL today? -> SQLite requires zero database server setup for offline law-enforcement laptops."
        ],
        codes=[
            "backend/app/main.py: FastAPI setup & CORS",
            "src/components/NetworkGraph.tsx: Cytoscape fcose layout",
            "package.json: React 19, Cytoscape, Mapbox GL dependencies"
        ],
        wb_sketch="Draw: Client (React HUD) -> FastAPI REST (ASGI) -> In-Memory Graph (NetworkX) + SQLite File.",
        rapid_ans="We paired a hardware-accelerated React 19 canvas HUD with an asynchronous FastAPI engine for sub-second forensic graph analytics."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 3: KNOWLEDGE GRAPH THEORY & GRAPH ALGORITHMS
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 3 — KNOWLEDGE GRAPH THEORY & GRAPH ALGORITHMS"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What is a knowledge graph and why is it better than relational tables for investigations?",
        "A knowledge graph is a mathematical network of entities (nodes) connected by meaningful relationships (edges). In relational SQL, tracing a 5-hop indirect proxy chain (e.g. Suspect A -> Phone B -> Mule C -> Account D -> Kingpin E) requires 5 to 7 expensive JOIN operations across massive tables, resulting in exponential query degradation. In a graph, relationships are first-class citizens stored as direct adjacency pointers, enabling constant-time pointer chasing and O(V + E) traversals regardless of total database size.",
        "In SQL, finding connections requires searching the entire library every time. In a graph, each book has a string physically tied to related books—you just follow the string.",
        "SQL: O(N^k) joins where N is table row count and k is hops. Graph: O(deg(v)^k) where deg(v) is average node degree, independent of total database size.",
        "backend/app/main.py: lines 300-350",
        "Do not say graphs replace SQL for everything; SQL is still better for aggregate payroll or basic CRUD."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. What node types and edge types exist in CrimeNet AI?",
        "CrimeNet AI models 6 distinct node types: Person (Suspects/Kingpins), Account (Bank/Hawala accounts), Phone (IMEI/IMSI/MSISDN), Vehicle (Cars/Couriers), Location (Cell towers/Toll plazas), and Event (Meetings/Seizures). Edges represent directed interactions: TRANSACTED_WITH, CALLED, ASSOCIATED_WITH, CO_LOCATED, and TRAVELLED_TO. Edges are weighted by interaction frequency, call duration, and transaction amounts.",
        "Nodes are the nouns (people, phones, bank accounts, cars); edges are the verbs (called, transferred, traveled, met).",
        "Multi-modal heterogeneous directed graph G = (V, E, W, Phi, Psi) where Phi maps vertices to types and Psi maps edges to relation types.",
        "backend/app/main.py: lines 310-340",
        "Make sure to mention that edges are directed (A paying B is not the same as B paying A)."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. What is a 5-hop traversal and how do you find indirect relationships?",
        "A hop is a single step across an edge from one node to an adjacent neighbor. A 5-hop traversal traverses a path of length 5 (e.g., A -> B -> C -> D -> E -> F). Criminal kingpins intentionally maintain 3 to 5 hops of operational separation from contraband or money couriers using layers of cut-outs. We find indirect relationships using Breadth-First Search (BFS) bounded at 5 hops, identifying intermediary proxy entities that bridge separate syndicates.",
        "Like the 'Six Degrees of Kevin Bacon' game: you might not know the President directly, but you know someone who knows someone who knows the President.",
        "BFS traversal time complexity: O(V + E). Path reconstruction traces predecessor pointers from target back to source.",
        "backend/app/main.py: lines 450-510",
        "Warning: Unbounded graph traversal causes combinatorial explosion. Always bound traversals to max hops (k <= 5)."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. What is a directed vs weighted graph, and how do you calculate edge weights?",
        "A directed graph means edges have a specific orientation (direction): Phone A calling Phone B is an outbound edge from A to B. A weighted graph assigns a numerical weight to each edge representing relationship intensity. In CrimeNet, we compute composite edge weights: W(u,v) = w1 * norm(Call_Count) + w2 * norm(Total_Duration) + w3 * norm(Transaction_Amount). Higher weights denote stronger operational links.",
        "A directed graph is a one-way street; an undirected graph is a two-way street. A weighted graph tells you how much traffic flows down that street.",
        "W(u, v) = alpha * (Freq / Freq_max) + beta * (Volume / Volume_max) where alpha + beta = 1.",
        "backend/app/main.py: lines 320-340",
        "Remember: In Dijkstra, high edge weight usually means high cost/distance. If your weight represents strength, you must invert it (1 / weight) for shortest-path queries!"
    ))
    story.append(Spacer(1, 3))

    diag_graph = (
        "      [Operative A] ---> (Call) ---> [Lieutenant 1] ---\n"
        "                                                        \\---> (Direct Order) ---> [KINGPIN MEHTA]\n"
        "      [Operative B] ---> (Call) ---> [Lieutenant 2] ---/                          (High PageRank)\n"
        "                                            |\n"
        "                                        (Transfer)\n"
        "                                            v\n"
        "      [Domestic Account] <---------------- [HAWALA BROKER RAFIQ] <---------------- [Offshore Shell]\n"
        "                                       (High Betweenness Bridge)\n"
        "             |                                                                             ^\n"
        "             \\-------------------> (Sub-50k Smurfing Cycle) -------------------------------/"
    )
    story.append(make_diagram_card(diag_graph, "Syndicate Graph Topology: Kingpin Authority vs Hawala Bridges"))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "Knowledge graphs store relationships as direct pointers, eliminating expensive multi-table SQL JOINs.",
            "CrimeNet uses 6 node types (Person, Account, Phone, Vehicle, Location, Event) and 5 edge relations.",
            "Traversals are bounded at 5 hops to trace cut-outs while preventing combinatorial explosion."
        ],
        traps=[
            "Why not represent everything in SQL? -> 5-hop relational JOINs degrade exponentially ($O(N^k)$).",
            "How do you handle duplicate entities? -> Entity resolution merges phone numbers/PANs to canonical IDs.",
            "How does graph size affect RAM? -> 48 nodes take <1 MB; at 10M nodes, you must use disk-backed graph engines."
        ],
        codes=[
            "backend/app/main.py: Graph construction & edge weighting",
            "backend/app/main.py: nx.shortest_path() traversal",
            "src/components/NetworkGraph.tsx: Cytoscape visual mapping"
        ],
        wb_sketch="Draw: Suspect -> Phone -> Mule -> Escrow -> Kingpin across 5 directed hops.",
        rapid_ans="We model multi-sensor criminal data as a directed weighted knowledge graph to trace 5-hop proxy chains in constant time."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 4: PAGERANK & CENTRALITY MATHEMATICS
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 4 — PAGERANK & CENTRALITY MATHEMATICS"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What is PageRank, how does it work, and what is the formula?",
        "PageRank is a link-analysis algorithm that measures the structural importance of a node based on the quality and quantity of incoming links. It models a random surfer who follows links with probability d (damping factor) and jumps to a random node with probability (1 - d). The formula is: PR(u) = (1 - d)/N + d * sum_{v in B_u} (PR(v) / L(v)), where B_u is the set of nodes linking to u and L(v) is the out-degree of v. We solve it via Power Iteration until convergence (|PR_{k+1} - PR_k| < 1e-6).",
        "It is like a voting system where a vote from someone influential carries far more weight than a vote from someone nobody knows.",
        "PR(u) = (1 - d)/N + d * sum_{v in B_u} (PR(v) / L(v)), with d = 0.85. Solved as the principal eigenvector of the Google stochastic transition matrix.",
        "backend/app/main.py: nx.pagerank(G, alpha=0.85, tol=1e-6)",
        "Do not claim high PageRank proves someone is a criminal; it proves structural authority in the network."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. Why did you use damping factor d=0.85, and why does PageRank expose kingpins?",
        "The damping factor d=0.85 represents an 85% probability of following graph edges and a 15% probability of a random jump, guaranteed by the Perron-Frobenius theorem to ensure the stochastic matrix is primitive, irreducible, and converges to a unique stationary distribution. In syndicates, kingpins practice strict operational security: they never contact low-level street runners. They only communicate with a few lieutenants. Because those lieutenants have high incoming connectivity, their endorsements funnel massive authority into the kingpin, driving his PageRank to the top (0.081).",
        "The boss only talks to 2 generals, but each general talks to 100 soldiers. When the generals vote for the boss, all that combined influence concentrates at the top.",
        "Kingpin Arjun Mehta has a low raw degree (3 links) but achieves the highest PageRank (0.081) because his in-links originate from top-tier lieutenant nodes.",
        "backend/app/main.py: lines 340-380",
        "Damping factor 0.85 is the established scientific benchmark; using 1.0 creates spider-traps and dead ends."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. What is Betweenness Centrality, what is its formula, and how is it calculated (Brandes' Algorithm)?",
        "Betweenness Centrality measures how frequently a node acts as a bridge along the shortest path between all pairs of other nodes: g(v) = sum_{s != v != t} (sigma_{st}(v) / sigma_{st}), where sigma_{st} is total shortest paths from s to t and sigma_{st}(v) is those passing through v. We compute it using Brandes' Algorithm, which reduces time complexity from O(V^3) to O(V * E) by accumulating pair dependencies through a backward recursive pass from BFS/Dijkstra trees.",
        "Imagine two towns separated by a river with only one bridge. Even if the bridge is narrow, all commerce must pass over it. Betweenness identifies that bridge.",
        "g(v) = sum_{s != v != t} (sigma_{st}(v) / sigma_{st}). Brandes computes delta_{s*}(v) = sum_{w: v in Pred(s,w)} (sigma_{sv} / sigma_{sw}) * (1 + delta_{s*}(w)).",
        "backend/app/main.py: nx.betweenness_centrality(G)",
        "Remember: PageRank finds the Kingpin (the boss); Betweenness finds the Broker (the courier or money launderer)."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. PageRank vs Betweenness Centrality vs Degree Centrality: When do you use which?",
        "Degree Centrality counts direct connections (in-degree + out-degree) / (N - 1), identifying noisy operatives like call-center spammers or active field couriers. PageRank measures authoritative hierarchy, identifying the insulated syndicate boss. Betweenness Centrality measures structural bottlenecking, identifying the financial broker (e.g. Hawala dealer Mohammed Rafiq) who connects two otherwise isolated criminal cliques. Removing a high-betweenness node shatters syndicate communication.",
        "Degree = Most popular person. PageRank = Most respected boss. Betweenness = Key gatekeeper or messenger between rival gangs.",
        "In our graph: Kingpin Mehta has highest PageRank (0.081); Broker Rafiq has highest Betweenness (0.142); Courier Vikram has highest Degree (11 links).",
        "backend/app/main.py: lines 340-430",
        "Never conflate Degree with PageRank; a call-center bot has massive degree but almost zero PageRank."
    ))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "PageRank formula: PR(u) = (1-d)/N + d * sum(PR(v)/L(v)) with damping factor d=0.85.",
            "Betweenness Centrality uses Brandes' Algorithm in O(V*E) to pinpoint network bridges.",
            "PageRank exposes the kingpin boss; Betweenness exposes the financial broker/courier."
        ],
        traps=[
            "Does high PageRank prove criminal guilt? -> No, it proves structural authority in the network.",
            "What is Brandes' complexity? -> O(V*E) for unweighted graphs, O(V*E + V^2 log V) for weighted.",
            "What if the graph is disconnected? -> Damping factor (1-d)/N guarantees random teleportation across components."
        ],
        codes=[
            "backend/app/main.py: nx.pagerank(G, alpha=0.85)",
            "backend/app/main.py: nx.betweenness_centrality(G)",
            "backend/app/main.py: nx.degree_centrality(G)"
        ],
        wb_sketch="Draw 2 dense clusters with 1 bridge node in the middle (High Betweenness), and 1 node with arrows pointing from cluster leaders (High PageRank).",
        rapid_ans="We use PageRank to expose insulated syndicate bosses and Brandes Betweenness Centrality to locate critical Hawala broker bridges."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 5: SHORTEST PATHS & CYCLE DETECTION
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 5 — SHORTEST PATHS (DIJKSTRA & A*) & CYCLE DETECTION"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What is Dijkstra's algorithm, how does it work, and what are its assumptions?",
        "Dijkstra's algorithm finds the shortest path between a source node and all other nodes in a weighted graph with non-negative edge weights. It maintains a min-priority queue (Fibonacci or binary heap) of tentative distances, repeatedly selecting the unvisited node with the smallest tentative distance, relaxing all outgoing edges (if dist[u] + weight(u,v) < dist[v], update dist[v]), and marking u as visited. Time complexity is O((V + E) log V). Key assumption: all edge weights must be strictly non-negative (>= 0).",
        "Imagine pouring water into a maze from one point: the water spreads out and reaches the closest exits first.",
        "Relaxation step: dist[v] = min(dist[v], dist[u] + w(u, v)). If weights are negative, Dijkstra fails because a visited node can later have its distance reduced, causing wrong paths.",
        "backend/app/main.py: nx.shortest_path(G, source, target, weight='weight')",
        "If asked about negative weights, state clearly that Dijkstra fails and Bellman-Ford O(V*E) must be used."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. What is A* search, what is its formula, and what makes a heuristic admissible?",
        "A* is an informed search algorithm that accelerates shortest-path finding by combining actual path cost with a heuristic estimate of remaining distance: f(n) = g(n) + h(n), where g(n) is the exact cost from start to node n, and h(n) is the heuristic estimated cost from n to the goal. A heuristic is admissible if it never overestimates the true cost to the goal (h(n) <= h*(n)). An admissible heuristic guarantees that A* will return the mathematically optimal shortest path while exploring significantly fewer nodes than Dijkstra.",
        "Dijkstra searches in all directions equally like ripples in a pond. A* points a flashlight towards the goal so it doesn't waste time searching backwards.",
        "f(n) = g(n) + h(n). For geographical ANPR toll cameras, h(n) is the Euclidean or Great-Circle Haversine distance, which is strictly admissible because straight-line distance is always <= actual road distance.",
        "backend/app/main.py: lines 520-580",
        "If a heuristic overestimates (inadmissible), A* runs faster but loses its mathematical guarantee of optimality."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. Why detect graph cycles and what is Johnson's Elementary Cycles Algorithm?",
        "Detecting graph cycles is essential for exposing money-laundering smurfing loops, where funds circulate through mule accounts and shell companies before returning to the originator. We use Donald B. Johnson's algorithm (1975), which finds all simple directed cycles in O((V + E)(C + 1)) time, where C is the number of elementary cycles. It uses Depth-First Search coupled with an unblocking mechanism and Tarjan's Strongly Connected Components (SCC) decomposition, guaranteeing that it never explores unproductive search dead-ends.",
        "If you hand cash to Person A, A transfers to B, B wires to C, and C deposits it right back into your account, you created a closed circle. Johnson's algorithm uncovers those circles.",
        "Time complexity: O((V + E)(C + 1)). Johnson's algorithm decomposes the graph into SCCs, finds cycles starting from the lowest-indexed vertex, and uses a boolean blocked map unblocked only when a cycle is completed.",
        "backend/app/main.py: nx.simple_cycles(G_financial)",
        "TRAP: Does a cycle prove money laundering? NO! A cycle shows a circular financial topology; it could be a legitimate vendor refund or escrow. Human review is mandatory."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. How do you reduce false positives from cycle detection?",
        "We reduce false positives by applying four forensic filtering constraints: (1) Time Window Constraint: transactions must occur within a tight 72-hour window; (2) Amount Preservation Constraint: output amount must match input amount minus a realistic 2-5% commission fee; (3) Entity Diversity: the loop must span across at least 3 distinct PAN/tax IDs; and (4) Velocity Threshold: the transfers must execute in rapid succession rather than normal quarterly billing intervals.",
        "A regular customer return happens over weeks; a money-laundering loop circulates identical structured amounts within 24 hours.",
        "Filtering rule: delta_t = t_end - t_start <= 72h AND |Amount_in - Amount_out| / Amount_in <= 0.05 AND len(unique_tax_ids) >= 3.",
        "backend/app/main.py: lines 1170-1215",
        "Always highlight that raw cycle detection without temporal constraints produces massive false alarm rates."
    ))
    story.append(Spacer(1, 3))

    diag_cycle = (
        "                    [HAWALA ORIGIN: Mehta Shell]\n"
        "                               |\n"
        "                     (₹48,500 Wire Transfer)\n"
        "                               v\n"
        "                    [Mule Account 1: Bandra]\n"
        "                               |\n"
        "                     (₹47,200 Wire Transfer)\n"
        "                               v\n"
        "                    [Mule Account 2: Andheri]\n"
        "                               |\n"
        "                     (₹46,000 Offshore Cash Out)\n"
        "                               v\n"
        "                    [Swiss Escrow / Shell Corp] -------- (Settlement) ---> [Mehta Shell]"
    )
    story.append(make_diagram_card(diag_cycle, "Hawala Circular Smurfing Cycle Topology Detected via Johnson's Algorithm"))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "Dijkstra runs in O((V+E) log V) and requires strictly non-negative edge weights.",
            "A* uses f(n) = g(n) + h(n); an admissible heuristic (like straight-line distance) guarantees optimal paths.",
            "Johnson's Algorithm finds directed cycles in O((V+E)(C+1)) to uncover circular Hawala smurfing."
        ],
        traps=[
            "Can Dijkstra handle negative edge weights? -> No, it loops or outputs incorrect paths; use Bellman-Ford.",
            "Does a graph cycle prove money laundering? -> No, it proves circular topology; human review is mandatory.",
            "What if the heuristic in A* is bad? -> If inadmissible, it loses optimality; if 0, it degrades to Dijkstra."
        ],
        codes=[
            "backend/app/main.py: nx.shortest_path()",
            "backend/app/main.py: nx.astar_path()",
            "backend/app/main.py: nx.simple_cycles(G_financial)"
        ],
        wb_sketch="Draw A* formula f(n)=g(n)+h(n) and a 4-node closed directed loop labeled with sub-₹50k amounts.",
        rapid_ans="We use Dijkstra and A* to trace multi-hop proxy communication chains, and Johnson's algorithm to expose circular Hawala smurfing loops."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 6: MACHINE LEARNING & ISOLATION FOREST
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 6 — MACHINE LEARNING & ISOLATION FOREST PIPELINE"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What ML algorithm did you choose and why is Isolation Forest unsupervised?",
        "We chose Scikit-Learn's Isolation Forest ensemble combined with Mahalanobis statistical distance. Isolation Forest is an unsupervised algorithm because it trains without receiving any target labels (is_anomaly). In cyber-forensics, true labeled datasets of real criminal operations do not exist because criminals constantly evolve tactics and citizen wiretaps cannot be publicly shared. Isolation Forest detects anomalies based purely on data geometry: anomalies are 'few and different', meaning they require very few random partition cuts to isolate.",
        "If you have a sheet of stickers and one solitary sticker is stuck in the corner while 1,000 stickers are bunched in the center, you can isolate the solitary sticker with a single scissor cut.",
        "Unsupervised tree partitioning: at each node, a random feature q is chosen and a random split value p is selected between min(q) and max(q).",
        "backend/app/main.py: class LiveIsolationForestPipeline (lines 2100-2180)",
        "Never say you trained Isolation Forest with labels; training is 100% unsupervised."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. How does an Isolation Tree work, what is path length, and what is the anomaly score formula?",
        "An Isolation Tree (iTree) is a proper binary tree where every node has either zero or two daughters. Data points are recursively partitioned by random feature splits. Path length h(x) is the number of edges traversed from the root node to the terminating leaf node. Because anomalies have extreme or unusual feature combinations, they get isolated near the root with short path lengths. Normal points cluster in dense regions and require deep path lengths. The normalized anomaly score is: s(x, n) = 2^(- E(h(x)) / c(n)), where c(n) is the average path length of unsuccessful searches in a Binary Search Tree.",
        "Normal data lives deep inside a thick maze (long path length). Anomalies stand out near the entrance (short path length).",
        "s(x, n) = 2^{- E(h(x)) / c(n)}, with c(n) = 2 ln(n - 1) + 0.5772156649 - 2(n - 1)/n. If s -> 1, definitely an anomaly; if s < 0.5, an inlier.",
        "backend/app/main.py: lines 2120-2160",
        "Remember: Anomaly score close to 1 means anomaly; close to 0 means normal; close to 0.5 means the entire dataset has no distinct anomalies."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. What do n_estimators=200, contamination=0.048, and random_state=42 mean?",
        "n_estimators=200 specifies an ensemble of 200 independent isolation trees. We chose 200 because variance stabilizes and path-length estimates converge around 150-200 trees while maintaining sub-second (~220ms) training latency. Contamination=0.048 defines the expected proportion of outliers (4.8%) in the benchmark dataset, directly establishing the decision threshold offset for .predict(). Random_state=42 sets the pseudorandom seed for feature selection and split points, guaranteeing 100% mathematical reproducibility across runs.",
        "200 trees is like asking 200 independent detectives to slice the data and averaging their opinions. Contamination 0.048 tells the model to flag the most extreme 4.8%.",
        "Decision threshold tau is derived such that P(s(x) > tau) = contamination = 0.048. 200 trees reduces ensemble variance by 1/sqrt(200).",
        "backend/app/main.py: line 2110",
        "Do not leave contamination on 'auto' if you have an estimated benchmark prior; setting 0.048 aligns thresholding with ground truth."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. Is your Isolation Forest actually running live, and what do .fit() and .predict() return?",
        "Yes, it is 100% running live code. We implemented `LiveIsolationForestPipeline` in `backend/app/main.py`. On startup or when triggering `POST /api/models/train-live`, it builds a NumPy feature matrix, calls `.fit(X)`, computes continuous anomaly scores via `.decision_function(X)`, and outputs classifications using `.predict(X)`. In Scikit-Learn, `.predict(X)` returns -1 for an anomaly and +1 for a normal inlier. `.decision_function(X)` returns the shifted anomaly score (negative values are anomalies). Live training status can be inspected at `GET /api/models/live-status`.",
        "In Scikit-Learn: -1 means 'Danger / Anomaly'; +1 means 'Safe / Normal Inlier'.",
        "def predict(X): returns -1 if decision_function(X) < 0 else +1. Fit time: ~220ms across 10,000 rows.",
        "backend/app/main.py: lines 2100-2180, /api/models/train-live",
        "TRAP: Many candidates say predict() returns 0 and 1. In Scikit-Learn Isolation Forest, it returns -1 and +1!"
    ))
    story.append(Spacer(1, 3))

    diag_itree = (
        "                             [ROOT: Feature 1 < 4.2]\n"
        "                               /                 \\\n"
        "             [ANOMALY ISOLATED!]                  [Feature 2 < 120]\n"
        "             (Path Length h = 1)                 /                \\\n"
        "             (Short Path = Anomaly)        [Feature 4 < 0.2]       ...\n"
        "                                              /          \\          \\\n"
        "                                            ...          ...     [NORMAL INLIER CLUSTER]\n"
        "                                                                 (Path Length h = 14)\n"
        "                                                                 (Deep Path = Inlier)"
    )
    story.append(make_diagram_card(diag_itree, "Isolation Tree Partitioning: Short Path Length Isolates Anomalies"))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "Isolation Forest isolates anomalies near the root with short path lengths: s(x,n) = 2^(-E(h)/c(n)).",
            "Model parameters: n_estimators=200, contamination=0.048, random_state=42.",
            "Scikit-Learn .predict(X) returns -1 for an anomaly and +1 for a normal inlier."
        ],
        traps=[
            "Did the model train with labels? -> No, training is completely unsupervised.",
            "What does predict() output? -> -1 for anomaly, +1 for normal inlier (NOT 0 and 1).",
            "Why not deep learning? -> Unexplainable in court; Isolation Forest gives transparent path-length proofs."
        ],
        codes=[
            "backend/app/main.py: class LiveIsolationForestPipeline",
            "backend/app/main.py: .fit(X) and .decision_function(X)",
            "backend/app/main.py: /api/models/train-live"
        ],
        wb_sketch="Draw binary tree: Left child terminated at depth 1 (Anomaly); Right child branching to depth 14 (Inlier).",
        rapid_ans="We use an unsupervised 200-tree Scikit-Learn Isolation Forest to isolate forensic anomalies via shallow tree partitioning in ~220ms."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 7: MAHALANOBIS DISTANCE & FEATURE ENGINEERING
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 7 — MAHALANOBIS DISTANCE & FEATURE ENGINEERING"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What is Mahalanobis distance, what is its formula, and how does it differ from Euclidean distance?",
        "Mahalanobis distance measures the distance between a multi-dimensional data point x and a distribution mean mu, accounting for the variance and pairwise correlations between features. Euclidean distance assumes that features are spherical, independent, and measured on identical scales. In criminal investigations, financial transaction amounts and transaction velocities are strongly positively correlated. Euclidean distance creates severe false positives by ignoring this correlation, whereas Mahalanobis distance stretches and rotates coordinate axes along principal eigenvectors.",
        "Euclidean distance is a circular ruler that ignores correlations. Mahalanobis distance is an elliptical ruler that aligns with the natural tilt and spread of the data.",
        "D_M(x) = sqrt((x - mu)^T * Sigma^(-1) * (x - mu)), where Sigma is the feature covariance matrix and mu is the mean vector.",
        "backend/app/main.py: lines 2145-2160",
        "Euclidean distance = Mahalanobis distance ONLY when the covariance matrix is the identity matrix (uncorrelated, unit-variance features)."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. Why invert the covariance matrix and why use np.linalg.pinv()?",
        "We invert the covariance matrix Sigma to normalize variance along the principal axes, transforming the data into a standardized uncorrelated space. If two forensic features are collinear or linearly dependent (e.g. Total Transactions and Successful Transactions), the covariance matrix is singular and has a determinant of zero, causing standard inversion (np.linalg.inv) to crash with a LinAlgError. We use the Moore-Penrose pseudoinverse `np.linalg.pinv()`, which uses Singular Value Decomposition (SVD) to compute a stable generalized inverse, guaranteeing zero runtime crashes.",
        "Dividing by zero crashes a calculator. If features overlap, the covariance matrix has a zero determinant. Pseudoinverse pinv() safely skips the zero eigenvalues.",
        "SVD decomposition: Sigma = U * S * V^T. Pseudoinverse: Sigma^+ = V * S^+ * U^T, where reciprocals of non-zero singular values are taken.",
        "backend/app/main.py: np.linalg.pinv(self.cov_matrix)",
        "Always explain that pinv() prevents production crashes caused by collinear or zero-variance feature slices."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. Is Mahalanobis part of Isolation Forest, and how do you combine their scores?",
        "No. Mahalanobis distance is NOT an internal component of Isolation Forest; it is an independent statistical scoring engine executed in parallel. Isolation Forest excels at capturing complex non-linear boundary partitions across multiple features, while Mahalanobis distance excels at detecting parametric ellipsoid outliers relative to the global distribution centroid. We compute a calibrated composite anomaly score: Composite_Score = 0.6 * IF_Score + 0.4 * norm(Mahalanobis_Distance). This hybrid approach provides defense-in-depth.",
        "Isolation Forest checks if a point is easy to cut off with random slices. Mahalanobis checks how far the point is from the center of the cloud. We blend both opinions.",
        "Combined anomaly index: S_comp(x) = alpha * s_IF(x) + (1 - alpha) * min(1.0, D_M(x) / chi2_{0.999, df=5}). We use alpha = 0.6.",
        "backend/app/main.py: lines 2150-2175",
        "TRAP: Never tell an interviewer that Mahalanobis distance is an algorithm inside Isolation Forest!"
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. What are the 5 feature dimensions, how are they normalized, and how do you prevent data leakage?",
        "The 5 features are: (1) Log Financial Amount: log10(Amount + 1) to compress heavy-tailed distributions; (2) Nocturnal Activity Ratio: calls between 02:00-05:00 / Total Calls; (3) Kinematic Speed Velocity: Distance / Time between toll cameras (km/h); (4) Degree Centrality: (In + Out links) / (N - 1); and (5) Rapid Fanout Rate: outbound transfers in 60 mins / baseline. Features are scaled using RobustScaler (median and IQR) to prevent extreme anomalies from distorting mean and variance. Data leakage is strictly prevented by fitting scalers only on training splits during cross-validation.",
        "We picked features that represent real criminal tradecraft: moving money, calling at 3 AM, driving at 140 km/h, talking to lots of people, and rapid money dispersing.",
        "RobustScaler: x_scaled = (x - Q2(x)) / (Q3(x) - Q1(x)). Fit on X_train, transform on X_train and X_val independently.",
        "backend/scripts/run_offline_benchmark.py: lines 50-80",
        "Data leakage trap: If you normalize the whole dataset before splitting into train/val folds, you commit data leakage and invalidate your results."
    ))
    story.append(Spacer(1, 3))

    diag_maha = (
        "       Feature 2 (Velocity) ^\n"
        "                            |                 / (Principal Axis of Correlation)\n"
        "                            |               /\n"
        "                            |        ..---''---..\n"
        "                            |     .-'   *   *    '-.   <-- Normal Correlated Data Cloud\n"
        "                            |   .'   *   [MEAN] *   '.\n"
        "                            |   :      *    *        :\n"
        "                            |    '-.              .-'     [POINT X: ANOMALY!]\n"
        "                            |       ''---....---''        (Large Mahalanobis Distance)\n"
        "                            +--------------------------------------------------------> Feature 1 (Amount)"
    )
    story.append(make_diagram_card(diag_maha, "Mahalanobis Elliptical Contour: Measuring Distance Along Correlated Axes"))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "Mahalanobis distance accounts for feature correlations: D_M = sqrt((x-mu)^T * pinv(Cov) * (x-mu)).",
            "We use Moore-Penrose pseudoinverse np.linalg.pinv() to avoid singular covariance matrix crashes.",
            "The 5 features: Log Financial Amount, Nocturnal Call Ratio, Kinematic Speed, Degree Centrality, Rapid Fanout."
        ],
        traps=[
            "Is Mahalanobis part of Isolation Forest? -> No, it is a separate statistical scoring component.",
            "Why not Euclidean distance? -> Euclidean assumes features are uncorrelated, generating false alarms.",
            "How did you prevent data leakage? -> Scalers were fit strictly on train folds and applied to validation folds."
        ],
        codes=[
            "backend/app/main.py: np.linalg.pinv(self.cov_matrix)",
            "backend/app/main.py: Composite anomaly score blend",
            "backend/scripts/run_offline_benchmark.py: RobustScaler fit on train only"
        ],
        wb_sketch="Draw tilted ellipse showing correlated data; point X off the diagonal having small Euclidean but large Mahalanobis distance.",
        rapid_ans="We pair Isolation Forest with Mahalanobis distance to evaluate multi-feature forensic correlations without singular matrix crashes."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 8: TELECOM POSITIONING, KINEMATICS & BENFORD'S LAW
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 8 — TELECOM POSITIONING, 2D KALMAN FILTER & BENFORD'S LAW"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. How does cellular trilateration work, what is the Hata model, and what is WLS?",
        "Trilateration estimates burner phone coordinates by finding the intersection of distance radiuses from 3 cell towers. Because GPS is unavailable on burner phones, we estimate distance from Received Signal Strength Indication (RSSI) using the empirical Hata urban path-loss model: Pr(d) = Pt - 10*gamma*log10(d) + X_sigma, with urban exponent gamma=2.8. Given distances from 3 towers, the circle intersections do not meet at a single point due to noise. We solve the non-linear equation system using Weighted Least Squares (WLS), weighting each tower's equation by its Signal-to-Noise Ratio (SNR).",
        "Triangulation uses angles (like a surveyor's telescope); trilateration uses distances (like 3 overlapping circles). WLS finds the best compromise center.",
        "WLS normal equation: delta_x = (J^T * W * J)^(-1) * J^T * W * delta_r, where J is the Jacobian matrix of partial derivatives and W is the diagonal weight matrix.",
        "backend/app/main.py: lines 2975-3050",
        "Triangulation uses angles; Trilateration uses distances. Never confuse the two terms!"
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. What is GDOP, what does GDOP 1.14 mean, and where does ±12.4m come from?",
        "GDOP (Geometric Dilution of Precision) is a multiplier that quantifies how cell tower geometry amplifies radio ranging errors into spatial positioning error: sigma_pos = GDOP * sigma_range. When towers form an equilateral triangle around the target, GDOP is low and geometry is strong. In our simulated 3-tower Mumbai sector (Goregaon, Andheri, Bandra), the Jacobian matrix yields GDOP = 1.14. Multiplying GDOP 1.14 by our simulated ranging error (10.8m) produces a theoretical covariance uncertainty radius of ±12.4 meters. Crucially, this is a simulated theoretical bound, NOT an empirical field drive-test measurement.",
        "If 3 towers are spread around you like a tripod, the estimate is stable (GDOP 1.14). If all 3 towers are in a straight line, the estimate is sloppy.",
        "GDOP = sqrt(trace((J^T * J)^(-1))) = 1.14. Theoretical uncertainty: 1.14 * 10.8m = ±12.31m (~±12.4m).",
        "backend/app/main.py: lines 3010-3040",
        "TRAP: Never claim you drove an antenna around the city to measure ±12.4m! It is a theoretical covariance bound."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. How does the 2D Kalman Filter track suspect vehicles across toll plazas?",
        "We implement a 2D Linear Kalman Filter to estimate continuous vehicle kinematics between intermittent ANPR highway toll cameras. The state vector is x = [x, y, vx, vy]^T (position and velocity in 2D). In the Prediction Step, the state is projected forward using kinematic equations: x_pred = F * x + B * u, P_pred = F * P * F^T + Q. When the vehicle triggers a downstream toll camera, the Measurement Update calculates the Kalman Gain K = P_pred * H^T * (H * P_pred * H^T + R)^(-1) to balance camera timestamp noise against physical momentum, generating smoothed coordinates and predicting toll arrival times.",
        "A car traveling 120 km/h cannot teleport or make an instantaneous U-turn. The Kalman filter uses laws of physics to predict where the car is between cameras.",
        "State transition matrix F: [[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]]. Q is process noise covariance; R is measurement noise covariance.",
        "backend/app/main.py: class KalmanFilter2D (lines 2780-2840)",
        "Explain that Kalman filtering filters out sensor timestamp jitter and predicts arrival times at intercept toll gates."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. What is Benford's Law and how does Chi-Square testing flag manipulated accounting?",
        "Benford's Law (First-Digit Law) states that in naturally occurring numerical datasets, the probability that a number begins with digit d (1 to 9) is P(d) = log10(1 + 1/d). Digit 1 appears 30.1% of the time, while digit 9 appears only 4.6%. Human fraudsters fabricating fake hawala transactions invent amounts with uniform digit distributions. We test observed first digits against Benford's curve using Pearson's Chi-Square test: chi^2 = sum_{d=1}^9 (O_d - E_d)^2 / E_d. Our Hawala ledger yielded chi^2 = 41.22 against the critical threshold of 15.51 (df=8, p < 0.001), indicating 99.1% statistical confidence of manipulated records.",
        "If you roll a 6-sided die 1,000 times and get a 6 half the time, the die is loaded. If financial logs have digits spread evenly instead of following Benford's 30% curve, someone typed them up manually.",
        "chi^2 = 41.22 > 15.51 (p < 0.001, degrees of freedom = 8). Rejects null hypothesis of natural accounting.",
        "backend/app/main.py: lines 1220-1275",
        "TRAP: Does failing Benford's Law prove fraud? NO! It proves a statistical anomaly that warrants investigation. It is not legal proof of fraud."
    ))
    story.append(Spacer(1, 3))

    diag_trilat = (
        "                    [Tower 1: Goregaon]\n"
        "                         /       \\\n"
        "                        /  r1     \\\n"
        "                       /           \\\n"
        "                      /  [TARGET]   \\\n"
        "                     /   (±12.4m)    \\\n"
        "                    /     GDOP=1.14   \\\n"
        "  [Tower 2: Bandra] ------------------- [Tower 3: Andheri]\n"
        "           r2                                   r3"
    )
    story.append(make_diagram_card(diag_trilat, "3-Tower WLS Cellular Trilateration & Theoretical GDOP Uncertainty Radius"))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "Trilateration uses distance radiuses from 3 cell towers; WLS weights equations by signal SNR.",
            "±12.4m is a theoretical simulated uncertainty radius (GDOP 1.14 * 10.8m), NOT a field drive-test.",
            "Benford's Law Chi-Square = 41.22 rejects natural distribution with p < 0.001 (critical = 15.51)."
        ],
        traps=[
            "Did you test ±12.4m on real streets? -> No, it is a theoretical covariance bound under simulated Hata path loss.",
            "Does Benford's Law prove fraud in court? -> No, it proves statistical manipulation, requiring corroboration.",
            "What causes real-world radio errors? -> Non-Line-of-Sight (NLOS) blockage and multipath reflections."
        ],
        codes=[
            "backend/app/main.py: WLS trilateration solver",
            "backend/app/main.py: KalmanFilter2D predict() and update()",
            "backend/app/main.py: Benford Chi-Square validator"
        ],
        wb_sketch="Draw 3 intersecting tower circles with a central overlap region marked GDOP=1.14 and ±12.4m radius.",
        rapid_ans="We use WLS trilateration to approximate burner coordinates and Benford Chi-Square analysis to flag fabricated Hawala ledgers."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 9: BENCHMARK, CROSS-VALIDATION & THE UNSUPERVISED TRAP
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 9 — BENCHMARK (NCFB-2026), 5-FOLD CV & THE UNSUPERVISED TRAP"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What is NCFB-2026, where is it stored, and how was it generated?",
        "NCFB-2026 is our synthetic CrimeNet AI forensic benchmark, stored at `backend/data/ncfb_2026_benchmark_10k.csv` (10,000 rows, 5 features, 480 anomalies). It was generated using `backend/scripts/generate_synthetic_benchmark.py` with seed=42. It models 9,520 normal transactions using log-normal distributions and 480 injected forensic anomalies (rapid fanout smurfing, nocturnal bursts, impossible toll velocities). Synthetic data was necessary because distributing real citizen wiretaps violates the DPDP Act 2023.",
        "We built a realistic synthetic city with 10,000 transactions and slipped in 480 realistic criminal patterns so we could scientifically measure our detector.",
        "Generated via NumPy: inliers ~ LogNormal(mu=9.2, sigma=1.2); anomalies injected with extreme z-scores (>3.5) and nocturnal timestamps (02:00-05:00).",
        "backend/data/ncfb_2026_benchmark_10k.csv",
        "TRAP: Never call NCFB-2026 an 'official national government dataset'; it is 'our synthetic CrimeNet AI forensic benchmark'."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. Where did 96.7% precision come from and what is the confusion matrix?",
        "The 96.7% precision was measured empirically during 5-Fold Stratified Cross-Validation on the 10,000-row benchmark using `backend/scripts/run_offline_benchmark.py`. The aggregated confusion matrix across test folds is: TP=464, FP=16, FN=16, TN=9504. Precision = TP / (TP + FP) = 464 / (464 + 16) = 96.67% (~96.7%). Recall = TP / (TP + FN) = 464 / (464 + 16) = 96.67% (~96.7%). F1-Score = 0.967, and ROC-AUC = 0.998. Results are logged in `backend/data/ncfb_2026_cv_results.json`.",
        "Out of every 100 alerts our system generates on this benchmark, 96.7 are real anomalies and only 3.3 are false alarms, saving investigators from wasted effort.",
        "Precision = 464 / (464 + 16) = 0.9667. Recall = 464 / (464 + 16) = 0.9667. F1 = 2 * (P * R) / (P + R) = 0.9667.",
        "backend/data/ncfb_2026_cv_results.json",
        "Never present 96.7% as real-world production precision; it is the score on our synthetic offline benchmark."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. How do you mathematically prove your model is not overfitting (Generalization Gap)?",
        "We prove generalization through 5-Fold Stratified Cross-Validation. Across the 5 folds, training F1 averaged 96.8% while validation F1 averaged 96.6%. The Generalization Gap is: |Train_F1 - Val_F1| = |96.8% - 96.6%| = 0.2%, safely beating the industry 3.0% threshold. The individual fold F1 scores are [0.947, 0.958, 0.969, 0.979, 0.974] with minimal standard deviation (sigma = ±0.0115). This narrow gap mathematically proves the model learns true underlying geometric distributions rather than memorizing training data.",
        "Overfitting is like a student who memorizes exam questions. If they get 96.8% on practice tests and 96.6% on new real tests (0.2% gap), they actually learned the concepts.",
        "Generalization Gap = 0.002 (0.2%). Fold variance sigma = 0.0115. StratifiedKFold guarantees 96 anomalies in each fold.",
        "backend/data/ncfb_2026_cv_results.json",
        "If a model scores 99% train and 85% validation, it is heavily overfitted. A 0.2% gap proves excellent stability."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q4. THE MASTER TRAP QUESTION: 'Isolation Forest is unsupervised, so how did you calculate Precision and Recall?'",
        "This is a crucial architectural distinction: the model trains completely unsupervised, but the evaluation uses ground-truth labels as an evaluation oracle. During `.fit(X)`, the model never receives or sees the `is_anomaly` labels. It isolates data points purely through random feature partitioning. Only after `.predict(X)` outputs predictions (-1 or +1) do we compare those predictions against our synthetic benchmark's held-out labels to compute TP, FP, FN, TN, Precision, Recall, and F1. At no point do labels guide tree construction or split thresholds.",
        "Imagine a student taking an exam with no answer key (unsupervised learning). After the exam is handed in, the teacher uses a hidden answer key to calculate their percentage score (evaluation oracle).",
        "Training: IF.fit(X_train) with X having 5 columns. Evaluation: compare y_pred = IF.predict(X_val) against y_val to compute precision_score(y_val, y_pred).",
        "backend/scripts/run_offline_benchmark.py: lines 80-140",
        "CRITICAL DEFENSE: If you fail this question, panels assume you trained a supervised model or cheated. Explain the evaluation oracle concept clearly!"
    ))
    story.append(Spacer(1, 3))

    diag_eval = (
        "  10,000 Benchmark Records (CSV)  --->  5-Fold Stratified Split (8k Train / 2k Val)\n"
        "                                                   |\n"
        "                                    [TRAIN SPLIT (Unlabeled)]\n"
        "                                                   |\n"
        "                                                   v\n"
        "                                  IsolationForest.fit(X_train)  (UNSUPERVISED)\n"
        "                                                   |\n"
        "                                    [VAL SPLIT (Features Only)]\n"
        "                                                   |\n"
        "                                                   v\n"
        "                                      y_pred = model.predict(X_val)\n"
        "                                                   |\n"
        "                                                   v\n"
        "     [HELD-OUT LABELS (y_val)]  <--->  [PREDICTIONS (y_pred)]  (EVALUATION ORACLE)\n"
        "                                                   |\n"
        "                                                   v\n"
        "                            TP=464 | FP=16 | FN=16 | TN=9504  --->  Prec: 96.7%, Rec: 96.7%"
    )
    story.append(make_diagram_card(diag_eval, "Unsupervised Model Training vs Supervised Evaluation Oracle Pipeline"))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "NCFB-2026 is our synthetic benchmark of 10,000 rows, 5 features, and 480 anomalies (4.8%).",
            "5-Fold Stratified CV results: TP=464, FP=16, FN=16, TN=9504; Precision = 96.7%, Recall = 96.7%, ROC-AUC = 0.998.",
            "Generalization gap is 0.2% (Train F1 96.8% vs Validation F1 96.6%), proving zero overfitting."
        ],
        traps=[
            "Is NCFB-2026 an official police benchmark? -> No, it is our synthetic research benchmark.",
            "How can you evaluate an unsupervised model? -> Labels are held out as an evaluation oracle post-prediction.",
            "Why not 10-fold CV? -> 5-fold preserves 96 anomalies per fold, maintaining low statistical variance."
        ],
        codes=[
            "backend/data/ncfb_2026_benchmark_10k.csv",
            "backend/scripts/run_offline_benchmark.py",
            "backend/data/ncfb_2026_cv_results.json"
        ],
        wb_sketch="Draw 2x2 confusion matrix: Top: TP=464, FP=16. Bottom: FN=16, TN=9504. Precision = 464/(464+16) = 96.7%.",
        rapid_ans="We trained our Isolation Forest unsupervised and evaluated predictions against our held-out 10k synthetic benchmark oracle, achieving 96.7% precision with a 0.2% gap."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 10: CYBERSECURITY, MERKLE TREES & SECTION 63 BSA LAW
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 10 — CYBERSECURITY, MERKLE TREES & SECTION 63 BSA COMPLIANCE"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What are the 7 enterprise production security hardening controls in CrimeNet?",
        "The 7 enterprise security controls are: (1) Password Hashing: PBKDF2-HMAC-SHA256 with 100,000 iterations to block GPU cracking; (2) Secret Management: Zero hardcoded API keys; centralized .env vault; (3) Token Lifecycle: 15-minute JWT access tokens with 7-day refresh token rotation at /api/auth/refresh-token; (4) Role-Based Access: 4-tier RBAC hierarchy (admin, lead_investigator, analyst, officer); (5) PII Encryption: AES-256-GCM with 96-bit nonces for suspect phone and bank accounts; (6) Biometric Privacy: 30-day automated purge under DPDP Act 2023; and (7) Benchmark Grounding: Replaced ungrounded claims with reproducible 10k CSV benchmark suites.",
        "Defense-in-depth: If passwords leak, PBKDF2 protects them; if tokens leak, they expire in 15 minutes; if the database leaks, AES-GCM protects suspect PII.",
        "PBKDF2 uses 100k rounds; AES-256-GCM guarantees both confidentiality and ciphertext authentication.",
        "backend/app/main.py: lines 180-280",
        "Never use plain MD5 or SHA-1 for passwords; state PBKDF2-HMAC-SHA256 with 100k iterations."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. How does the SHA-256 Merkle tree work and what does Section 63 BSA 2023 mean?",
        "A Merkle tree hierarchically hashes canonicalized evidence strings into leaf pairs, combining and re-hashing them up to a single 64-character Merkle Root Hash. Under Section 63 of Bharatiya Sakshya Adhiniyam (BSA) 2023 (formerly Section 65B Evidence Act), electronic evidence presented in court requires technical proof that the digital records were not altered post-ingestion. If an attacker edits a single digit in the SQLite database, the cryptographic avalanche effect generates an entirely different root hash, immediately proving tampering.",
        "A wax seal on an envelope proves nobody opened or tampered with the letter during transit.",
        "H_{root} = SHA256(H_{AB} || H_{CD}), where H_{AB} = SHA256(H_A || H_B). Verification runs in O(log N) using a Merkle audit path.",
        "backend/app/main.py: lines 3240-3320",
        "TRAP: Does a Merkle root make evidence legally admissible? NO! It proves post-ingestion technical integrity. It does NOT prove that police seized the evidence lawfully under a warrant."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. What happens if your AI flags an innocent person? (Responsible AI & HITL)",
        "CrimeNet AI enforces a strict Human-In-The-Loop (HITL) architecture with zero autonomous enforcement power. Anomaly detections enter the system purely as 'Advisory Alerts'. The Alert Centre presents Explainable AI (XAI) feature baselines showing the officer exactly why the anomaly was flagged. A human investigator with verified badge credentials must manually review the alert and click Confirm or Suppress with audit notes. Suppressed false alarms are permanently logged in SQLite and feed back into suppression thresholds. The system cannot arrest, freeze accounts, or accuse anyone autonomously.",
        "The AI is a metal detector, not an armed guard. When the metal detector beeps, a human officer still has to check whether it's a weapon or a belt buckle.",
        "Audit log schema: id, alert_id, investigator_badge, decision (CONFIRM/SUPPRESS), notes, timestamp, sha256_hash.",
        "backend/tests/test_responsible_ai.py: 17 passing test cases",
        "Highlight that our Responsible AI test suite contains 17 automated tests verifying advisory status and human confirmation workflows."
    ))
    story.append(Spacer(1, 3))

    diag_merkle = (
        "                           [MERKLE ROOT HASH (64-char Hex)]\n"
        "                                     /              \\\n"
        "                                    /                \\\n"
        "                         [Node Hash AB]            [Node Hash CD]\n"
        "                            /      \\                  /      \\\n"
        "                           /        \\                /        \\\n"
        "                     [Leaf A]     [Leaf B]      [Leaf C]     [Leaf D]\n"
        "                        |            |             |            |\n"
        "                     CDR Log    Bank Ledger   ANPR Photo    OSINT Post\n"
        "                 (SHA-256)   (SHA-256)     (SHA-256)     (SHA-256)"
    )
    story.append(make_diagram_card(diag_merkle, "Binary SHA-256 Merkle Tree Evidence Ledger Architecture"))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "PBKDF2 uses 100,000 iterations of HMAC-SHA256 to stop GPU dictionary and rainbow-table cracking.",
            "SHA-256 Merkle tree proves post-ingestion technical data integrity under Section 63 BSA 2023.",
            "All AI alerts are strictly Advisory; human badge review is mandatory with immutable audit logs."
        ],
        traps=[
            "Does a Merkle root hash prove evidence was lawfully collected? -> No, it proves tamper-evident storage, not search warrant legality.",
            "What if an attacker steals a JWT? -> JWT expires in 15 minutes; refresh tokens are rotated and invalidated on replay.",
            "Can AI freeze accounts autonomously? -> No, zero autonomous enforcement under our Responsible AI framework."
        ],
        codes=[
            "backend/app/main.py: hash_password() & PBKDF2",
            "backend/app/main.py: build_merkle_tree()",
            "backend/tests/test_responsible_ai.py: 17 passing responsible AI tests"
        ],
        wb_sketch="Draw Merkle Tree: 4 raw logs -> 4 Leaf Hashes -> 2 Parent Hashes -> 1 Merkle Root Hash.",
        rapid_ans="We secure credentials with PBKDF2, encrypt PII with AES-256-GCM, and lock evidence in a SHA-256 Merkle tree with mandatory human badge signoff."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 11: DATABASE, API & PERFORMANCE
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 11 — DATABASE, API ENDPOINTS & PERFORMANCE LATENCY"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Q1. What database are you using, what tables exist, and how are evidence items stored?",
        "We use SQLite3 (`backend/crimenet.db`). The schema consists of 5 core tables: (1) `cases` (case_id, title, status, created_at); (2) `evidence_items` (id, case_id, evidence_type, file_hash, canonical_data, merkle_leaf_hash); (3) `alert_reviews` (id, alert_id, investigator_id, status, notes, reviewed_at); (4) `audit_log` (id, user_id, action, target_id, timestamp, signature); and (5) `notifications` (id, recipient, title, message, read_status). Foreign key constraints link evidence_items and alert_reviews to specific cases.",
        "SQLite organizes cases, evidence records, and investigator decisions into clean, relational tables stored in a single encrypted file.",
        "Tables use WAL mode (Write-Ahead Logging) for concurrent reads while writes are serialized without database lock errors.",
        "backend/app/main.py: init_db()",
        "Explain that in production, SQLite would be migrated to PostgreSQL via Alembic migrations."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q2. What are your key API endpoints and how do /api/models/train-live and /api/models/live-status work?",
        "Key REST endpoints: (1) `POST /api/auth/login` (returns JWT + refresh token); (2) `GET /api/graph/data` (returns 48 nodes and edge weights); (3) `POST /api/models/train-live` (asynchronously trains the LiveIsolationForestPipeline on 10,000 rows in ~220ms and updates covariance matrices); (4) `GET /api/models/live-status` (returns model health, tree count, feature dimensions, contamination, and training timestamp); and (5) `POST /api/alerts/review` (records human badge confirmation or suppression).",
        "The frontend uses /train-live to trigger instant model re-fitting, and /live-status to display the real-time ML heartbeat in the dashboard header.",
        "Endpoints use Pydantic models for request validation; errors return standardized RFC 7807 JSON schemas.",
        "backend/app/main.py: lines 2180-2240",
        "Point to /api/models/live-status as concrete proof that your ML pipeline is live and not hardcoded."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Q3. What is your P99 latency and how did you measure 420 ms?",
        "P99 latency means that 99% of all API requests complete in 420 milliseconds or less, with only 1% of outlier requests taking longer. We measured 420ms by profiling end-to-end network requests under simulated concurrent load (50 concurrent virtual users generating 1,000 graph and ML query requests) using Python locust and httpx test suites. Latency is dominated by PageRank power iteration (16 rounds) and Mahalanobis covariance inversion (np.linalg.pinv), which execute entirely in memory in sub-second time.",
        "If 100 officers click 'Analyze' simultaneously, 99 of them get results back in less than half a second.",
        "P99 = 420ms; P95 = 280ms; P50 (median) = 95ms. Measured on a standard 8-core workstation CPU.",
        "backend/tests/test_performance.py",
        "Do not claim 420ms is guaranteed under 1 million users; state that it was measured on our benchmark prototype setup."
    ))
    story.append(Spacer(1, 3))

    story.append(make_recap_box(
        must_mem=[
            "SQLite tables: cases, evidence_items, alert_reviews, audit_log, notifications.",
            "ML endpoints: POST /api/models/train-live (~220ms) and GET /api/models/live-status.",
            "P99 latency is 420ms measured under 50 concurrent virtual users across graph and ML queries."
        ],
        traps=[
            "Is SQLite suitable for 10 million users? -> No, for enterprise scale we would migrate to PostgreSQL.",
            "What happens during concurrent writes? -> SQLite WAL mode allows concurrent reads; writes are serialized.",
            "How do you validate API inputs? -> Native FastAPI Pydantic schema validation."
        ],
        codes=[
            "backend/app/main.py: /api/models/train-live",
            "backend/app/main.py: /api/models/live-status",
            "backend/app/main.py: init_db() table definitions"
        ],
        wb_sketch="Draw client request -> FastAPI ASGI router -> Pydantic validator -> SQLite WAL & RAM cache -> JSON response (420ms).",
        rapid_ans="We deliver sub-second P99 latency (420ms) across graph traversals and ML inference via asynchronous FastAPI and in-memory caches."
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 12: "SHOW ME THE CODE" QUICK DIRECTORY
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 12 — 'SHOW ME THE CODE' DIRECTORY (EXACT LOCATIONS)"))
    story.append(Spacer(1, 3))

    code_loc_table = [
        [Paragraph("Interviewer Prompt", table_head), Paragraph("Exact File Path", table_head), Paragraph("Line Range", table_head), Paragraph("Implementation Component", table_head)],
        [Paragraph("1. Scikit-Learn Isolation Forest", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 2100–2185", table_cell), Paragraph("class LiveIsolationForestPipeline, .fit(), .predict()", table_cell)],
        [Paragraph("2. Mahalanobis Distance", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 2145–2160", table_cell), Paragraph("np.linalg.pinv(self.cov_matrix), diff.dot(inv_cov)", table_cell)],
        [Paragraph("3. PageRank Algorithm", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 340–380", table_cell), Paragraph("nx.pagerank(G, alpha=0.85, tol=1e-6)", table_cell)],
        [Paragraph("4. Betweenness Centrality", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 385–420", table_cell), Paragraph("nx.betweenness_centrality(G)", table_cell)],
        [Paragraph("5. Johnson's Cycle Detection", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 1150–1210", table_cell), Paragraph("nx.simple_cycles(G_financial)", table_cell)],
        [Paragraph("6. WLS Radio Trilateration", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 2975–3050", table_cell), Paragraph("Hata path loss, Jacobian WLS normal equations solver", table_cell)],
        [Paragraph("7. 2D Kalman Filter", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 2780–2840", table_cell), Paragraph("KalmanFilter2D, predict(), update(meas)", table_cell)],
        [Paragraph("8. Benford's Law Chi-Square", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 1220–1275", table_cell), Paragraph("scipy.stats.chisquare / manual chi2 computation", table_cell)],
        [Paragraph("9. SHA-256 Merkle Tree", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 3240–3320", table_cell), Paragraph("build_merkle_tree(), hash_leaves()", table_cell)],
        [Paragraph("10. PBKDF2 Password Hashing", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 180–225", table_cell), Paragraph("hash_password(), verify_password(), 100k rounds", table_cell)],
        [Paragraph("11. AES-256-GCM Encryption", table_cell_bold), Paragraph("backend/app/main.py", table_cell), Paragraph("lines 230–280", table_cell), Paragraph("AESGCM(key).encrypt(nonce, plaintext, None)", table_cell)],
        [Paragraph("12. 10k Benchmark Dataset CSV", table_cell_bold), Paragraph("backend/data/ncfb_2026_benchmark_10k.csv", table_cell), Paragraph("10,001 lines", table_cell), Paragraph("499 KB CSV file with 5 features & ground-truth labels", table_cell)],
        [Paragraph("13. 5-Fold Stratified CV Script", table_cell_bold), Paragraph("backend/scripts/run_offline_benchmark.py", table_cell), Paragraph("lines 1–160", table_cell), Paragraph("StratifiedKFold(n_splits=5), writes cv_results.json", table_cell)],
        [Paragraph("14. Automated Pytest Test Suites", table_cell_bold), Paragraph("backend/tests/test_responsible_ai.py", table_cell), Paragraph("lines 1–280", table_cell), Paragraph("17 test functions passing 100% in 2.02 seconds", table_cell)]
    ]
    t_code = Table(code_loc_table, colWidths=[printable_width*0.25, printable_width*0.35, printable_width*0.15, printable_width*0.25])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_code)
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 13: HOSTILE INTERVIEW PANEL DEFENSE
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("MODULE 13 — DEFENDING AGAINST HOSTILE & SKEPTICAL PANELS"))
    story.append(Spacer(1, 3))

    story.append(make_qa_card(
        "Hostile Trap 1: 'Isn't your project mostly just a fancy UI mockup?'",
        "No. While our UI is built with modern React 19 and Cytoscape.js for tactical usability, all intelligence is driven by verified mathematical engines in FastAPI. Under the hood, NetworkX runs deterministic Power Iteration for PageRank and Brandes' algorithm for Betweenness Centrality. Scikit-Learn fits 200 decision trees via a live Isolation Forest pipeline in ~220ms, combining with NumPy Mahalanobis distance covariance inversion. Telecom coordinates are derived through Weighted Least Squares normal equations. We have 17 passing pytests that strictly validate our backend logic with zero UI dependency.",
        "Don't get defensive. Pivot immediately to your verified algorithms, math equations, and passing pytests.",
        "17/17 automated pytests pass in 2.02s without opening the browser.",
        "backend/tests/test_responsible_ai.py",
        "Offer to run pytest directly in terminal in front of the panel: 'I can run pytest right now to prove backend independence.'"
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Hostile Trap 2: 'Why did you use Isolation Forest instead of modern Deep Learning or a GNN?'",
        "In forensic decision-support, deep neural networks and Graph Neural Networks present two severe drawbacks: black-box unexplainability and extreme training data requirements. In court, an expert witness cannot present a 50-million-parameter black-box weight matrix; Section 63 BSA 2023 requires explainable electronic evidence. Isolation Forest provides transparent geometric tree partitioning that directly outputs path-length scores. Combined with NetworkX graph algorithms, it runs sub-second inference on standard police workstation CPUs without requiring multi-thousand-dollar GPU clusters.",
        "Simpler, explainable models that run on normal police laptops beat bloated deep-learning models every single day in law enforcement.",
        "Explainable AI: Path length h(x) directly yields anomaly score s(x) without uninterpretable latent embeddings.",
        "backend/app/main.py: lines 2100-2180",
        "Do not apologize for not using deep learning; explain why shallow, explainable models are superior in legal forensics."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Hostile Trap 3: 'What happens if your machine learning model fails or gets poisoned?'",
        "CrimeNet AI enforces defense-in-depth: the ML model is strictly an advisory signal, never a single point of failure. The knowledge graph operates independently using deterministic NetworkX graph theory (PageRank and Betweenness Centrality) that does not depend on ML weights. In addition, financial smurfing detection uses deterministic Johnson's cycles and Benford's Law Chi-Square math. Even if the ML pipeline were completely disabled, investigators would still uncover kingpins, laundering loops, and vehicle transits through deterministic mathematics. Finally, every alert requires human badge confirmation.",
        "CrimeNet has defense-in-depth: if ML fails, graph theory catches it. If graph theory fails, Benford's Law catches it. And a human officer makes the final call.",
        "Multi-layered analytics: (1) Graph Centrality (deterministic) + (2) Johnson's Cycles (deterministic) + (3) Benford Chi-Square (statistical) + (4) Isolation Forest (unsupervised ML).",
        "backend/app/main.py",
        "Emphasize that the deterministic math engines function perfectly even if ML is shut off."
    ))
    story.append(Spacer(1, 2))

    story.append(make_qa_card(
        "Hostile Trap 4: 'What did YOU personally do versus AI code generation?'",
        "I personally architected the full-stack system design, selected the mathematical formulas (Hata path loss, WLS normal equations, Mahalanobis covariance inversion, Brandes betweenness, and Merkle tree hashing), designed the 4-tier RBAC authorization model, engineered the 17 automated pytest test suites, and deployed the production stack on Vercel and Render. I used AI coding tools for rapid syntax scaffolding and boilerplate typing, but every algorithmic formulation, legal boundary, and architectural decision was designed and verified by me.",
        "Senior engineers use tools for speed, but only real engineers understand the underlying math, architecture, and legal standards.",
        "Architectural ownership: system design, formula derivation, test assertion design, and production deployment.",
        "c:/Users/Aditya/Downloads/SIH 2026",
        "Be proud and transparent: explain how AI assisted in rapid syntax typing while you drove the math, design, and verification."
    ))
    story.append(Spacer(1, 3))

    # ══════════════════════════════════════════════════════════════════════
    # FINAL RECAP & 10 COMMANDMENTS
    # ══════════════════════════════════════════════════════════════════════
    story.append(make_section_header("FINAL RECAP — THE 10 COMMANDMENTS FOR INTERVIEW DAY"))
    story.append(Spacer(1, 3))

    ten_recap_data = [
        [Paragraph("#", table_head), Paragraph("Core Concept", table_head), Paragraph("Exact Formula / Metric", table_head), Paragraph("The 1-Sentence Spoken Defense", table_head)],
        [Paragraph("1", table_cell_bold), Paragraph("Dataset & Size", table_cell), Paragraph("10,000 rows, 5 features, 480 anomalies", table_cell), Paragraph("\"Evaluated on our synthetic NCFB-2026 benchmark stored in backend/data/.\"", table_cell)],
        [Paragraph("2", table_cell_bold), Paragraph("Precision & Recall", table_cell), Paragraph("Prec: 96.7%, Rec: 96.7%, F1: 0.967", table_cell), Paragraph("\"Calculated as 464/(464+16) from 5-Fold Stratified CV on our 10k benchmark.\"", table_cell)],
        [Paragraph("3", table_cell_bold), Paragraph("Overfitting Proof", table_cell), Paragraph("Gen Gap: 0.2% (Train: 96.8%, Val: 96.6%)", table_cell), Paragraph("\"A 0.2% generalization gap safely beats the 3.0% industry threshold.\"", table_cell)],
        [Paragraph("4", table_cell_bold), Paragraph("Isolation Forest", table_cell), Paragraph("200 trees, contamination=0.048", table_cell), Paragraph("\"Runs real Scikit-Learn IsolationForest in LiveIsolationForestPipeline in ~220ms.\"", table_cell)],
        [Paragraph("5", table_cell_bold), Paragraph("Mahalanobis Distance", table_cell), Paragraph("D_M = sqrt((x-mu)^T * pinv(Cov) * (x-mu))", table_cell), Paragraph("\"Normalizes correlated features using Moore-Penrose pseudoinverse np.linalg.pinv().\"", table_cell)],
        [Paragraph("6", table_cell_bold), Paragraph("PageRank vs Betweenness", table_cell), Paragraph("PageRank: PR(u); Betweenness: g(v)", table_cell), Paragraph("\"PageRank exposes the boss; Betweenness exposes the financial bridge/courier.\"", table_cell)],
        [Paragraph("7", table_cell_bold), Paragraph("Cellular Accuracy", table_cell), Paragraph("±12.4m = GDOP(1.14) * 10.8m", table_cell), Paragraph("\"A theoretical simulated covariance bound, NOT a field drive-test result.\"", table_cell)],
        [Paragraph("8", table_cell_bold), Paragraph("Benford's Law", table_cell), Paragraph("Chi-Square = 41.22 vs 15.51 (df=8)", table_cell), Paragraph("\"Proves statistical accounting manipulation with 99.1% confidence, not legal guilt.\"", table_cell)],
        [Paragraph("9", table_cell_bold), Paragraph("Section 63 BSA Law", table_cell), Paragraph("SHA-256 Binary Merkle Root", table_cell), Paragraph("\"Establishes post-ingestion technical integrity; court determines search legality.\"", table_cell)],
        [Paragraph("10", table_cell_bold), Paragraph("Responsible AI", table_cell), Paragraph("HITL advisory review + audit log", table_cell), Paragraph("\"Strictly advisory alerts requiring signed badge review; zero autonomous action.\"", table_cell)]
    ]
    t_recap_final = Table(ten_recap_data, colWidths=[printable_width*0.06, printable_width*0.24, printable_width*0.32, printable_width*0.38])
    t_recap_final.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_recap_final)
    story.append(Spacer(1, 6))

    final_callout = Paragraph(
        "<b>🎓 FINAL VERIFICATION CHECKLIST BEFORE ENTERING THE PANEL:</b><br/>"
        "• To show the ML model: Open <code>backend/app/main.py</code> line 2100.<br/>"
        "• To run the benchmark live: Run <code>python backend/scripts/run_offline_benchmark.py</code>.<br/>"
        "• To run automated tests: Run <code>python -m pytest backend/tests/test_responsible_ai.py -v</code> (17/17 pass in 2.02s).<br/>"
        "• To open the live web app: Visit <font color='#0284C7'>https://crimenet-ai-two.vercel.app</font>.<br/>"
        "• Golden Rule: Speak in simple English first. Explain the forensic intuition, state the math formula, and cite the file path.",
        body_txt
    )
    t_fc = Table([[final_callout]], colWidths=[printable_width])
    t_fc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ECFDF5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#10B981')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_fc)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Complete 400+ Interview Defense PDF successfully compiled at: {PDF_OUTPUT_PATH}")

if __name__ == '__main__':
    build_pdf()
