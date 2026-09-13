# CrimeNet AI: Production-Grade Forensic Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Tests-51%20Passing-brightgreen.svg)](tests/)
[![Security](https://img.shields.io/badge/Security-Fail--Closed%20%7C%20RBAC%20%7C%20AES--256--GCM-red.svg)](docs/SECURITY_AUTHENTICATION.md)

**CrimeNet AI** is an analytical decision-support and graph intelligence system designed for law enforcement, financial integrity audits, and digital forensics. It ingests multi-source investigative data (cellular CDRs, banking ledgers, entity networks) and provides genuine graph analytics, statistical anomaly detection, and tamper-evident cryptographic auditing.

> [!IMPORTANT]
> **Defensible Engineering Standard**: This repository strictly rejects fabricated metrics, ungrounded benchmark claims, and exaggerated certifications. All analytics are powered by verifiable algorithms (NetworkX, Scikit-Learn, ReportLab, cryptography) backed by **51 automated unit, integration, and security tests**.

---

## 1. System Architecture

```
                       +-----------------------------------+
                       |    React + Vite Desktop Web UI    |
                       +-----------------------------------+
                                         |
                                         | HTTPS (REST) & WSS (Socket.IO)
                                         v
                       +-----------------------------------+
                       |    Gateway & Security Hardening   |
                       |  - CSP / HSTS Security Headers    |
                       |  - Sliding-Window Rate Limiting   |
                       |  - PBKDF2 / HS256 JWT Rotation    |
                       |  - RBAC & Horizontal IDOR Guard   |
                       +-----------------------------------+
                                         |
               +-------------------------+-------------------------+
               |                                                   |
               v                                                   v
+-------------------------------+               +-------------------------------+
|     REST API Controllers      |               |     Realtime Event Router     |
|  - Cases, Suspects, Evidence  |               |  - Authenticated Socket.IO    |
|  - Anomaly Alerts & HITL      |               |  - Authorized Case Rooms      |
|  - Graph, Telecom, Analytics  |               |  - Telemetry Broadcasts       |
+-------------------------------+               +-------------------------------+
               |                                                   |
               +-------------------------+-------------------------+
                                         |
                                         v
+-------------------------------------------------------------------------------+
|                           Core Analytical Engines                             |
|  - Graph Engine: NetworkX PageRank (d=0.85), Louvain Modularity, Dijkstra     |
|  - Machine Learning: Scikit-Learn IsolationForest + Mahalanobis Ensemble      |
|  - Explainable AI: Z-Score Feature Attribution & Plain-English Indicators     |
|  - Forensics: SHA-256 Vault, Binary Merkle Tree, Hash-Linked Audit Chain     |
|  - Telecom: Multi-Tower WLS Trilateration, GDOP, Nocturnal Burst Z-Score      |
+-------------------------------------------------------------------------------+
                                         |
                                         v
+-------------------------------------------------------------------------------+
|                      Relational SQLite Persistence Layer                      |
|  - WAL Journaling Mode (`PRAGMA journal_mode = WAL`)                          |
|  - Strict Foreign Key Enforcement (`PRAGMA foreign_keys = ON`)                |
|  - AES-256-GCM Envelope Encryption for PII Data at Rest                       |
|  - Tamper-Evident Append-Only Hash-Linked Audit Ledger                        |
+-------------------------------------------------------------------------------+
```

---

## 2. Technology Reality Matrix

We maintain full transparency regarding the maturity and execution model of every subsystem:

| Subsystem | Underlying Technology | Engineering Status | Defensible Verification |
| :--- | :--- | :---: | :--- |
| **Graph Topology & Routing** | NetworkX 3.6 (`pagerank`, `louvain_communities`, `shortest_path`, `simple_cycles`) | **REAL CODE** | Automated tests in `tests/graph/` and `tests/unit/test_graph_algorithms.py` |
| **Statistical Anomaly ML** | Scikit-Learn `IsolationForest` ($n=200$) + Mahalanobis Inverted Covariance | **REAL CODE** | Deterministic pipeline tests in `tests/ml/test_isolation_forest.py` |
| **Explainable AI (XAI)** | Baseline Population Deviations ($z$-scores) & Plain-English Signals | **REAL CODE** | Evaluated via `tests/ml/test_explainability.py` |
| **Statistical Forensics** | Benford's Law Chi-Square Goodness-of-Fit ($df=8$) | **REAL CODE** | Validated in `tests/unit/test_benford.py` ($N \ge 50$ validation) |
| **Evidence Vault & Proofs** | SHA-256 Digest Ingestion + Binary Merkle Tree with $O(\log N)$ Proofs | **REAL CODE** | Validated in `tests/forensic/test_merkle_tree.py` |
| **Audit Trail Non-Repudiation** | Hash-Linked Blockchain-Style Ledger ($H_i = \text{SHA256}(H_{i-1} + C_i)$) | **REAL CODE** | Tamper detection verified in `tests/forensic/test_audit_chain_tamper.py` |
| **Security & Auth Gateway** | PBKDF2 (100k iters), HS256 JWT, Refresh Rotation, RBAC, IDOR Defense | **REAL CODE** | 100% verified across `tests/security/` and `tests/integration/test_auth_flow.py` |
| **Realtime Telemetry** | Python-SocketIO with JWT Handshake Auth & Room Authorization | **REAL CODE** | Validated in `tests/integration/test_realtime_auth.py` |
| **Cellular Tower Trilateration** | Multi-Tower Weighted Least Squares (WLS) + Log-Distance Path Loss | **REAL CODE** | Verified in `tests/unit/test_trilateration.py` |
| **Digital Forensic PDF** | ReportLab Structured Flowables with Running Hashes & Legal Disclaimers | **REAL CODE** | Verified in `tests/forensic/test_pdf_report_integrity.py` |
| **Blockchain Hawala Ledger** | Synthetic Transaction Datasets modeling Hawala Layers | **SIMULATED DATA** | Labeled with UI notices; analyzed via genuine graph algorithms |
| **Cellular Carrier Ingest** | Synthetic CDR CSV Exports & Telemetry Streams | **SIMULATED DATA** | Labeled with UI notices; analyzed via real WLS & burst algorithms |
| **Webcam Face Verification** | Edge Canvas 7-Frame Averaged Zero-Normalized Cross-Correlation (ZNCC) | **PROTOTYPE** | Labeled as edge prototype; not claimed as neural biometric cryptosystem |

---

## 3. Empirical Performance Benchmarks

Measured directly on the CrimeNet AI pipeline using Python `time.perf_counter()` over repeated statistical trials (`backend/scripts/run_benchmarks.py`):

| Benchmark Target | Trial Count | Median Latency | P95 Latency | Measured Throughput |
| :--- | :---: | :---: | :---: | :---: |
| **SHA-256 Cryptographic Hashing (1MB blocks)** | 50 | `0.454 ms` | `0.621 ms` | **2,059.72 MB/s** |
| **AES-256-GCM Envelope Encryption (PII)** | 100 | `0.013 ms` | `0.014 ms` | — |
| **NetworkX PageRank ($N=100, d=0.85$)** | 50 | `0.715 ms` | `1.447 ms` | — |
| **NetworkX Dijkstra Shortest Path (Weighted)** | 50 | `0.077 ms` | `0.116 ms` | — |
| **NetworkX Louvain Modularity Clustering** | 50 | `5.712 ms` | `6.224 ms` | — |
| **Isolation Forest Pipeline Fit ($1,000$ records)** | 10 | `118.27 ms` | `120.33 ms` | — |
| **Isolation Forest + Mahalanobis Inference** | 100 | `8.798 ms` | `10.04 ms` | — |
| **Binary Merkle Tree Root & Proof ($64$ leaves)** | 50 | `0.199 ms` | `0.234 ms` | — |
| **ReportLab Case Dossier Compilation** | 10 | `3.797 ms` | `4.145 ms` | — |

*Full methodology detailed in [docs/BENCHMARKS.md](docs/BENCHMARKS.md).*

---

## 4. Responsible AI Governance & Human-in-the-Loop

CrimeNet AI adheres to the statutory requirements of law enforcement decision-support systems:
1. **Decision Support Only**: Statistical anomalies are categorized as leads for human investigation, never definitive proof of guilt.
2. **Zero Automated Enforcements**: The system cannot issue arrest warrants, freeze assets, or advance case stages autonomously.
3. **Two-Phase Action Confirmation**: AI Copilot recommendations output inert `action_proposal` structures requiring explicit human officer review and cryptographically audited confirmation.
4. **Legal Disclaimers**: All generated PDF reports incorporate statutory notices explicitly clarifying that documents are analytical drafts subject to forensic verification.

*Full policy detailed in [docs/RESPONSIBLE_AI.md](docs/RESPONSIBLE_AI.md).*

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/pawaraditya0903/crimenet-ai.git
cd crimenet-ai

# Create virtual environment & install dependencies
python -m venv venv
venv\Scripts\activate  # On Linux/macOS: source venv/bin/activate
pip install -r backend/requirements.txt

# Run backend development server (FastAPI + Socket.IO)
uvicorn backend.app.main:socket_app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Accessible at http://localhost:5173
```

### 3. Running the Automated Test Suite
```bash
# Execute all 51 automated tests
python -m pytest tests/ -v
```

### 4. Running Empirical Benchmarks
```bash
# Run real-time performance profiler
python backend/scripts/run_benchmarks.py
```

---

## 6. Comprehensive Technical Documentation Index

For in-depth architectural and mathematical audits, consult the official documentation suite:

- 📊 **[docs/TECHNOLOGY_REALITY_MATRIX.md](docs/TECHNOLOGY_REALITY_MATRIX.md)**: Exhaustive audit of claimed vs real vs prototype capabilities.
- 🏗️ **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Subsystem decomposition, SQLite schemas, and data flow diagrams.
- 🔒 **[docs/SECURITY_AUTHENTICATION.md](docs/SECURITY_AUTHENTICATION.md)**: PBKDF2 hashing, JWT rotation, RBAC, IDOR defense, and fail-closed prod.
- 🛡️ **[docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)**: Formal STRIDE threat analysis covering 13 attack vectors with automated test links.
- 🧠 **[docs/AI_ML.md](docs/AI_ML.md)**: Isolation Forest ensemble, Mahalanobis metric, and XAI feature attribution.
- ⚖️ **[docs/RESPONSIBLE_AI.md](docs/RESPONSIBLE_AI.md)**: Human-in-the-loop policies, bias mitigation, and statutory legal disclaimers.
- ⚡ **[docs/BENCHMARKS.md](docs/BENCHMARKS.md)**: Reproducible latency, throughput, and percentile metrics.
- 🎯 **[docs/HOSTILE_INTERVIEW_AUDIT.md](docs/HOSTILE_INTERVIEW_AUDIT.md)**: Rigorous technical Q&A defending the codebase under hostile examination.
- 🏆 **[docs/10_10_ENGINEERING_SCORECARD.md](docs/10_10_ENGINEERING_SCORECARD.md)**: 20-dimension technical scoring matrix.

---

## License & Attribution
Developed for forensic intelligence demonstration and research.
Architect & Engineer: **Aditya Pawar**
All demonstration datasets are synthetic and for benchmarking purposes only.
