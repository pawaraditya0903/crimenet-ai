# 🤖 CrimeNet Copilot — Intelligence Assistant Manual (COPILOT_GUIDE.md)

**System Classification:** Voice-Enabled Forensic Decision-Support Assistant  
**Lead Architect:** Aditya Pawar  

---

## 1. Executive Summary

**CrimeNet Copilot** is a voice-enabled conversational AI assistant designed for law enforcement analysts and financial investigators. It operates in a secure decision-support capacity, querying graph network topology, calculating shortest link paths, retrieving Explainable AI (XAI) feature breakdowns, and preparing case review drafts.

---

## 2. Voice & Audio Interaction (Web Speech API)

* **Voice Input:** Uses the standard browser `SpeechRecognition` / `webkitSpeechRecognition` API. Click the 🎤 microphone button or use push-to-talk.
* **Waveform HUD:** An animated canvas sine wave responds in real time to audio states (*Listening*, *Speaking*, *Idle*).
* **SpeechSynthesis Output:** Auto-reads analytical answers aloud with rate and voice customization.
* **Stop Control:** Instant ⏹ Stop button cancels audio output immediately.

---

## 3. Safe Internal Tool-Calling Pipeline

CrimeNet Copilot uses a deterministic rule-based tool-calling engine:

| Tool Function | Permission Tier | Output Type |
| :--- | :--- | :--- |
| `get_case_summary(case_id)` | Read-Only | Case overview, priority, entities, and active alert counts. |
| `get_case_alerts(case_id)` | Read-Only | List of flagged risk indicators and advisory scores. |
| `get_alert_explanation(alert_id)` | Read-Only | Isolation Forest trigger features vs historical baselines. |
| `get_entity_profile(query)` | Read-Only | Composite threat score, linked MSISDN, and 1-hop associates. |
| `find_shortest_graph_path(src, tgt)` | Read-Only | NetworkX shortest path traversal connecting 2 entities. |
| `draft_case_briefing(case_id)` | Draft Generator | Executive briefing requiring investigator review. |
| `draft_supervisor_escalation(alert_id)`| Draft Generator | Formal memo requiring supervisor sign-off. |
| `start_demo_simulation()` | Control | Engages live synthetic event stream. |

---

## 4. Citation & Evidence Provenance

Every Copilot response embeds structured provenance citations:
* `[Case: c1]`
* `[Evidence: ev-01]`
* `[Alert: a1]`
* `[Entity: Arjun Mehta]`

Clicking any citation in the Copilot drawer automatically shifts focus to that record in the relevant module.

---

## 5. Human-in-the-Loop Safety Constraints

1. **Non-Autonomous Enforcement:** Copilot cannot independently issue warrants, alter case stages, or execute seizures.
2. **Action Confirmation Modals:** Any command modifying case state generates a **Draft Preview Modal** requiring explicit human authorization.
3. **Audit Logging:** Every query, tool execution, and user confirmation is cryptographically timestamped in `crimenet.db`.
