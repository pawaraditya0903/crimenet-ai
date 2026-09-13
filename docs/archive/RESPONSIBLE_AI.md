# 🧭 CrimeNet AI — Responsible AI & Human Oversight Charter (RESPONSIBLE_AI.md)

**System Classification:** Human-in-the-Loop Decision Support System for Financial Forensics & Link Analysis  
**Lead Architect:** Aditya Pawar  

---

## 1. Intended Use & Purpose

CrimeNet AI is designed solely as an **advisory decision-support platform** for law enforcement analysts, fraud examiners, and forensic auditors. Its primary objectives are:
1. Identifying hidden statistical patterns across multi-source financial and telecom metadata.
2. Reducing investigative latency by organizing complex records into interactive graphs.
3. Assisting human investigators with interpretable, explainable anomaly breakdowns.

---

## 2. Explicitly Prohibited Uses

The following uses are **strictly prohibited** by design and policy:
* **Autonomous Decision-Making:** CrimeNet AI **cannot and must not** autonomously issue arrest warrants, execute property seizures, or authorize ground tactical operations without independent human authorization.
* **Autonomous Guilt Declarations:** Anomaly scores, PageRank scores, or graph clusterings do not constitute legal proof of guilt or criminal culpability.
* **Predictive Policing / Demographic Profiling:** The platform does not use racial, ethnic, religious, or socioeconomic demographic variables as predictive features.
* **Real-World Unsanctioned Deployment:** In its current demonstration state, CrimeNet AI operates **exclusively on synthetic, fictional benchmark datasets**.

---

## 3. Human-in-the-Loop (HITL) Oversight Workflow

Every alert follows a strict 5-stage human approval lifecycle:

$$\text{Statistical Alert Generated} \longrightarrow \text{Pending Review} \longrightarrow \begin{cases} \text{Confirmed by Investigator} \\ \text{Suppressed as False Positive} \\ \text{Escalated to Supervisor} \end{cases} \longrightarrow \text{Supervisory Authorization}$$

1. **Investigator Review:** An investigator must inspect the Explainable AI (XAI) feature breakdown and enter explanatory audit notes.
2. **False Positive Suppression:** Investigators can suppress normal commercial spikes, dynamically recalibrating the model's contamination parameter ($\nu$).
3. **Supervisory Sign-off:** High-risk tactical recommendations require formal multi-level approval from a supervisory officer.

---

## 4. Explainability & Transparency (XAI Policy)

Black-box scores are strictly prohibited. Every anomaly alert is accompanied by:
* **Trigger Value vs. Historical Baseline:** Clear comparison (e.g., $4.41\times$ above moving average).
* **Plain-English Explanation:** Contextual description of the mathematical anomaly.
* **Confidence & Uncertainty Margins:** Explicit bounds (e.g., $\text{Confidence: HIGH} \pm 0.04$).

---

## 5. Data Minimization & Privacy Protection

* **Synthetic Data Governance:** All names, telephone numbers, bank accounts, vehicle license plates, and narratives within the demonstration environment are 100% fictional.
* **Retention & Deletion Policy:** Records are assigned configurable retention dates, after which metadata is pruned to prevent persistent surveillance drift.
* **Biometric Safety:** Biometric face enrollment is simulated for access control only and is not used for unconstrained public mass facial surveillance.

---

## 6. Statutory Evidentiary Disclaimer

> **Statutory Notice:** Cryptographic hash and Merkle root verification confirms data integrity post-ingestion. It does not independently establish the authenticity, legality of collection, or final judicial admissibility of underlying evidence under Section 63 of Bharatiya Sakshya Adhiniyam 2023 or Section 65B of the Indian Evidence Act. All findings require independent procedural validation by authorized legal authorities.
