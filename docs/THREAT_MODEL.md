# CrimeNet AI: Comprehensive STRIDE Threat Model

This document provides a formal **STRIDE Threat Model** evaluating the 13 primary attack vectors against **CrimeNet AI**, detailing the threat classification, attack mechanics, implemented defensive countermeasures, and automated verification tests.

---

## 1. STRIDE Threat Matrix Summary

| # | Threat Vector | STRIDE Category | Impact Severity | Defense Mechanism | Automated Test Reference |
| :-: | :--- | :---: | :---: | :--- | :--- |
| **1** | JWT Algorithm Confusion (`'none'` alg) | Spoofing | **Critical** | Header algorithm check enforcing `HS256` | `test_reject_none_algorithm_jwt` |
| **2** | Forged JWT Signature / Key Guessing | Spoofing | **Critical** | Constant-time HMAC verification + fail-closed secret | `test_reject_forged_signature_jwt` |
| **3** | Horizontal IDOR on Case Records | Elevation of Privilege | **High** | Relational case assignment check (`require_case_access`) | `test_horizontal_idor_prevention` |
| **4** | Vertical Privilege Escalation | Elevation of Privilege | **High** | 4-tier Role-Based Access Control gate | `test_vertical_privilege_escalation` |
| **5** | Password Brute Force / Credential Stuffing | Denial of Service | **Medium** | Sliding window rate limit + 5-attempt lockout | `test_brute_force_login_lockout` |
| **6** | Insider Database Tampering of Audit Trail | Tampering / Repudiation | **Critical** | Cryptographic hash-linked chain ($H_i = \text{SHA256}(H_{i-1} + C_i)$) | `test_audit_chain_tamper_detection` |
| **7** | Digital Evidence Bit-Flipping / Alteration | Tampering | **Critical** | SHA-256 vault digest + Binary Merkle Root inclusion | `test_evidence_bit_flip_tampering` |
| **8** | Unauthenticated WebSocket Eavesdropping | Information Disclosure | **High** | Socket.IO handshake JWT check + case room auth | `test_socket_connection_rejected_without_auth` |
| **9** | Large Body Request Payload DoS Flooding | Denial of Service | **Medium** | Streaming 10MB Content-Length & body size limiter | `test_request_size_limit_rejection` |
| **10** | Timing Side-Channel Attacks on Signatures | Information Disclosure | **Medium** | `hmac.compare_digest` constant-time evaluation | `test_constant_time_comparison` |
| **11** | ML Feature Manipulation / False Alarms | Tampering | **Medium** | Explainability z-scores + human officer verification | `test_feature_attribution_and_signal` |
| **12** | Prompt Injection & Copilot Hijacking | Tampering / Spoofing | **High** | Authoritative backend retrieval + two-step action confirm | `test_copilot_context_retrieval_and_action` |
| **13** | Insecure Startup Defaults in Production | Configuration / Tampering | **Critical** | Fail-closed production validator (`verify_production_secrets`) | Tested via environment startup validation |

---

## 2. In-Depth Analysis of Threat Vectors

### Vector 1: JWT Algorithm Confusion (`'none'` algorithm attack)
- **Mechanics**: An attacker modifies the JWT header to `{"alg": "none", "typ": "JWT"}` and strips the signature, hoping the server accepts the unverified claims.
- **Countermeasure**: In `backend/app/security/jwt.py`, `verify_jwt_token` explicitly parses the header and enforces `if header.get("alg") != "HS256": return None`. Unsigned tokens are rejected immediately.
- **Verification**: `tests/security/test_jwt_attacks.py::test_reject_none_algorithm_jwt`.

### Vector 2: Forged JWT Signatures & Secret Brute-Forcing
- **Mechanics**: An attacker creates a token signed with an arbitrary key or tries to brute-force a weak secret.
- **Countermeasure**: Signatures are evaluated using HMAC-SHA256 with constant-time equality. In production (`CRIMENET_ENV=production`), `config.py` enforces high-entropy secrets (minimum 32 bytes, not containing "demo", "secret", or "changeme").
- **Verification**: `tests/security/test_jwt_attacks.py::test_reject_forged_signature_jwt`.

### Vector 3: Horizontal IDOR (Insecure Direct Object References)
- **Mechanics**: An authenticated investigator assigned to Case A alters the URL parameter or request payload to access Case B.
- **Countermeasure**: The `require_case_access` dependency queries the `case_assignments` table. Unless the investigator is assigned to the requested case or holds the `SUPERVISORY_OFFICER` role, the server aborts with `403 Forbidden`.
- **Verification**: `tests/security/test_rbac_idor.py::test_horizontal_idor_prevention_on_unassigned_case`.

### Vector 4: Vertical Privilege Escalation
- **Mechanics**: An `INTELLIGENCE_AUDITOR` or `FORENSIC_ANALYST` issues requests to administrative endpoints, such as advancing case stages or reviewing supervisor escalations.
- **Countermeasure**: Role hierarchy decorators (`require_roles([ForensicRole.LEAD_INVESTIGATOR, ForensicRole.SUPERVISORY_OFFICER])`) inspect claims extracted from verified JWT tokens and deny execution.
- **Verification**: `tests/security/test_rbac_idor.py::test_vertical_privilege_escalation_rejection`.

### Vector 5: Password Brute-Force & Credential Stuffing
- **Mechanics**: Automated botnets attempt dictionary attacks on user logins.
- **Countermeasure**: Sliding window rate limiting combined with SQLite-persisted failed attempt counters. Five failed login attempts lock the account for 15 minutes (`lockout_until = time() + 900`).
- **Verification**: `tests/security/test_brute_force.py::test_brute_force_login_lockout`.

### Vector 6: Insider Database Tampering of Audit Logs
- **Mechanics**: A privileged database administrator or rogue insider attempts to alter or delete rows in the `audit_chain` table to erase traces of unauthorized activity.
- **Countermeasure**: Every record stores a previous block hash:
  $$H_i = \text{SHA256}(H_{i-1} + \text{canonical}(payload_i))$$
  Modifying, inserting, or deleting any row invalidates all subsequent hashes. The `verify_audit_chain()` engine scans the entire chain and pinpoints the exact index of any discrepancy.
- **Verification**: `tests/forensic/test_audit_chain_tamper.py::test_hash_linked_audit_chain_tamper_detection`.

### Vector 7: Digital Evidence Bit-Flipping / Post-Ingest Alteration
- **Mechanics**: Evidence files stored on disk or in the database are modified after ingestion.
- **Countermeasure**: During ingestion, an authoritative SHA-256 digest is generated and recorded. Bit-level re-verification detects single-bit flips. Furthermore, all evidence items are rolled into a Binary Merkle Tree, allowing inclusion proofs and quick tamper localization.
- **Verification**: `tests/forensic/test_evidence_tampering.py::test_evidence_bit_flip_tampering`.

### Vector 8: Unauthenticated WebSocket / Telemetry Eavesdropping
- **Mechanics**: An external actor establishes a Socket.IO connection to intercept live investigation broadcasts.
- **Countermeasure**: Handshake authentication enforces Bearer JWT validation. Clients joining rooms (`join_case_room`) must be assigned to the requested case; otherwise, the join is refused.
- **Verification**: `tests/integration/test_realtime_auth.py`.

### Vector 9: Malicious Request Body Flooding (DoS)
- **Mechanics**: Attackers upload excessively large JSON or binary payloads to exhaust backend memory.
- **Countermeasure**: Streaming ASGI middleware enforces a strict 10 MB payload ceiling (`MAX_CONTENT_LENGTH_BYTES = 10 * 1024 * 1024`), terminating oversized streams before memory allocation.
- **Verification**: `tests/security/test_api_hardening.py::test_request_size_limit_rejection`.

### Vector 10: Timing Side-Channel Attacks
- **Mechanics**: Measuring execution time variations during string comparison to infer secret token bytes one by one.
- **Countermeasure**: All secret, token, hash, and password comparisons utilize `hmac.compare_digest`.
- **Verification**: `tests/unit/test_hashing.py::test_constant_time_comparison`.

### Vector 11: Adversarial Telemetry Poisoning
- **Mechanics**: Attackers flood call records or small transactions to skew machine learning anomaly thresholds.
- **Countermeasure**: Multi-dimensional ensemble combining tree partitioning (Isolation Forest) with Mahalanobis covariance distance. Feature attribution provides transparent baseline deviations ($z$-scores) for human validation.

### Vector 12: Prompt Injection & Copilot Hijacking
- **Mechanics**: Malicious text injected into case dossiers directs the Copilot to take illegal actions or fabricate evidence.
- **Countermeasure**: Client-provided context is ignored; context is fetched server-side from SQLite. Copilot actions are purely proposals (`action_proposal`) that require explicit human officer authorization via `/api/copilot/actions/confirm`.
- **Verification**: `tests/integration/test_copilot_safety.py`.

### Vector 13: Insecure Production Defaults
- **Mechanics**: Deploying the application to production with demo keys or missing environment variables.
- **Countermeasure**: In `backend/app/config.py`, when `CRIMENET_ENV=production`, `verify_production_secrets()` checks `JWT_SECRET_KEY` and `PII_ENCRYPTION_KEY`. If keys are default, short, or weak, `RuntimeError` is raised and the process terminates immediately.
