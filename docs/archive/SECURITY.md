# 🔒 CrimeNet AI — Security Architecture & Governance Policy (SECURITY.md)

**System Classification:** Responsible Law Enforcement Decision-Support System  
**Lead Architect:** Aditya Pawar  
**Status:** Active Security Governance Document  

---

## 1. Threat Model

CrimeNet AI is architected as an intelligence decision-support platform. The threat model mitigates four primary adversary categories:

| Threat Category | Potential Attack Vector | Applied Mitigation Strategy |
| :--- | :--- | :--- |
| **Unauthorized Access** | Compromise of investigator credentials / brute-force attempts. | Rate limiting, hardware lockout cooldowns, and HMAC-SHA256 Bearer JWTs with 24-hour expiration. |
| **Evidence Tampering** | Malicious modification of historical CDR or financial records. | SHA-256 binary Merkle tree evidence accumulators; post-ingestion verification guarantees immutability. |
| **Biometric Spoofing** | Static printed photos or digital phone screen replays. | Zero-Mean Normalized Cross-Correlation (ZNCC) feature extraction paired with passive Eye Aspect Ratio (EAR) blink detection. |
| **Privilege Escalation** | Analyst attempting unauthorized case closure or warrant export. | Backend-enforced Role-Based Access Control (RBAC) validated on every FastAPI route. |

---

## 2. Role-Based Access Control (RBAC) Matrix

Permissions are enforced strictly in the **FastAPI backend layer**, not merely hidden in the frontend:

```
┌────────────────────────┬───────────┬──────────────┬────────────┬───────────────┬────────────┐
│ Capability / Action    │  Analyst  │ Investigator │ Supervisor │ Administrator │ Prosecutor │
├────────────────────────┼───────────┼──────────────┼────────────┼───────────────┼────────────┤
│ View Intelligence Graph│     ✓     │      ✓       │     ✓      │       ✓       │     ✓      │
│ Run Graph ML Analytics │     ✓     │      ✓       │     ✓      │       ✓       │     -      │
│ Annotate & Review XAI  │     -     │      ✓       │     ✓      │       ✓       │     -      │
│ Escalate High-Risk Lead│     -     │      ✓       │     ✓      │       ✓       │     -      │
│ Supervisor Approval    │     -     │      -       │     ✓      │       ✓       │     -      │
│ Export Dossier Drafts  │     -     │      ✓       │     ✓      │       ✓       │     ✓      │
│ Audit Log Inspection   │     -     │      -       │     ✓      │       ✓       │     -      │
│ System Policy Config   │     -     │      -       │     -      │       ✓       │     -      │
└────────────────────────┴───────────┴──────────────┴────────────┴───────────────┴────────────┘
```

---

## 3. Cryptographic Token & Secret Management

* **JWT Secret Keys:** Loaded strictly from environment variables (`CRIMENET_JWT_SECRET`). Never committed to Git.
* **Header Transmission:** Transmitted using the standard `Authorization: Bearer <TOKEN>` header.
* **Token Invalidation:** Revoked on logout and automatically expired after 86,400 seconds (24 hours).

---

## 4. Append-Only Audit Logging

All actions within the platform generate an immutable-style audit record:
* **Unique Audit ID:** `AUD-XXXX`
* **Timestamp in UTC:** Format `YYYY-MM-DD HH:MM:SS UTC`
* **User & Role Claims:** Investigator ID, Badge Number, Security Clearance Level.
* **Action Type:** `GRAPH_EXPLORATION_QUERY`, `CDR_BURST_INSPECTION`, `ALERT_CONFIRMATION`, `SUPERVISOR_APPROVAL`.
* **State Hash:** SHA-256 hash of the system state at the moment of execution.

> **Operational Note:** While CrimeNet AI enforces append-only semantics in the application layer, real-world forensic non-repudiation requires external WORM (Write-Once-Read-Many) cloud storage and SIEM retention.

---

## 5. Vulnerability Reporting & Disclosure

To report security concerns or unexpected model edge cases, contact the project maintainer:
* **Lead Architect:** Aditya Pawar
* **Repository:** pawaraditya0903/crimenet-ai
