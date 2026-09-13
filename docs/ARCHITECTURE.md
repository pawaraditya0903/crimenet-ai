# CrimeNet AI: System Architecture & Data Flow

This document details the software architecture, modular subsystem decomposition, database schemas, and data pipelines of **CrimeNet AI**.

---

## 1. High-Level System Architecture

CrimeNet AI is structured into decoupled layers, ensuring clear boundaries between transport, business logic, analytics, security, and persistence:

```
+-----------------------------------------------------------------------+
|                     PRESENTATION LAYER (React + Vite)                 |
|  - Tactical Operations Dashboard   - Network Graph Explorer           |
|  - Cellular CDR & Radar            - Crypto/Hawala Flow Tracer        |
|  - Alert Centre & Human Review     - Copilot Chat Interface           |
+-----------------------------------------------------------------------+
                                  |
                                  | HTTPS (REST API) & WSS (Socket.IO)
                                  v
+-----------------------------------------------------------------------+
|                    GATEWAY & SECURITY MIDDLEWARE                      |
|  - Correlation ID Middleware       - Security Headers (CSP, HSTS)     |
|  - 10MB Body Payload Limiter       - Sliding-Window Rate Limiter      |
|  - PBKDF2 / JWT Auth Engine        - RBAC & IDOR Authorization Gate   |
+-----------------------------------------------------------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
+-----------------------+                   +-----------------------+
|   ROUTER CONTROLLERS  |                   |   REALTIME ENGINE     |
|  - /api/auth          |                   |  - python-socketio    |
|  - /api/cases         |                   |  - Case Room Routing  |
|  - /api/evidence      |                   |  - In-Flight Alerts   |
|  - /api/alerts        |                   +-----------------------+
|  - /api/graph         |                               |
|  - /api/analytics     |                               |
|  - /api/telecom       |                               |
|  - /api/copilot       |                               |
+-----------------------+                               |
            |                                           |
            +---------------------+---------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                     CORE SERVICE ENGINES                              |
|  +---------------------+  +--------------------+  +----------------+  |
|  | NetworkX Engine     |  | ML Pipeline        |  | Forensic Vault |  |
|  | - PageRank (d=0.85) |  | - Isolation Forest |  | - SHA-256 Root |  |
|  | - Dijkstra (Weight) |  | - Mahalanobis Cov  |  | - Merkle Tree  |  |
|  | - Louvain Modularity|  | - Feature XAI      |  | - ReportLab PDF|  |
|  | - Johnson's Cycles  |  | - Benford Analysis |  | - Audit Chain  |  |
|  +---------------------+  +--------------------+  +----------------+  |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                  PERSISTENCE LAYER (SQLite with WAL)                  |
|  - Foreign Key Constraints Active   - PRAGMA journal_mode = WAL       |
|  - Atomic Transactions Context      - Relational Indices on FKs       |
|  - Encrypted PII (AES-256-GCM)      - Append-Only Audit Chain Ledger  |
+-----------------------------------------------------------------------+
```

---

## 2. Directory Layout & Subsystem Responsibilities

```
backend/
├── app/
│   ├── config.py                 # Fail-closed environment variables and production keys
│   ├── main.py                   # FastAPI app entrypoint, middleware, and router mounting
│   ├── models/
│   │   ├── database.py           # SQLite connection pool, WAL mode, transaction context
│   │   └── tables.py             # Schema initializers and demonstration data seeding
│   ├── schemas/                  # Pydantic v2 request/response validation contracts
│   │   ├── auth.py, cases.py, evidence.py, alerts.py, analytics.py, copilot.py
│   ├── security/
│   │   ├── crypto.py             # AES-256-GCM envelope encryption, SHA-256, constant-time compare
│   │   ├── passwords.py          # PBKDF2-HMAC-SHA256 (100k iters) and password complexity rules
│   │   ├── jwt.py                # HMAC-SHA256 tokens, refresh token rotation and revocation
│   │   ├── rbac.py               # 4-tier forensic roles and horizontal IDOR case access checks
│   │   ├── rate_limit.py         # Sliding window rate limiter & brute-force lockout
│   │   ├── middleware.py         # Security headers, correlation IDs, 10MB request size limit
│   │   └── face_prototype.py     # Edge ZNCC facial comparison prototype
│   ├── graph/
│   │   ├── engine.py             # SQLite-to-NetworkX graph topology loader
│   │   ├── centrality.py         # PageRank ($d=0.85$), degree, betweenness centrality
│   │   ├── communities.py        # Louvain community clustering and modularity ($Q$) score
│   │   ├── paths.py              # Dijkstra weighted shortest path computation
│   │   └── cycles.py             # Johnson's simple cycles for money laundering loops
│   ├── ml/
│   │   ├── features.py           # 5-dimensional feature engineering extraction
│   │   ├── pipeline.py           # Scikit-Learn IsolationForest + Mahalanobis ensemble
│   │   ├── explainability.py     # Feature attribution z-scores and plain-English signals
│   │   └── evaluation.py         # Synthetic anomaly injection benchmarking
│   ├── analytics/
│   │   ├── benford.py            # First-digit distribution, Chi-square test ($df=8$)
│   │   ├── financial.py          # Smurfing detection, Shannon entropy of mule accounts
│   │   ├── telecom.py            # Nocturnal calling ratio, burst z-score, burner SIMs
│   │   └── trilateration.py      # Multi-tower WLS trilateration, GDOP, uncertainty radius
│   ├── forensics/
│   │   ├── evidence_vault.py     # SHA-256 file hashing and bit-level integrity verification
│   │   ├── merkle.py             # Binary Merkle Tree construction and inclusion proofs
│   │   └── report_builder.py     # Multi-page ReportLab PDF generation with running hashes
│   ├── audit/
│   │   └── chain.py              # Hash-linked tamper-evident ledger ($H_i = \text{SHA256}(H_{i-1} + C_i)$)
│   ├── realtime/
│   │   └── socket_manager.py     # Authenticated Socket.IO connections and room authorization
│   ├── copilot/
│   │   └── service.py            # Server-side case context retrieval and safe action proposals
│   └── routers/                  # 11 Clean FastAPI router modules
└── scripts/
    └── run_benchmarks.py         # Empirical performance benchmark harness
```

---

## 3. Core Data Workflows

### 3.1 Evidence Ingestion Workflow
1. Investigator uploads digital evidence (CDR, RTGS wire CSV, ANPR log) via `/api/evidence/upload`.
2. Gateway verifies caller has `FORENSIC_ANALYST` or higher role and is assigned to the target case.
3. Vault computes `SHA-256` hash immediately on incoming byte stream.
4. Evidence metadata, byte size, MIME type, and hash are inserted into `evidence_items`.
5. Audit event `EVIDENCE_ATTACHED` is appended to the hash-linked chain with prior block link.
6. Binary Merkle tree recalculates root hash across all case evidence items.
7. Realtime Socket.IO broadcasts `EVIDENCE_ADDED` to authorized subscribers in `case_{case_id}`.

### 3.2 Statistical Anomaly Generation & Review Workflow
1. Telemetry ingest triggers ML feature engineering pipeline (`features.py`).
2. Scikit-Learn `IsolationForest` decision function and Mahalanobis covariance distance produce a calibrated anomaly score.
3. Explainability module generates z-score feature deviations and plain-English signals.
4. Record inserted into `alerts` table with initial status `PENDING_REVIEW`.
5. Investigator reviews alert in UI: selects `CONFIRM`, `SUPPRESS`, or `ESCALATE_SUPERVISOR` with case note.
6. If escalated, the supervisory officer must approve or reject the lead. AI cannot advance stages autonomously.
7. Decision logged in `alert_reviews` and recorded in the audit chain.

### 3.3 Copilot Query & Safe Action Workflow
1. User submits query to Copilot chat interface (`/api/copilot/chat`).
2. Service retrieves authoritative context from SQLite (case info, suspects, evidence hashes, active alerts). User client cannot supply unverified context.
3. System compiles structured briefing citing exact entity IDs (`[Case: c1]`, `[Evidence: ev-01]`).
4. If stage transition is suggested, Copilot returns an `action_proposal` with parameters.
5. Action remains inert until investigator explicitly clicks "Confirm Action" hitting `/api/copilot/actions/confirm`.
6. Database mutation occurs under relational transaction, and an audit event is appended.

---

## 4. Frontend Architecture & Modular Decomposition

The frontend is organized into modular components with strict boundary separation:

```
frontend/src/
├── components/
│   ├── SecurityGate.tsx       # Zero-trust login gate with pure backend JWT auth (no bypass buttons)
│   ├── SecurityModals.tsx     # Modular audit log table and intruder mugshot preview
│   ├── CommandBar.tsx         # Unified tactical search and command palette
│   ├── CopilotDrawer.tsx      # HITL AI copilot drawer
│   ├── DemoTourModal.tsx      # System architecture tour
│   └── NotificationToast.tsx  # Event notifications
├── lib/
│   ├── api.ts                 # Axios instance with JWT interceptor
│   └── audio.ts               # Singleton Web Audio API synthesizer
├── pages/                     # 13 Dedicated analytical modules
├── App.tsx                    # Master application shell, state router, desktop layout
└── main.tsx                   # React DOM root entrypoint
```

- **AudioContext Singleton**: A shared `AudioContext` in `lib/audio.ts` prevents browser resource exhaustion and context starvation.
- **WebSocket Reconnection Stability**: Real-time event listeners use mutable React refs (`soundEnabledRef`) to isolate UI audio toggles from Socket.IO socket connections, preventing reconnection storms.
- **Collision-Proof Case Creation**: Relational cases use UUID-backed identifiers (`case-{uuid.uuid4().hex[:8]}`) preventing race-condition collisions during concurrent registrations.
- **Persistent Biometric Vector Store**: Master face descriptors are persisted directly to SQLite `system_settings`, ensuring durability across multi-worker and server restarts.

