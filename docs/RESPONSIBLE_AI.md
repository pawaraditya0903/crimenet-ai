# CrimeNet AI — Responsible AI & Human-in-the-Loop Governance Charter

**Classification:** Decision-Support Software for Criminal Intelligence & Anti-Money Laundering  
**Standard:** IEEE 7000 / NIST AI Risk Management Framework (AI RMF 1.0) Compliant Governance  

---

## 1. Foundational Operating Principle

CrimeNet AI is strictly **decision-support software**. It is designed to assist human criminal investigators, digital forensic analysts, and compliance officers by identifying statistical outliers, mapping complex relational graphs, and organizing digital evidence.

### What CrimeNet AI DOES NOT Do:
1. **Does NOT Determine Guilt or Innocence**: Algorithmic scores and graph centralities do not constitute legal proof of criminal liability or culpability.
2. **Does NOT Authorize Arrests or Raids**: The software cannot unilaterally issue arrest warrants, order tactical deployments, or freeze financial assets.
3. **Does NOT Replace Judicial Due Process**: Algorithmic findings are investigative leads that must be independently corroborated and vetted by human authorities under lawful procedure.
4. **Does NOT Perform Mass Public Surveillance**: The platform is built for focused casework based on lawfully ingested investigative records.

---

## 2. Permitted vs. Prohibited Use Cases

| Permitted Investigative Use | Strictly Prohibited Use |
| :--- | :--- |
| Structuring multi-hop financial transactions into visual graphs | Autonomous issuance of arrest warrants or seizure orders |
| Identifying unusual nocturnal call bursts requiring human review | Demographic profiling or predictive policing based on race/religion |
| Verifying post-ingestion bit-level evidence file integrity (SHA-256) | Claiming algorithmic scores constitute "automatic judicial proof" |
| Recommending case progression for human officer authorization | Execution of coercive state actions without human signoff |

---

## 3. Human-in-the-Loop (HITL) Protocol

All analytical anomalies follow an enforceable five-stage human lifecycle:

```
[ Algorithmic Signal ] ──> [ Pending Human Review ] ──> [ Investigator Review ]
                                                              │
                                     ┌────────────────────────┴────────────────────────┐
                                     ▼                                                 ▼
                          [ Confirm Threat Lead ]                           [ Suppress False Positive ]
                                     │
                                     ▼
                     [ Escalate to Supervisor ]
                                     │
                                     ▼
                     [ Supervisory Authorization ]
                                     │
                                     ▼
                 [ Recorded in Hash-Linked Audit Chain ]
```

### Review Controls:
- **Investigator Accountability**: Every review action records the investigator's ID, timestamp, decision, and explanatory justification in a cryptographically linked audit chain.
- **Dual-Control Escalation**: High-consequence investigative advancements (e.g. stage transition to warrant drafting) require formal supervisory officer sign-off.
- **False Positive Feedback**: Investigators can flag commercial anomalies (e.g. legitimate holiday wire surges) to calibrate contamination parameters.

---

## 4. Explainable AI (XAI) Standards

Black-box alert scoring is strictly prohibited in CrimeNet AI. Every alert must provide:
- **Feature Attribution**: Explicit comparison of observed values against population baseline means and standard deviations ($Z$-score).
- **Plain-English Explanation**: Clear description of the contributing signals (e.g. *"Call frequency surge of 4.12σ above 24-hour baseline paired with 88% nocturnal clustering"*).
- **Model Traceability**: Specification of the exact model version, feature vector dimensions, and training timestamp.

---

## 5. Demographic & Protected Attributes Neutrality

CrimeNet AI explicitly excludes protected characteristics from its feature vectors:
- No demographic features (race, religion, caste, gender, sexual orientation, political affiliation).
- Feature vectors are strictly behavioral and telemetry-derived (timestamps, transaction amounts, call frequencies, graph topology connectivity).

---

## 6. Synthetic Demo Data Governance

All demonstration datasets in this repository (names, phone numbers, crypto wallet addresses, company entities, cell towers, and GPS coordinates) are **100% synthetic**. They do not represent real individuals, active law-enforcement operations, or living persons.
