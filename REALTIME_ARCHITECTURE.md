# 📡 CrimeNet AI — Real-Time Event Architecture (REALTIME_ARCHITECTURE.md)

**System Classification:** Real-Time Decision-Support & Event-Streaming Engine  
**Lead Architect:** Aditya Pawar  
**Protocol:** Async ASGI Socket.IO & WebSocket Dual Channel  

---

## 1. Architectural Overview

CrimeNet AI employs an asynchronous Socket.IO engine implemented in FastAPI via `python-socketio (async_mode="asgi")`. The engine manages room subscriptions partitioned by `case_id`, preventing data leakage across sensitive multi-jurisdiction cases.

```
┌─────────────────────────┐          Socket.IO Channel          ┌───────────────────────────┐
│     FastAPI Backend     │ ─────────────────────────────────> │ React 18 Command Center   │
│  (Simulation Streamer   │ <───────────────────────────────── │ (AppShell, Radar, Telecom │
│   & Anomaly Evaluator)  │       Room: "case_c1", etc.        │  Hawala, Copilot Drawer)  │
└─────────────────────────┘                                    └───────────────────────────┘
```

---

## 2. Event Types & Typed Payloads

All events emitted across the bus adhere to the following payload schema:

```json
{
  "event_id": "evt-1740571200000-842",
  "event_type": "RADAR_POSITION_UPDATED",
  "timestamp_utc": "2026-08-26 12:15:30 UTC",
  "case_id": "c3",
  "actor_id": "SYSTEM_AUTOMATION",
  "severity": "warning",
  "payload": {
    "target_name": "BMW X5 (MH-01-AB-5678)",
    "lat": 19.0624,
    "lng": 72.8312,
    "speed_kmh": 68.4,
    "heading_deg": 42.5,
    "uncertainty_m": 12.4,
    "nearest_checkpoint": "Bandra-Worli Toll Plaza"
  }
}
```

### Core Event Taxonomy

| Event Type | Room Scope | Severity | Trigger Description |
| :--- | :--- | :--- | :--- |
| `RADAR_POSITION_UPDATED` | `case_c3` | `warning` | 2D Kalman-filtered simulated vehicle telemetry coordinate update. |
| `FINANCIAL_ANOMALY_DETECTED` | `case_c2` | `critical` | Sub-₹50,000 PMLA structured smurfing transaction detected across mule layer. |
| `TELECOM_BURST_DETECTED` | `case_c1` | `warning` | Cellular call spike (>3.8 $\sigma$) recorded on burner MSISDN. |
| `ALERT_CREATED` | Global / Case | `critical` | Unsupervised Isolation Forest outlier detected. |
| `EVIDENCE_VERIFIED` | Case | `info` | SHA-256 Merkle tree integrity verification confirmed intact. |
| `COPILOT_MESSAGE` | User Session | `info` | Real-time conversational streaming response from CrimeNet Copilot. |
| `SYSTEM_NOTIFICATION` | Global | `info` | Background simulation status changed (Start, Pause, Speed). |

---

## 3. Room Subscription & RBAC Isolation

1. **Client Join:** When an investigator selects a case in the UI, the frontend emits:
   ```javascript
   socket.emit('join_case_room', { case_id: 'c1' })
   ```
2. **Backend Validation:** The server verifies investigator clearance for `c1` before executing `sio.enter_room(sid, "case_c1")`.
3. **Room Isolation:** Telemetry destined for `case_c2` is broadcast exclusively to `case_c2` subscribers, ensuring complete data containment.

---

## 4. Live Simulation Stream Controls

The background telemetry loop simulates continuous real-world data generation for demonstrations:
* `POST /api/simulation/start`: Engages real-time event generation.
* `POST /api/simulation/pause`: Halts event generation.
* `POST /api/simulation/speed`: Sets speed multiplier ($1\times, 2\times, 5\times$).
* `POST /api/simulation/reset`: Resets event counter.
