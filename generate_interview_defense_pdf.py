import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = os.path.normpath(r"c:\Users\Aditya\Downloads\SIH 2026\CrimeNet_AI_Interview_Defense_Master_Guide.pdf")

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that adds running headers and dynamic 'Page X of Y' footers.
    """
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
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header on all pages after page 1
        if self._pageNumber > 1:
            self.drawString(36, A4[1] - 28, "CRIMENET AI — MASTER TECHNICAL INTERVIEW & VIVA MANUAL")
            self.drawRightString(A4[0] - 36, A4[1] - 28, "DEFENSE & ENGINEERING DIRECTORY")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, A4[1] - 32, A4[0] - 36, A4[1] - 32)
            
        # Running Footer
        self.setFont("Helvetica", 8)
        self.drawString(36, 24, "CrimeNet AI Technical Defense Manual • Simple English & Mathematical Proofs")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 36, 24, page_text)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 34, A4[0] - 36, 34)
        
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )
    printable_width = A4[0] - 72

    styles = getSampleStyleSheet()
    
    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#0284C7'),
        spaceAfter=10
    )
    module_h1 = ParagraphStyle(
        'ModuleH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    q_title_style = ParagraphStyle(
        'QTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0369A1'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=3
    )
    spoken_style = ParagraphStyle(
        'SpokenText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor('#0F172A')
    )
    code_box_style = ParagraphStyle(
        'CodeBox',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor('#0F172A')
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1E293B')
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0F172A')
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []

    def make_callout(text, bg='#F0F9FF', border='#0284C7', title=""):
        content = []
        if title:
            content.append(Paragraph(f"<b>{title}</b>", ParagraphStyle('CTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor(border), spaceAfter=2)))
        content.append(Paragraph(text, body_style))
        t = Table([[content]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg)),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border)),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 7),
            ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ]))
        return t

    def make_spoken_card(spoken_text, simple_concept, math_formula="", code_ref=""):
        items = []
        items.append(Paragraph(f"<b>🗣️ Spoken Interview Answer (Simple English):</b><br/>\"{spoken_text}\"", spoken_style))
        items.append(Spacer(1, 3))
        items.append(Paragraph(f"<b>💡 Simple Intuition (Why this makes sense):</b> {simple_concept}", body_style))
        if math_formula:
            items.append(Spacer(1, 2))
            items.append(Paragraph(f"<b>🔬 Technical Formula / Logic:</b> <font face='Courier' size='7.5'>{math_formula}</font>", body_style))
        if code_ref:
            items.append(Spacer(1, 2))
            items.append(Paragraph(f"<b>📂 Exact Code Reference:</b> <font color='#0284C7'>{code_ref}</font>", body_style))
        
        t = Table([[items]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#94A3B8')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 7),
            ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ]))
        return t

    def make_diagram_box(diagram_ascii, caption):
        p_diag = Paragraph(diagram_ascii.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_box_style)
        p_cap = Paragraph(f"<b>Whiteboard Diagram to Sketch:</b> <i>{caption}</i>", ParagraphStyle('Cap', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.8, leading=10, textColor=colors.HexColor('#0369A1'), spaceBefore=2))
        t = Table([[ [p_diag, p_cap] ]], colWidths=[printable_width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 7),
            ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ]))
        return t

    def make_topic_summary(must_memorize, trap_questions, code_checks, whiteboard_note, rapid_sentence):
        rows = [
            [Paragraph("<b>Category</b>", table_header), Paragraph("<b>Key Takeaways & Quick Review Points</b>", table_header)],
            [Paragraph("<b>3 Must-Memorize Points</b>", table_cell_bold), Paragraph("<br/>".join([f"• {m}" for m in must_memorize]), table_cell)],
            [Paragraph("<b>3 Trap Questions</b>", table_cell_bold), Paragraph("<br/>".join([f"⚠️ {t}" for t in trap_questions]), table_cell)],
            [Paragraph("<b>3 Code Inspection Targets</b>", table_cell_bold), Paragraph("<br/>".join([f"🔍 {c}" for c in code_checks]), table_cell)],
            [Paragraph("<b>Whiteboard Diagram</b>", table_cell_bold), Paragraph(whiteboard_note, table_cell)],
            [Paragraph("<b>1-Sentence Rapid Response</b>", table_cell_bold), Paragraph(f"<i>\"{rapid_sentence}\"</i>", table_cell)]
        ]
        t = Table(rows, colWidths=[printable_width*0.25, printable_width*0.75])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        return t

    # ══════════════════════════════════════════════════════════════════════
    # COVER / HEADER BANNER
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("CRIMENET AI — MASTER INTERVIEW & VIVA DEFENSE MANUAL", title_style))
    story.append(Paragraph("Complete Technical Question-by-Question Guide, Mathematical Proofs, Whiteboard Sketches & Simple-English Answers", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=1, spaceAfter=6))

    meta_info = [
        [
            Paragraph("<b>Developer:</b> Aditya Pawar", table_cell),
            Paragraph("<b>Role:</b> Full-Stack & AI/ML Engineer", table_cell),
            Paragraph("<b>Core Stack:</b> React 19, FastAPI, NetworkX, SQLite", table_cell)
        ],
        [
            Paragraph("<b>Live Demo:</b> <font color='#0284C7'>crimenet-ai-two.vercel.app</font>", table_cell),
            Paragraph("<b>Benchmark:</b> NCFB-2026 (10,000 synthetic rows)", table_cell),
            Paragraph("<b>Evaluation:</b> 96.7% Precision (5-Fold Stratified CV)", table_cell)
        ]
    ]
    t_meta = Table(meta_info, colWidths=[printable_width*0.35, printable_width*0.35, printable_width*0.3])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 6))

    story.append(make_callout(
        "<b>CRITICAL CANDIDATE GROUND RULES FOR THE ENTIRE INTERVIEW:</b><br/>"
        "1. <b>Never claim synthetic data is real police data:</b> Real telecom intercepts and bank logs are legally protected by the DPDP Act 2023 and Section 5(2) Indian Telegraph Act.<br/>"
        "2. <b>Never claim 96.7% precision is guaranteed in real-world production:</b> State clearly that 96.7% is the measured precision on our synthetic NCFB-2026 offline benchmark.<br/>"
        "3. <b>Isolation Forest is unsupervised during training:</b> The model trains with zero labels; benchmark ground-truth labels are only used as an evaluation oracle.<br/>"
        "4. <b>±12.4m is a theoretical geometric covariance uncertainty radius:</b> Derived from Hata path loss and GDOP 1.14, NOT an empirical field drive-test measurement.<br/>"
        "5. <b>Merkle trees establish technical data integrity post-ingestion:</b> Final court admissibility requires valid judicial search warrants.<br/>"
        "6. <b>Zero autonomous enforcement:</b> CrimeNet AI generates advisory alerts for human badge confirmation; it never arrests or freezes accounts autonomously.",
        bg='#FEF2F2',
        border='#EF4444',
        title="⚠️ CANDIDATE INTEGRITY & TRAP PROTECTION RULES"
    ))
    story.append(Spacer(1, 6))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 1: PROJECT & PROBLEM STATEMENT
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 1 — PROJECT OVERVIEW & PROBLEM STATEMENT", module_h1))
    
    story.append(Paragraph("Q1. What is CrimeNet AI and what problem does it solve?", q_title_style))
    story.append(make_spoken_card(
        "CrimeNet AI is a cyber-forensic decision-support platform that unifies four disconnected investigative data streams—telecom Call Detail Records, hawala banking transactions, highway toll cameras, and dark-web intercepts—into an interactive 48-node knowledge graph. It solves the massive problem of investigative data silos where officers spend months manually cross-referencing spreadsheets to uncover syndicate kingpins and laundering loops.",
        "Think of a jigsaw puzzle where the police department has 10 pieces, the bank has 10 pieces, and highway toll cameras have 10 pieces. CrimeNet AI puts all 30 pieces on one table and connects them using graph theory and anomaly detection.",
        code_ref="backend/app/main.py: startup_event(), synthetic graph initialization"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q2. What is your 30-second and 1-minute elevator pitch?", q_title_style))
    story.append(make_spoken_card(
        "30-Second Pitch: In organized crime, kingpins never carry contraband or transfer money in their own name. They hide behind layers of burner SIMs and mule accounts. I built CrimeNet AI to fuse multi-sensor logs into an interactive knowledge graph. Using NetworkX PageRank, tuned Isolation Forest anomaly detection with 96.7% precision on our 10k benchmark, and 3-tower radio trilateration, it detects syndicate leaders and circular Hawala smurfing in seconds, locking evidence with SHA-256 Merkle trees compliant with Section 63 BSA 2023.",
        "For a 1-minute pitch, add the decoupled architecture (React 19, TypeScript, FastAPI) and the Human-In-The-Loop advisory review model with zero autonomous enforcement."
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q3. How do you explain the project WITHOUT using the word 'AI'?", q_title_style))
    story.append(make_spoken_card(
        "CrimeNet AI is a forensic data fusion platform. It converts tabular telecom logs and banking transactions into a mathematical relational network. It applies graph matrix algorithms—specifically PageRank and Betweenness Centrality—to uncover hidden hub entities, uses statistical tree partitioning and Mahalanobis distance to flag statistical transaction outliers, solves non-linear radio path-loss equations across cell towers to approximate burner phone coordinates, and generates cryptographically signed tamper-proof evidence records.",
        "Strip away the buzzwords: it is pure discrete mathematics, linear algebra, graph theory, and cryptographic hashing."
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q4. Is this a real production police system, and does it use real police data?", q_title_style))
    story.append(make_spoken_card(
        "No. CrimeNet AI is a high-fidelity investigative decision-support prototype and research benchmark platform. It does NOT use real citizen police intercepts. Under Section 5(2) of the Indian Telegraph Act, the Digital Personal Data Protection (DPDP) Act 2023, and commercial banking secrecy statutes, releasing actual citizen CDRs or bank account records in an open repository is strictly illegal. We evaluated on our synthetic National Cyber Forensic Benchmark (NCFB-2026), calibrated against log-normal transaction and power-law telecom distributions.",
        "Never pretend you have secret access to police databases. Interviewers will respect your understanding of statutory privacy laws.",
        code_ref="backend/data/ncfb_2026_benchmark_10k.csv"
    ))
    story.append(Spacer(1, 4))

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
    story.append(make_diagram_box(diag_arch, "CrimeNet AI 5-Tier Decoupled Architecture"))
    story.append(Spacer(1, 4))

    story.append(make_topic_summary(
        must_memorize=[
            "CrimeNet AI fuses 4 silos (CDR, banking, toll cameras, dark web) into a 48-node knowledge graph.",
            "It is a research/decision-support prototype, not a live production police system.",
            "Real police intercepts cannot be legally distributed due to DPDP Act 2023 & Telegraph Act."
        ],
        trap_questions=[
            "Did you test this on real criminals? -> No, tested on our synthetic NCFB-2026 benchmark.",
            "Can this AI arrest someone? -> No, zero autonomous enforcement; strictly advisory HITL review.",
            "What is the single biggest limitation? -> Requires digitized structured sensor inputs; cannot parse handwritten diary logs."
        ],
        code_checks=[
            "backend/app/main.py: Startup event & graph initialization",
            "backend/data/ncfb_2026_benchmark_10k.csv: 10,000 synthetic rows",
            "src/App.tsx: React 19 single-page dashboard routing"
        ],
        whiteboard_note="Draw the 3 boxes: Ingestion Silos -> Knowledge Graph & Math Engines -> Advisory Alert HUD.",
        rapid_sentence="CrimeNet AI connects multi-sensor investigative silos into an interactive graph to uncover syndicate leaders and Hawala loops in seconds."
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 2: SYSTEM ARCHITECTURE & TECHNOLOGY STACK
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 2 — SYSTEM ARCHITECTURE & TECHNOLOGY SELECTION", module_h1))

    tech_table_data = [
        [Paragraph("Component", table_header), Paragraph("Why Selected for CrimeNet AI", table_header), Paragraph("Alternative Considered", table_header), Paragraph("Why Rejected", table_header)],
        [Paragraph("React 19 + TypeScript", table_cell_bold), Paragraph("Strict type contracts across 48 graph nodes & schemas; prevents UI runtime crashes.", table_cell), Paragraph("Vanilla JS / Angular", table_cell), Paragraph("Vanilla JS lacks type safety; Angular is heavyweight and sluggish for canvas HUDs.", table_cell)],
        [Paragraph("Vite 8", table_cell_bold), Paragraph("Lightning-fast Hot Module Replacement and 417ms production build rollups.", table_cell), Paragraph("Webpack / CRA", table_cell), Paragraph("Webpack builds take 30-60s; Create-React-App is deprecated.", table_cell)],
        [Paragraph("FastAPI (Python 3.14)", table_cell_bold), Paragraph("High-throughput ASGI async loop, native Pydantic validation, direct access to NumPy & NetworkX.", table_cell), Paragraph("Flask / Django", table_cell), Paragraph("Flask lacks async by default; Django is monolithic and bloated.", table_cell)],
        [Paragraph("SQLite3", table_cell_bold), Paragraph("Zero-configuration embedded ACID storage; zero socket latency for local forensic appliances.", table_cell), Paragraph("PostgreSQL", table_cell), Paragraph("Postgres requires background daemon orchestration; SQLite delivers zero-latency local queries.", table_cell)],
        [Paragraph("NetworkX", table_cell_bold), Paragraph("Scientific, deterministic implementation of PageRank, Betweenness, and Johnson's cycles.", table_cell), Paragraph("Neo4j", table_cell), Paragraph("Neo4j requires JVM overhead and complex Cypher bridges; NetworkX operates purely in-memory.", table_cell)],
        [Paragraph("Cytoscape.js", table_cell_bold), Paragraph("Optimized HTML5 canvas graph engine supporting physics-based force-directed layouts (fcose).", table_cell), Paragraph("D3.js", table_cell), Paragraph("D3 requires building graph interaction primitives from scratch; Cytoscape gives turn-key link analysis.", table_cell)],
        [Paragraph("Mapbox GL", table_cell_bold), Paragraph("WebGL hardware-accelerated mapping for real-time ANPR toll radar and cellular tower heatmaps.", table_cell), Paragraph("Leaflet.js", table_cell), Paragraph("Leaflet uses DOM rendering which lags when rendering hundreds of geospatial coordinate rings.", table_cell)]
    ]
    t_tech = Table(tech_table_data, colWidths=[printable_width*0.2, printable_width*0.35, printable_width*0.2, printable_width*0.25])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Q. How would you scale this architecture to handle 50 million records?", q_title_style))
    story.append(make_spoken_card(
        "To scale to 50 million records: (1) Replace embedded SQLite with PostgreSQL or TimescaleDB for partition-indexed time-series CDR telemetry; (2) Migrate the in-memory graph to a distributed graph cluster like Neo4j or Amazon Neptune; (3) Ingest streaming telecommunications data via Apache Kafka; and (4) Decouple the ML inference engine into an asynchronous Celery/Redis worker cluster.",
        "Right now, an in-memory graph holds 48 nodes in RAM. At 50 million nodes, RAM explodes, so you must use disk-backed graph partitions and streaming queues."
    ))
    story.append(Spacer(1, 4))

    story.append(make_topic_summary(
        must_memorize=[
            "FastAPI was chosen for native async loop and seamless interoperability with Python scientific libraries (NumPy, NetworkX, Scikit-Learn).",
            "Cytoscape.js runs hardware-accelerated HTML5 canvas rendering using the physics-based fcose layout.",
            "SQLite provides zero-config embedded storage for the standalone prototype."
        ],
        trap_questions=[
            "Why not microservices? -> Over-engineering for an MVP; introduces network latency and distributed transaction complexity.",
            "What happens if the backend goes down? -> React frontend catches Axios errors and presents an offline status banner.",
            "Why not PostgreSQL? -> SQLite requires zero daemon configuration on a forensic field laptop."
        ],
        code_checks=[
            "backend/app/main.py: FastAPI app instantiation and CORS middleware",
            "src/components/NetworkGraph.tsx: Cytoscape initialization and stylesheet",
            "package.json: React 19, Cytoscape, Mapbox GL dependencies"
        ],
        whiteboard_note="Draw: Client (React/Cytoscape) --[REST/JSON]--> FastAPI --[In-Memory NetworkX / Scikit-Learn] + SQLite.",
        rapid_sentence="We decoupled a high-performance React 19 canvas HUD from an asynchronous FastAPI Python engine for sub-second graph analytics."
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 3: KNOWLEDGE GRAPH THEORY & GRAPH ALGORITHMS
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 3 — KNOWLEDGE GRAPH THEORY & GRAPH ALGORITHMS", module_h1))

    story.append(Paragraph("Q1. What is a Knowledge Graph, and why use it instead of relational SQL tables?", q_title_style))
    story.append(make_spoken_card(
        "A knowledge graph is a network of real-world entities (nodes) connected by meaningful relationships (directed edges). In relational SQL, discovering a multi-hop proxy link between a kingpin and an operative requires 5 to 7 expensive JOIN operations across massive tables, resulting in polynomial query degradation. In a graph, relationships are first-class citizens stored as adjacency pointers, enabling constant-time pointer chasing and O(V + E) traversals regardless of total database size.",
        "In SQL, finding who called who who paid who requires joining 5 huge tables. In a graph, you just walk along the lines connecting the dots."
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q2. How does PageRank work, and why does it expose syndicate kingpins?", q_title_style))
    story.append(make_spoken_card(
        "PageRank measures the structural authority of a node based on the quality and quantity of incoming links. We use a damping factor of d=0.85, solved via Power Iteration (converged in 16 iterations). In organized syndicates, the boss (e.g. Arjun Mehta) never calls low-level operatives; he only communicates with a few high-level lieutenants. Because those lieutenants possess immense network connectivity, their incoming links confer overwhelming authority onto the kingpin, driving his PageRank to the top of the leaderboard (0.081).",
        "It's like voting: if a regular person votes for you, it's worth 1 point. If the Prime Minister votes for you, it's worth 1,000 points. The kingpin gets votes from the most powerful lieutenants.",
        math_formula="PR(u) = (1 - d)/N + d * sum_{v in B_u} (PR(v) / L(v))  [where d = 0.85]",
        code_ref="backend/app/main.py: nx.pagerank(G, alpha=0.85, tol=1e-6)"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q3. What is Betweenness Centrality, and how is it calculated (Brandes' Algorithm)?", q_title_style))
    story.append(make_spoken_card(
        "Betweenness Centrality measures how often a node falls on the shortest path between all pairs of other nodes in the network. We compute it using Brandes' Algorithm in O(V * E) time. While PageRank exposes the boss, Betweenness Centrality exposes the financial bridges and couriers—like Hawala broker Mohammed Rafiq—who link otherwise disconnected criminal cliques. Severing high-betweenness nodes dismantles syndicate communications.",
        "Imagine two islands connected by only one bridge. Even if the bridge is small, all traffic must cross it. Betweenness finds that bridge.",
        math_formula="g(v) = sum_{s != v != t} (sigma_{st}(v) / sigma_{st})",
        code_ref="backend/app/main.py: nx.betweenness_centrality(G)"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q4. Dijkstra vs A* Shortest Path: How do they work in CrimeNet?", q_title_style))
    story.append(make_spoken_card(
        "Dijkstra finds the shortest path between two nodes in a non-negative weighted graph in O((V + E) log V) using a min-priority queue. A* enhances Dijkstra by incorporating a heuristic function h(n): f(n) = g(n) + h(n). If the heuristic is admissible (never overestimates distance), A* is guaranteed to find the optimal path while exploring significantly fewer nodes. In CrimeNet, we use Dijkstra to trace exact proxy communication chains between suspects.",
        "Dijkstra searches in all directions equally like ripples in a pond. A* points a flashlight towards the destination so it doesn't waste time searching in the wrong direction.",
        math_formula="f(n) = g(n) + h(n)  [g(n) = exact cost from start, h(n) = admissible heuristic]",
        code_ref="backend/app/main.py: nx.shortest_path(G, source, target, weight='weight')"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q5. What is Johnson's Elementary Cycles Algorithm, and how does it detect Hawala laundering?", q_title_style))
    story.append(make_spoken_card(
        "Johnson's algorithm finds all simple directed cycles in a graph in O((V + E)(C + 1)) time using depth-first search with an unblocking mechanism. Hawala operators often launder dirty money by structuring funds into sub-₹50,000 increments, routing them through mule accounts and offshore shell corporations, and cycling them back to the originator. Johnson's algorithm uncovers closed loops (e.g., Mehta -> Phoenix LLC -> Swiss Escrow -> Local Mule -> Mehta). However, a cycle alone does not prove money laundering; it indicates a circular financial topology that requires human corroboration.",
        "If you give money to Alice, Alice gives it to Bob, Bob gives it to Charlie, and Charlie gives it right back to you, that's a closed circle. Johnson's algorithm finds those circles.",
        code_ref="backend/app/main.py: nx.simple_cycles(G_financial)"
    ))
    story.append(Spacer(1, 4))

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
    story.append(make_diagram_box(diag_graph, "Syndicate Network Topology: Kingpin Authority vs Hawala Bridges"))
    story.append(Spacer(1, 4))

    story.append(make_topic_summary(
        must_memorize=[
            "PageRank formula uses damping factor d=0.85 and exposes the authoritative syndicate kingpins.",
            "Betweenness Centrality uses Brandes' Algorithm O(V*E) and exposes financial bridges and couriers.",
            "Johnson's Algorithm O((V+E)(C+1)) detects circular Hawala laundering topologies."
        ],
        trap_questions=[
            "Does high PageRank prove a suspect is guilty? -> No, it proves structural network authority, not guilt.",
            "Does a transaction cycle prove money laundering? -> No, legitimate refunds or escrows can form cycles; it requires investigation.",
            "Can Dijkstra handle negative edge weights? -> No, negative weights cause infinite loops; Bellman-Ford is needed for negative weights."
        ],
        code_checks=[
            "backend/app/main.py: nx.pagerank(G, alpha=0.85)",
            "backend/app/main.py: nx.betweenness_centrality(G)",
            "backend/app/main.py: nx.simple_cycles(G_financial)"
        ],
        whiteboard_note="Draw Kingpin with few incoming arrows from highly-connected Lieutenants; draw Broker bridging two separate clusters.",
        rapid_sentence="We apply PageRank to detect syndicate bosses and Betweenness Centrality to pinpoint financial bridge couriers."
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 4: MACHINE LEARNING & STATISTICAL ANOMALY ENGINE
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 4 — MACHINE LEARNING & STATISTICAL ANOMALY ENGINE", module_h1))

    story.append(Paragraph("Q1. What ML algorithm is used, and how does Isolation Forest actually isolate anomalies?", q_title_style))
    story.append(make_spoken_card(
        "We use an Isolation Forest ensemble combined with Mahalanobis statistical distance. Isolation Forest works on the principle that anomalies are 'few and different'. An isolation tree recursively selects a random feature and a random split value between the min and max. Normal inlier points reside in dense clusters and require many cuts to isolate, resulting in deep tree path lengths. Anomalies exist in sparse regions and get isolated near the root of the tree with short path lengths. The anomaly score is: s(x, n) = 2^(- E(h(x)) / c(n)).",
        "If you want to cut a lone tree in an open field, one slice of the mower isolates it. If you want to cut a specific tree in a dense forest, you have to make 50 cuts. Anomalies are cut out in 2 or 3 slices.",
        math_formula="s(x, n) = 2^{- E(h(x)) / c(n)}, where c(n) = 2 ln(n - 1) + 0.5772156649 - (2(n - 1)/n)",
        code_ref="backend/app/main.py: class LiveIsolationForestPipeline (lines 2100-2180)"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q2. Is your Isolation Forest actually running live, or is it hardcoded?", q_title_style))
    story.append(make_spoken_card(
        "It is 100% running live code. We implemented `LiveIsolationForestPipeline` in `backend/app/main.py`. It imports `sklearn.ensemble.IsolationForest` and instantiates 200 trees (`n_estimators=200`, `contamination=0.048`). On startup or via `POST /api/models/train-live`, it builds a 5D feature matrix, calls `.fit(X)`, computes continuous anomaly scores via `.decision_function(X)`, and computes Mahalanobis distance by inverting the covariance matrix with `np.linalg.pinv()`. Live status can be inspected at `GET /api/models/live-status`.",
        "You can open `backend/app/main.py` lines 2100-2180 and trigger `POST /api/models/train-live` in Postman; it will return the real elapsed milliseconds (~220ms).",
        code_ref="backend/app/main.py: /api/models/train-live & /api/models/live-status"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q3. What is Mahalanobis Distance, and why invert the covariance matrix with np.linalg.pinv()?", q_title_style))
    story.append(make_spoken_card(
        "Mahalanobis distance measures the distance between a point x and a multi-dimensional distribution mean mu, accounting for feature correlations and variance. Euclidean distance assumes all features are spherical and uncorrelated. In financial crime, transfer amount and transaction velocity are highly correlated; Euclidean distance creates severe false alarms. We invert the covariance matrix Sigma to normalize variance along the principal axes. We use Moore-Penrose pseudoinverse `np.linalg.pinv()` because if two features are collinear, the covariance matrix is singular (determinant zero) and standard inversion crashes.",
        "If you measure height in inches and weight in pounds, Euclidean distance is distorted. Mahalanobis stretches and rotates the ruler to fit the correlation shape.",
        math_formula="D_M(x) = sqrt((x - mu)^T * Sigma^{-1} * (x - mu))",
        code_ref="backend/app/main.py: np.linalg.pinv(self.cov_matrix)"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q4. What are the 5 feature dimensions used by the model?", q_title_style))
    
    feat_table_data = [
        [Paragraph("Feature Dimension", table_header), Paragraph("Mathematical Definition", table_header), Paragraph("Forensic Significance", table_header)],
        [Paragraph("1. Log Financial Amount", table_cell_bold), Paragraph("log10(Amount + 1)", table_cell), Paragraph("Compresses heavy-tailed financial distributions; highlights extreme value spikes without outlier blowout.", table_cell)],
        [Paragraph("2. Nocturnal Activity Ratio", table_cell_bold), Paragraph("Calls between 02:00-05:00 / Total Calls", table_cell), Paragraph("Legitimate business calls occur during daylight; syndicates concentrate burner SIM chatter in dead of night.", table_cell)],
        [Paragraph("3. Kinematic Speed Velocity", table_cell_bold), Paragraph("Distance / Time between toll plazas (km/h)", table_cell), Paragraph("Identifies physically impossible transit speeds or reckless courier convoy transits (>130 km/h).", table_cell)],
        [Paragraph("4. Degree Centrality", table_cell_bold), Paragraph("In_Degree + Out_Degree / (N - 1)", table_cell), Paragraph("Measures direct operational fanout and communication volume across the 48-node syndicate graph.", table_cell)],
        [Paragraph("5. Rapid Fanout Rate", table_cell_bold), Paragraph("Outbound Transfers in 60 mins / Baseline", table_cell), Paragraph("Detects smurfing behavior where incoming dirty deposits are immediately dispersed across mule tranches.", table_cell)]
    ]
    t_feat = Table(feat_table_data, colWidths=[printable_width*0.25, printable_width*0.35, printable_width*0.4])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 4))

    story.append(make_topic_summary(
        must_memorize=[
            "Isolation Forest isolates anomalies near the root with short path lengths: s(x,n) = 2^(-E(h)/c(n)).",
            "Model parameters: n_estimators=200, contamination=0.048, random_state=42.",
            "Mahalanobis distance uses Moore-Penrose pseudoinverse np.linalg.pinv() to prevent singular matrix crashes."
        ],
        trap_questions=[
            "Is Mahalanobis distance inside Isolation Forest? -> No, it is a separate statistical scoring component run in parallel.",
            "What does predict() return? -> -1 for an anomaly, +1 for a normal inlier.",
            "Why not use an Autoencoder or Deep Learning? -> Deep learning is unexplainable in court; Isolation Forest gives transparent path-length scoring."
        ],
        code_checks=[
            "backend/app/main.py: LiveIsolationForestPipeline class",
            "backend/app/main.py: .fit(X) and .decision_function(X)",
            "backend/app/main.py: np.linalg.pinv(cov) calculation"
        ],
        whiteboard_note="Draw an Isolation Tree showing an anomaly isolated at depth 2 while normal points require depth 12.",
        rapid_sentence="We combine Scikit-Learn Isolation Forest (200 trees) with Mahalanobis covariance distance to isolate multi-dimensional forensic anomalies."
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 5: TELECOM POSITIONING, KINEMATICS & BENFORD'S LAW
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 5 — TELECOM POSITIONING, KINEMATICS & BENFORD'S LAW", module_h1))

    story.append(Paragraph("Q1. How does cellular trilateration work without GPS, and what does ±12.4m mean?", q_title_style))
    story.append(make_spoken_card(
        "We model urban radio signal propagation using the Hata empirical path-loss equation: Pr(d) = Pt - 10*gamma*log10(d) + X_sigma with urban exponent gamma=2.8. Given RSSI from 3 cell towers, we solve the non-linear distance intersection using Weighted Least Squares (WLS), weighting towers by signal-to-noise ratio. The Jacobian matrix yields a Geometric Dilution of Precision (GDOP) of 1.14. Multiplying GDOP by our baseline ranging error (10.8m) gives a theoretical covariance uncertainty radius of ±12.4 meters. Crucially, this is a simulated theoretical bound under line-of-sight assumptions, NOT a field drive-test measurement.",
        "Triangulation uses angles; trilateration uses distances. Three circles drawn around three cell towers overlap in a small region. That overlap is our location estimate.",
        math_formula="delta_x = (J^T * W * J)^{-1} * J^T * W * delta_r;  sigma_{pos} = GDOP * sigma_{range} = 1.14 * 10.8m = ±12.4m",
        code_ref="backend/app/main.py: WLS trilateration solver (lines 2975-3050)"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q2. How does the 2D Kalman Filter track suspect vehicles across toll plazas?", q_title_style))
    story.append(make_spoken_card(
        "We implement a 2D Linear Kalman Filter modeling vehicle state vectors: x_k = [x, y, vx, vy]^T. The prediction step projects vehicle position based on physical motion equations: x_pred = F * x + B * u, P_pred = F * P * F^T + Q. When the vehicle triggers an ANPR toll camera, the measurement update step calculates the Kalman Gain K = P_pred * H^T * (H * P_pred * H^T + R)^(-1) to balance noisy camera timestamps against kinematic momentum, outputting smoothed coordinates and arrival time predictions at downstream toll checkpoints.",
        "A car can't teleport or make a 90-degree turn at 120 km/h. The Kalman filter uses physics to guess where the car is even when between cameras.",
        math_formula="K_k = P_k^- * H^T * (H * P_k^- * H^T + R)^{-1};  x_k = x_k^- + K_k * (z_k - H * x_k^-)",
        code_ref="backend/app/main.py: class KalmanFilter2D (lines 2780-2840)"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q3. What is Benford's Law, and how does Chi-Square testing flag fabricated accounting?", q_title_style))
    story.append(make_spoken_card(
        "Benford's Law states that in natural financial records, the number 1 appears as the first digit 30.1% of the time, while 9 appears only 4.6% of the time: P(d) = log10(1 + 1/d). Human fraudsters who invent false wire transfers distribute first digits uniformly. We compute Pearson's Chi-Square statistic: chi^2 = sum((O_i - E_i)^2 / E_i). In our hawala ledger, the observed chi^2 is 41.22 against the critical threshold of 15.51 (degrees of freedom = 8, p < 0.001). This proves 99.1% statistical confidence of manipulated accounting. However, Benford's Law flags a statistical anomaly; it does not independently prove criminal guilt.",
        "If someone rolls a die 1,000 times and gets a 6 half the time, the die is loaded. If financial logs don't follow Benford's 30% curve, someone made up the numbers.",
        math_formula="P(d) = log_{10}(1 + 1/d);  chi^2 = sum_{d=1}^9 ((O_d - E_d)^2 / E_d) = 41.22  [Critical = 15.51, df=8]",
        code_ref="backend/app/main.py: Benford Chi-Square validator (lines 1220-1275)"
    ))
    story.append(Spacer(1, 4))

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
    story.append(make_diagram_box(diag_trilat, "3-Tower Weighted Least Squares Trilateration Intersection"))
    story.append(Spacer(1, 4))

    story.append(make_topic_summary(
        must_memorize=[
            "Trilateration uses distance circles from 3 towers; triangulation uses angles of arrival.",
            "±12.4m accuracy is a simulated theoretical uncertainty bound (GDOP 1.14 * 10.8m), not a real-world drive test.",
            "Benford's Law chi-square = 41.22 rejects natural distribution with p < 0.001 (critical threshold 15.51)."
        ],
        trap_questions=[
            "Did you drive around Mumbai with an antenna to test ±12.4m? -> No, it is a theoretical covariance bound under simulated Hata path loss.",
            "Does failing Benford's Law prove money laundering? -> No, it indicates fabricated numbers; human corroboration is mandatory.",
            "What causes radio positioning error in reality? -> Non-Line-of-Sight (NLOS) shadowing and urban multipath reflections."
        ],
        code_checks=[
            "backend/app/main.py: Hata path loss formula & WLS Jacobian solver",
            "backend/app/main.py: KalmanFilter2D state prediction and update",
            "backend/app/main.py: Benford distribution chi-square calculation"
        ],
        whiteboard_note="Draw 3 intersecting circles with radii r1, r2, r3 and a central uncertainty ellipse marked GDOP=1.14.",
        rapid_sentence="We apply WLS trilateration to estimate burner phone locations and Benford Chi-Square analysis to flag fabricated Hawala ledgers."
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 6: BENCHMARK DATASET, 5-FOLD CV & THE UNSUPERVISED TRAP
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 6 — BENCHMARK DATASET, 5-FOLD CV & THE UNSUPERVISED TRAP", module_h1))

    story.append(Paragraph("Q1. What is NCFB-2026, and where did the 96.7% precision come from?", q_title_style))
    story.append(make_spoken_card(
        "NCFB-2026 is our synthetic CrimeNet AI forensic benchmark, stored at `backend/data/ncfb_2026_benchmark_10k.csv` (10,000 rows, 5 features, 480 anomalies). We evaluated it via 5-Fold Stratified Cross-Validation using `backend/scripts/run_offline_benchmark.py`. The resulting confusion matrix is: TP=464, FP=16, FN=16, TN=9504. Precision = 464 / (464 + 16) = 96.67% (96.7%). Recall = 464 / (464 + 16) = 96.67% (96.7%). F1-Score = 0.967, and ROC-AUC = 0.998.",
        "Precision means: when our system screams 'Anomaly!', 96.7% of the time it is a real threat, meaning officers waste almost zero time on false alarms.",
        math_formula="Precision = TP / (TP + FP) = 464 / (464 + 16) = 96.67%;  Recall = TP / (TP + FN) = 464 / (464 + 16) = 96.67%",
        code_ref="backend/data/ncfb_2026_benchmark_10k.csv & backend/scripts/run_offline_benchmark.py"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q2. How do you mathematically prove your model isn't overfitting?", q_title_style))
    story.append(make_spoken_card(
        "We prove generalization through 5-Fold Stratified Cross-Validation. Across the 5 folds, training F1 averaged 96.8% while validation F1 averaged 96.6%. The Generalization Gap is exactly 0.2%, well below the industry 3.0% threshold. The individual fold F1 scores are [0.947, 0.958, 0.969, 0.979, 0.974] with minimal standard deviation (sigma = ±0.0115). This proves the model does not memorize training noise.",
        "Overfitting is like a student who memorizes test questions instead of learning the concept. If they pass new practice tests with the same score (0.2% gap), they actually learned the concept.",
        math_formula="Generalization Gap = |Train_F1 - Val_F1| = |96.8% - 96.6%| = 0.2%  (Standard Dev = ±0.0115)",
        code_ref="backend/data/ncfb_2026_cv_results.json"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q3. THE MASTER TRAP QUESTION: 'Isolation Forest is unsupervised, so how did you calculate Precision and Recall?'", q_title_style))
    story.append(make_spoken_card(
        "This is a crucial architectural distinction: the model trains completely unsupervised, but the evaluation uses ground-truth labels as an evaluation oracle. During `.fit(X)`, the model never sees, receives, or uses the `is_anomaly` labels. It isolates data points purely via recursive random splits. Only after `.predict(X)` produces predictions (-1 or +1) do we compare those outputs against our synthetic benchmark's held-out labels to calculate TP, FP, FN, TN, Precision, Recall, and F1. At no point do labels guide tree construction.",
        "Imagine grading a blind test. The student (model) takes the exam with zero answer keys. The teacher (evaluation oracle) uses the hidden answer key afterwards to calculate their percentage.",
        code_ref="backend/scripts/run_offline_benchmark.py (lines 80-140)"
    ))
    story.append(Spacer(1, 4))

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
    story.append(make_diagram_box(diag_eval, "Unsupervised Model Training vs Supervised Evaluation Oracle Pipeline"))
    story.append(Spacer(1, 4))

    story.append(make_topic_summary(
        must_memorize=[
            "NCFB-2026 contains exactly 10,000 synthetic rows, 5 features, and 480 anomalies (4.8% contamination).",
            "5-Fold Stratified CV results: TP=464, FP=16, FN=16, TN=9504; Precision = 96.7%, Recall = 96.7%, ROC-AUC = 0.998.",
            "Generalization gap is 0.2% (Train F1 96.8% vs Validation F1 96.6%)."
        ],
        trap_questions=[
            "Is NCFB-2026 an official police benchmark? -> No, it is our synthetic research benchmark generated for CrimeNet AI.",
            "Did the model train with labels? -> Absolutely not; training is strictly unsupervised. Labels are only an evaluation oracle.",
            "Why not use 10-fold CV? -> 5-fold preserves sufficient anomaly counts (96 per fold) without excessive variance."
        ],
        code_checks=[
            "backend/data/ncfb_2026_benchmark_10k.csv (10k rows)",
            "backend/scripts/run_offline_benchmark.py (StratifiedKFold execution)",
            "backend/data/ncfb_2026_cv_results.json (Fold metrics & generalization gap)"
        ],
        whiteboard_note="Draw 2x2 Confusion Matrix: Top row: TP=464, FP=16. Bottom row: FN=16, TN=9504. Precision = 464/(464+16) = 96.7%.",
        rapid_sentence="We validated our unsupervised Isolation Forest on our 10,000-row synthetic benchmark using 5-fold stratified CV, proving 96.7% precision with a 0.2% gap."
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 7: CYBERSECURITY, MERKLE LEDGER & LEGAL COMPLIANCE
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 7 — CYBERSECURITY, MERKLE TREES & SECTION 63 BSA LAW", module_h1))

    sec_table_data = [
        [Paragraph("Hardening Pillar", table_header), Paragraph("Standard / Cipher", table_header), Paragraph("Code Location", table_header), Paragraph("Vulnerability Mitigated", table_header)],
        [Paragraph("1. Password Hashing", table_cell_bold), Paragraph("PBKDF2-HMAC-SHA256 (100k iters)", table_cell), Paragraph("main.py: hash_password()", table_cell), Paragraph("Immunity to GPU rainbow tables & precomputation.", table_cell)],
        [Paragraph("2. Secret Management", table_cell_bold), Paragraph("Zero-hardcode .env Vault", table_cell), Paragraph(".env & python-dotenv", table_cell), Paragraph("Eliminates credential leaks in public code repositories.", table_cell)],
        [Paragraph("3. Token Lifecycle", table_cell_bold), Paragraph("15-Min JWT + 7-Day Refresh Rotation", table_cell), Paragraph("/api/auth/refresh-token", table_cell), Paragraph("Prevents replay attacks and session hijacking.", table_cell)],
        [Paragraph("4. Role-Based Access", table_cell_bold), Paragraph("4-Tier RBAC Hierarchy", table_cell), Paragraph("require_roles() guard", table_cell), Paragraph("Stops horizontal and vertical privilege escalation.", table_cell)],
        [Paragraph("5. PII Encryption", table_cell_bold), Paragraph("AES-256-GCM (96-bit Nonce)", table_cell), Paragraph("encrypt_pii() / decrypt()", table_cell), Paragraph("Guarantees data confidentiality & tamper detection at rest.", table_cell)],
        [Paragraph("6. Biometric Privacy", table_cell_bold), Paragraph("DPDP Act 30-Day Retention", table_cell), Paragraph("purge_expired_logs()", table_cell), Paragraph("Auto-purges intruder webcam captures older than 30 days.", table_cell)],
        [Paragraph("7. Benchmark Grounding", table_cell_bold), Paragraph("NCFB-2026 10k CSV Suite", table_cell), Paragraph("run_offline_benchmark.py", table_cell), Paragraph("Replaced ungrounded claims with reproducible benchmarks.", table_cell)]
    ]
    t_sec = Table(sec_table_data, colWidths=[printable_width*0.22, printable_width*0.28, printable_width*0.25, printable_width*0.25])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sec)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Q. How does the SHA-256 Merkle Tree work, and does it guarantee legal admissibility?", q_title_style))
    story.append(make_spoken_card(
        "A Merkle tree hierarchically hashes canonicalized evidence strings into leaf pairs, combining and re-hashing them up to a single 64-character Root Hash. Under Section 63 of Bharatiya Sakshya Adhiniyam (BSA) 2023, digital records require proof that electronic records were not altered post-ingestion. If an attacker edits a single digit in the SQLite database, the avalanche effect generates a completely different root hash, immediately proving tampering. However, a Merkle tree proves technical data integrity post-ingestion; it does NOT prove legality of collection. If police conducted an illegal wiretap without a Section 5(2) Telegraph Act warrant, a Merkle hash cannot make it admissible. CrimeNet explicitly prints this statutory limitation on all generated dossiers.",
        "A wax seal on an envelope proves no one opened the letter in transit. It does not prove the letter inside was legally obtained or true.",
        math_formula="H_{root} = SHA256(H_{AB} || H_{CD});  H_{AB} = SHA256(H_A || H_B)",
        code_ref="backend/app/main.py: build_merkle_tree() (lines 3240-3320)"
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Q. What happens if your AI flags an innocent person? (Responsible AI & HITL)", q_title_style))
    story.append(make_spoken_card(
        "CrimeNet AI enforces a strict Human-In-The-Loop (HITL) architecture with zero autonomous enforcement power. When an anomaly is detected, it enters the system purely as an Advisory Alert. The Alert Centre displays Explainable AI (XAI) feature baselines showing the investigator exactly why the anomaly was flagged. A human investigator with verified badge credentials must manually review the alert and click Confirm or Suppress with audit notes. Suppressed false alarms are permanently logged in SQLite and feed back into suppression thresholds. The system cannot arrest, freeze accounts, or accuse anyone autonomously.",
        "The AI is a metal detector, not an armed guard. When the metal detector beeps, a human officer still has to check whether it's a weapon or a belt buckle.",
        code_ref="backend/tests/test_responsible_ai.py: test_alerts_contain_advisory_status()"
    ))
    story.append(Spacer(1, 4))

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
    story.append(make_diagram_box(diag_merkle, "Binary SHA-256 Merkle Tree Evidence Ledger Architecture"))
    story.append(Spacer(1, 4))

    story.append(make_topic_summary(
        must_memorize=[
            "PBKDF2 uses 100,000 iterations of HMAC-SHA256 to stop GPU dictionary and rainbow-table cracking.",
            "SHA-256 Merkle tree proves post-ingestion technical data integrity under Section 63 BSA 2023.",
            "All AI alerts are strictly Advisory; human badge review is mandatory with immutable audit logs."
        ],
        trap_questions=[
            "Does a Merkle root hash prove evidence was lawfully collected? -> No, it proves tamper-evident storage, not search warrant legality.",
            "What if an attacker steals a JWT? -> JWT expires in 15 minutes; refresh tokens are rotated and invalidated on replay.",
            "Can AI freeze accounts autonomously? -> No, zero autonomous enforcement under our Responsible AI framework."
        ],
        code_checks=[
            "backend/app/main.py: hash_password() and verify_password()",
            "backend/app/main.py: build_merkle_tree()",
            "backend/tests/test_responsible_ai.py: 17 passing responsible AI tests"
        ],
        whiteboard_note="Draw Merkle Tree: 4 raw logs -> 4 Leaf Hashes -> 2 Parent Hashes -> 1 Merkle Root Hash.",
        rapid_sentence="We secure credentials with PBKDF2, encrypt PII with AES-256-GCM, and lock evidence in a SHA-256 Merkle tree with mandatory human badge signoff."
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 8: "SHOW ME THE CODE" DIRECTORY
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 8 — 'SHOW ME THE CODE' DIRECTORY (EXACT LOCATIONS)", module_h1))

    code_loc_data = [
        [Paragraph("Algorithm / Component", table_header), Paragraph("Exact File Path", table_header), Paragraph("Line Range", table_header), Paragraph("Key Function / Implementation Details", table_header)],
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
    t_code = Table(code_loc_data, colWidths=[printable_width*0.25, printable_width*0.35, printable_width*0.15, printable_width*0.25])
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
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 9: HOSTILE & SKEPTICAL INTERVIEW DEFENSE
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 9 — DEFENDING AGAINST HOSTILE & SKEPTICAL PANELS", module_h1))

    story.append(Paragraph("Hostile Trap 1: 'Isn't your project mostly just a fancy UI mockup?'", q_title_style))
    story.append(make_spoken_card(
        "No. While our UI is built with modern React 19 and Cytoscape.js for tactical usability, all intelligence is driven by verified mathematical engines in FastAPI. Under the hood, NetworkX runs deterministic Power Iteration for PageRank and Brandes' algorithm for Betweenness Centrality. Scikit-Learn fits 200 decision trees via a live Isolation Forest pipeline in ~220ms, combining with NumPy Mahalanobis distance covariance inversion. Telecom coordinates are derived through Weighted Least Squares normal equations. We have 17 passing pytests that strictly validate our backend logic with zero UI dependency.",
        "Don't get defensive. Pivot immediately to your verified algorithms, math equations, and passing pytests."
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Hostile Trap 2: 'Why did you use Isolation Forest instead of modern Deep Learning or a GNN?'", q_title_style))
    story.append(make_spoken_card(
        "In forensic decision-support, deep neural networks and Graph Neural Networks present two severe drawbacks: black-box unexplainability and extreme training data requirements. In court, an expert witness cannot present a 50-million-parameter black-box weight matrix; Section 63 BSA 2023 requires explainable electronic evidence. Isolation Forest provides transparent geometric tree partitioning that directly outputs path-length scores. Combined with NetworkX graph algorithms, it runs sub-second inference on standard police workstation CPUs without requiring multi-thousand-dollar GPU clusters.",
        "Simpler, explainable models that run on normal police laptops beat bloated deep-learning models every single day in law enforcement."
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Hostile Trap 3: 'What happens if your machine learning model is poisoned or completely wrong?'", q_title_style))
    story.append(make_spoken_card(
        "CrimeNet AI's architecture is resilient against model failure because the ML model is strictly an advisory signal, never a single point of failure. The knowledge graph operates independently using deterministic NetworkX graph theory (PageRank and Betweenness Centrality) that does not depend on ML weights. In addition, financial smurfing detection uses deterministic Johnson's cycles and Benford's Law Chi-Square math. Even if the ML pipeline were completely disabled, investigators would still uncover kingpins, laundering loops, and vehicle transits through deterministic mathematics. Finally, every alert requires human badge confirmation.",
        "CrimeNet has defense-in-depth: if ML fails, graph theory catches it. If graph theory fails, Benford's Law catches it. And a human officer makes the final call."
    ))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Hostile Trap 4: 'What was your personal contribution versus AI code generation?'", q_title_style))
    story.append(make_spoken_card(
        "I personally architected the full-stack system design, selected the mathematical formulas (Hata path loss, WLS normal equations, Mahalanobis covariance inversion, Brandes betweenness, and Merkle tree hashing), designed the 4-tier RBAC authorization model, engineered the 17 automated pytest test suites, and deployed the production stack on Vercel and Render. I used AI coding tools for rapid syntax scaffolding and boilerplate typing, but every algorithmic formulation, legal boundary, and architectural decision was designed and verified by me.",
        "Be honest and confident: senior engineers use tools, but only strong engineers understand the underlying math, architecture, and legal standards."
    ))
    story.append(Spacer(1, 4))

    story.append(make_topic_summary(
        must_memorize=[
            "Isolation Forest was chosen over Deep Learning for mathematical explainability in court and sub-second CPU execution.",
            "Defense-in-depth: If the ML model fails, deterministic NetworkX graph math and Benford's Law still identify syndicate hubs and laundering.",
            "Personal ownership: You designed the architecture, mathematical formulations, security contracts, and test assertions."
        ],
        trap_questions=[
            "Did ChatGPT write all your code? -> Confidently explain how you architected the system, selected the math formulas, and wrote the test assertions.",
            "Can a criminal tamper with your database? -> If SQLite is modified, the SHA-256 Merkle root hash completely changes, instantly proving tampering.",
            "Why not use an Autoencoder? -> Autoencoders require massive hyperparameter tuning, lack deterministic tree paths, and are unexplainable in court."
        ],
        code_checks=[
            "backend/tests/test_responsible_ai.py (17 automated pytests proving independence from UI)",
            "backend/app/main.py (Deterministic graph math running alongside ML)",
            "backend/scripts/run_offline_benchmark.py (Reproducible offline cross-validation)"
        ],
        whiteboard_note="Draw Defense-in-Depth stack: Ingest -> Deterministic Graph Math + Deterministic Accounting + Unsupervised ML -> Human Review.",
        rapid_sentence="CrimeNet pairs explainable tree partitioning with deterministic graph mathematics so that no single model failure can blind an investigation."
    ))
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════
    # MODULE 10: RAPID RECAP & MUST-MEMORIZE CHECKLIST
    # ══════════════════════════════════════════════════════════════════════
    story.append(Paragraph("SECTION 10 — RAPID RECAP & THE 10 COMMANDMENTS FOR INTERVIEW DAY", module_h1))

    recap_data = [
        [Paragraph("#", table_header), Paragraph("Question / Concept", table_header), Paragraph("Exact Formula / Metric", table_header), Paragraph("The 1-Sentence Spoken Defense", table_header)],
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
    t_recap = Table(recap_data, colWidths=[printable_width*0.06, printable_width*0.24, printable_width*0.32, printable_width*0.38])
    t_recap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_recap)
    story.append(Spacer(1, 8))

    story.append(make_callout(
        "<b>FINAL CONFIDENCE CHECKLIST BEFORE ENTERING THE INTERVIEW:</b><br/>"
        "• If asked to show the ML model: Open <code>backend/app/main.py</code> line 2100.<br/>"
        "• If asked to run the benchmark: Run <code>python backend/scripts/run_offline_benchmark.py</code>.<br/>"
        "• If asked to run tests: Run <code>python -m pytest backend/tests/test_responsible_ai.py -v</code> (17/17 pass).<br/>"
        "• If asked to show the live app: Open <font color='#0284C7'>https://crimenet-ai-two.vercel.app</font>.<br/>"
        "• Remember: Speak in simple English first. State the business/forensic intuition, then drop the exact formula and file name.",
        bg='#ECFDF5',
        border='#10B981',
        title="🎓 YOU ARE FULLY PREPARED — DEFEND YOUR CODE WITH ABSOLUTE CONFIDENCE!"
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master Interview Defense PDF successfully generated at: {PDF_OUTPUT_PATH}")

if __name__ == '__main__':
    build_pdf()
