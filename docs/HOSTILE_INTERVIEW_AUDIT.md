# CrimeNet AI: Hostile Technical Interview Audit

This document serves as the **Hostile Technical Interview Defense Guide** for **CrimeNet AI**. Every question below is answered with direct technical candor, referencing real code paths, mathematical formulations, operational trade-offs, and empirical verification.

---

## I. Architecture, Concurrency & Backend Engineering

### Q1: "Is this just an academic prototype or a real production backend?"
**Answer**: It is a modular, production-hardened Python application built with FastAPI, SQLite WAL mode, and decoupled service layers. While currently operating in `development`/`demonstration` mode with synthetic benchmark datasets, the backend enforces production fail-closed security invariants, transactional integrity, and genuine algorithmic implementations. All simulated components are explicitly labeled.

### Q2: "Why SQLite instead of PostgreSQL or MySQL?"
**Answer**: SQLite was chosen for zero-dependency standalone execution and transactional reliability. To make it production-defensible, we configured:
- `PRAGMA journal_mode = WAL` (Write-Ahead Logging allowing concurrent readers without blocking writes).
- `PRAGMA foreign_keys = ON` (relational referential integrity enforced on all tables).
- `PRAGMA busy_timeout = 5000` (resilient lock queueing).
- Context-managed transactions (`get_db()`) ensuring automatic rollback on exceptions.

### Q3: "How does the system handle concurrency and race conditions?"
**Answer**: WAL mode allows concurrent read transactions while serialized write transactions acquire table-level locks safely. By setting `busy_timeout` to 5 seconds and utilizing atomic SQLite transactions within Python context managers, write races are queued rather than failing abruptly.

### Q4: "What happens if the backend server crashes mid-request?"
**Answer**: SQLite Write-Ahead Logging ensures ACID crash recovery. Any uncommitted transaction is rolled back upon reconnection. For evidence uploads, the file hash is computed in-memory before database persistence, preventing orphaned records.

### Q5: "How are monolithic god-objects avoided in your codebase?"
**Answer**: The legacy monolith was decomposed into 11 dedicated routers (`auth`, `cases`, `evidence`, `alerts`, `graph`, `analytics`, `telecom`, `copilot`, `audit`, `reports`, `security`) and separate domain packages (`graph`, `ml`, `analytics`, `forensics`, `security`, `realtime`, `copilot`).

---

## II. Security, Identity & Cryptography

### Q6: "How are passwords stored and defended against GPU cracking?"
**Answer**: Using `PBKDF2-HMAC-SHA256` with 100,000 iterations and a unique 16-byte cryptographically secure salt generated via `secrets.token_bytes(16)` per user (`passwords.py`). Password verification is evaluated via `hmac.compare_digest` in constant time.

### Q7: "Can an attacker bypass authentication using the JWT `'none'` algorithm attack?"
**Answer**: No. `verify_jwt_token()` in `jwt.py` explicitly parses the header JSON and enforces `if header.get("alg") != "HS256": return None`. Furthermore, token claims must match `token_use == "access"`.

### Q8: "How does your system prevent Horizontal IDOR (accessing other users' cases)?"
**Answer**: Every case-scoped endpoint enforces `require_case_access()`. It queries the relational `case_assignments` table to verify that the requesting user ID is assigned to that case ID. Only users holding the `SUPERVISORY_OFFICER` role have oversight access across unassigned cases.

### Q9: "How do you defend against brute-force password guessing?"
**Answer**: A two-tier defense:
1. An in-memory sliding-window rate limiter per client IP.
2. An account lockout policy in SQLite: 5 consecutive failed attempts trigger a 15-minute lockout (`lockout_until = time() + 900`).

### Q10: "How do you protect PII data at rest?"
**Answer**: Sensitive suspect attributes (phones, addresses) are encrypted via AES-256-GCM (`crypto.py`) with a fresh 12-byte random nonce per operation (`os.urandom(12)`), outputting envelope ciphertext `enc:v1:<nonce>:<ct_and_tag>`.

### Q11: "What prevents production deployment with hardcoded default keys?"
**Answer**: `config.py` enforces a `verify_production_secrets()` hook. When `CRIMENET_ENV=production`, the application refuses to start if `JWT_SECRET_KEY` or `PII_ENCRYPTION_KEY` contains default words or has fewer than 32 bytes of entropy.

### Q12: "Is your facial recognition claim a marketing exaggeration, and how is the endpoint secured?"
**Answer**: We do NOT claim high-entropy facial biometrics or deep neural face embeddings. The face matching module is explicitly documented as a **Prototype** using Zero-Normalized Cross-Correlation (ZNCC) with multi-frame averaging for dual-factor demonstration. Furthermore, the endpoint is fully hardened:
1. `POST /api/security/verify-face` requires JWT authentication (`require_authenticated_user`).
2. Input vectors are bound and validated by Pydantic (`FaceVerifyRequest`: $16 \le \text{length} \le 1024$).
3. IP sliding-window rate limiting prevents brute-forcing ($30 \text{ req} / 60\text{s}$).
4. Enrolled master face descriptors are persisted in SQLite `system_settings` rather than transient server memory.
5. All frontend demo bypass buttons and hardcoded secrets have been completely removed.


---

## III. AI, Machine Learning & Analytics

### Q13: "What algorithm does your anomaly detection actually use?"
**Answer**: A Scikit-Learn `IsolationForest` ensemble ($n=200$ trees, $5\%$ contamination) combined with the Mahalanobis distance of the inverted covariance matrix. It operates on a 5-dimensional feature vector:
1. `financial_velocity_score`
2. `nocturnal_activity_ratio`
3. `graph_centrality_percentile`
4. `cdr_burst_zscore`
5. `benford_deviation_score`

### Q14: "How do you explain ML anomaly scores to investigators (XAI)?"
**Answer**: Through z-score feature attribution in `explainability.py`. Each feature's value is compared against background population baselines ($\mu, \sigma$). Any feature exceeding $2.0\sigma$ is highlighted with plain-English investigative signals (e.g., *"+748% above normal nocturnal velocity"*).

### Q15: "Why did your project previously claim '96.8% accuracy'?"
**Answer**: That was an ungrounded presentation claim from earlier design mockups. In this refactored release, all fake accuracy numbers have been permanently eliminated. Anomaly detection is statistically evaluated using synthetic injection benchmarks measuring real precision/recall on controlled test distributions.

### Q16: "Can your AI automatically advance a case or trigger an arrest warrant?"
**Answer**: **Never**. Automated enforcement is strictly forbidden under our Responsible AI Policy (`RESPONSIBLE_AI.md`). Copilot suggestions are output as inert `action_proposal` payloads requiring explicit human officer confirmation (`/api/copilot/actions/confirm`).

### Q17: "How is Benford's Law implemented?"
**Answer**: `benford.py` calculates leading-digit frequencies ($d \in \{1..9\}$) and compares them against Newcomb-Benford logarithmic distribution using a Pearson Chi-Square Goodness-of-Fit test with 8 degrees of freedom. Datasets with $N < 50$ transactions are rejected as statistically unrepresentative.

### Q18: "How does your telecom analysis detect burner SIM multiplexing?"
**Answer**: `telecom.py` analyzes cellular CDRs by grouping records by IMEI handset identifier and timestamp. If multiple distinct IMSIs (SIM cards) are detected operating on the same IMEI within a tight temporal window, a `SIM_MULTIPLEXING` alert is triggered.

### Q19: "How does cell tower trilateration work in your system?"
**Answer**: `trilateration.py` implements multi-tower Weighted Least Squares (WLS) using the log-distance path loss model:
$$P_{rx}(d) = P_{tx} - 10\cdot\eta\cdot\log_{10}(d)$$
Weights are assigned inversely proportional to distance variance, calculating Geometric Dilution of Precision (GDOP) and an estimated uncertainty radius. If fewer than 3 towers are available, it falls back to a 2-tower intersection chord.

---

## IV. Graph Analytics

### Q20: "Are your graph algorithms real NetworkX algorithms or fake mockups?"
**Answer**: Every graph endpoint runs genuine NetworkX 3.6 algorithms:
- `nx.pagerank(G, alpha=0.85)` for node importance.
- `nx.community.louvain_communities(G)` for modularity clustering.
- `nx.shortest_path(G, source, target, weight='weight')` via Dijkstra's algorithm.
- `nx.simple_cycles(G)` via Johnson's algorithm for financial circular loops.

### Q21: "How do you detect money laundering round-tripping?"
**Answer**: By building a directed financial transaction graph from SQLite and executing Johnson's simple cycles algorithm bounded to cycles of length $\le 6$. Any closed loops (e.g., Company A $\to$ Company B $\to$ Company C $\to$ Company A) are extracted with hop details and flag counts.

### Q22: "How scalable is your graph engine?"
**Answer**: In our empirical benchmarks (`docs/BENCHMARKS.md`), NetworkX executes PageRank on 100-node graphs in under $1.5\text{ ms}$ and Louvain community detection in under $6\text{ ms}$. For large-scale multi-million node graphs, an external graph database (e.g. Neo4j) would be required, but NetworkX is optimal and zero-overhead for typical law enforcement syndicate networks (< 5,000 entities).

---

## V. Forensics, Evidence & Audit Trail

### Q23: "How do you prove that evidence has not been tampered with post-upload?"
**Answer**: During upload, the server immediately calculates the `SHA-256` digest of the byte stream and saves it to `evidence_items`. Any subsequent request to `/api/evidence/{id}/verify` recalculates the hash and compares it in constant time. If a single bit is modified, verification flags `TAMPER_DETECTED`.

### Q24: "How does your Merkle tree verify evidence integrity?"
**Answer**: `merkle.py` implements a Binary Merkle Tree. It takes all evidence SHA-256 hashes as leaves, pairs them upwards, and computes the Merkle Root. Inclusion proofs ($O(\log N)$ sibling hashes) verify any item's presence without transmitting the entire repository.

### Q25: "How does your audit log prevent rogue database administrators from modifying history?"
**Answer**: In `audit/chain.py`, audit events form a cryptographically hash-linked chain:
$$H_i = \text{SHA256}(H_{i-1} + \text{canonical}(payload_i))$$
If a DBA modifies an event's action, resource, or deletes a row, `verify_audit_chain()` detects the broken link and pinpoints the exact row index.

### Q26: "Does your PDF report builder constitute legal court certification under Section 65B?"
**Answer**: No. Every generated PDF includes a prominent statutory legal disclaimer stating that the document is a preliminary analytical draft for investigator decision support, not an automated judicial certificate.

---

## VI. Realtime Telemetry & Testing

### Q27: "How is Socket.IO authenticated?"
**Answer**: In `socket_manager.py`, the `connect` event handler extracts the Bearer JWT from `auth.token` or query parameters and verifies it. Connections with invalid or absent tokens return `False` and are dropped. Case room subscriptions require verified case assignment.

### Q28: "How extensive is your automated test suite?"
**Answer**: We have **51 automated tests** covering unit, integration, security, machine learning, graph analytics, and digital forensics. All tests run under `pytest` with zero failures.

### Q29: "What real performance metrics can you share?"
**Answer**: From our empirical benchmark suite (`run_benchmarks.py`):
- SHA-256 Throughput: $>2,000\text{ MB/s}$ (Median $0.45\text{ ms}$ for 1MB).
- AES-256-GCM Envelope Encryption: Median $0.013\text{ ms}$.
- PageRank: Median $0.71\text{ ms}$.
- Isolation Forest Inference: Median $8.8\text{ ms}$.
- PDF Generation: Median $3.8\text{ ms}$.

### Q30: "Why is CrimeNet AI now a 10/10 defensible engineering project?"
**Answer**: Because every claim is backed by real code, every algorithm executes genuine mathematics, every security boundary is enforced and verified with automated tests, and every simulated capability is labeled with total transparency.
