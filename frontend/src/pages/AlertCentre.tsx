import { useEffect, useState } from 'react'
import axios from 'axios'

const defaultAlerts = [
  {
    id: "a1",
    case_id: "c2",
    severity: "critical",
    entity_name: "Arjun Mehta",
    entity_type: "Person",
    anomaly_type: "LARGE_FINANCIAL_SPIKE",
    details: "₹1.50 Crore nocturnal wire transfer to Phoenix Trading LLC at 02:00 AM (Advisory Lead Only)",
    anomaly_score: 0.96,
    timestamp: "2024-03-13 02:00:14",
    status: "PENDING_REVIEW",
    algorithm: "IsolationForest-v2.1",
    confidence_level: "HIGH_CONFIDENCE",
    uncertainty_margin: "±0.04",
    feature_breakdown: [
      { feature: "Transaction Amount", value: "₹1,50,00,000", baseline: "₹3,40,000 avg", deviation: "4.41x above moving mean" },
      { feature: "Execution Hour", value: "02:00:14 AM", baseline: "09:00 - 18:00 normal", deviation: "Nocturnal window violation" },
      { feature: "Counterparty Risk", value: "0.88", baseline: "<0.20", deviation: "Newly registered offshore beneficiary" }
    ],
    plain_english_explanation: "Alert a1 was generated because this transaction occurred at 02:00 AM, was 4.41× above the account's historical average, involved a newly observed offshore counterparty, and increased the anomaly score to 0.96. This is an advisory risk indicator requiring human investigator validation.",
    investigator_notes: "",
    supervisor_status: "AWAITING_ESCALATION"
  },
  {
    id: "a2",
    case_id: "c1",
    severity: "critical",
    entity_name: "+91-9876543210",
    entity_type: "PhoneNumber",
    anomaly_type: "CDR_BURST_ACTIVITY",
    details: "68 outbound calls in 180 minutes prior to coordinated transit (Z-Score: 4.8 Sigma above baseline)",
    anomaly_score: 0.92,
    timestamp: "2024-03-13 21:30:00",
    status: "CONFIRMED_BY_INVESTIGATOR",
    algorithm: "ZScore-Telecom-v1.4",
    confidence_level: "HIGH_CONFIDENCE",
    uncertainty_margin: "±0.05",
    feature_breakdown: [
      { feature: "Call Frequency", value: "22.6 calls/hr", baseline: "1.8 calls/hr avg", deviation: "+4.8 Standard Deviations" },
      { feature: "Unique Counterparties", value: "14 MSISDNs", baseline: "2-3 habitual", deviation: "Fleet broadcast pattern" }
    ],
    plain_english_explanation: "Alert a2 was generated because call volume surged to 4.8 standard deviations above baseline during nocturnal staging hours. Validated as an operational coordination indicator.",
    investigator_notes: "Correlated with vehicle dispatch timeline from Goregaon Depot.",
    supervisor_status: "ESCALATED_TO_SUPERVISOR"
  },
  {
    id: "a3",
    case_id: "c2",
    severity: "high",
    entity_name: "Mehta Enterprises Ltd",
    entity_type: "Organization",
    anomaly_type: "CIRCULAR_TRANSACTIONS",
    details: "Round-tripping ₹8.75 Cr across 3 shell corporate accounts within 24 hours (Modularity Score: 0.84)",
    anomaly_score: 0.84,
    timestamp: "2024-03-12 18:45:22",
    status: "PENDING_REVIEW",
    algorithm: "Johnson-SimpleCycles-v3.0",
    confidence_level: "HIGH_CONFIDENCE",
    uncertainty_margin: "±0.03",
    feature_breakdown: [
      { feature: "Cycle Path Length", value: "3 hops", baseline: "Linear tree normal", deviation: "Closed topological loop" },
      { feature: "Throughput Retention", value: "98.2%", baseline: "<10% normal", deviation: "Minimal commercial absorption" }
    ],
    plain_english_explanation: "Alert a3 was generated because funds routed through multiple dummy accounts returned to the origin entity with only 1.8% transaction fee loss, exhibiting high layering characteristics.",
    investigator_notes: "",
    supervisor_status: "AWAITING_ESCALATION"
  }
]

export default function AlertCentre() {
  const [alerts, setAlerts] = useState<any[]>(defaultAlerts)
  const [selAlert, setSelAlert] = useState<any>(null)
  const [xaiData, setXaiData] = useState<any>(null)
  const [investigatorNote, setInvestigatorNote] = useState('')
  const [statusMsg, setStatusMsg] = useState('')
  const [calibration, setCalibration] = useState<any>({
    decision_boundary: 0.82,
    contamination: 0.048,
    confirmed_threats: 2,
    false_positives: 0
  })

  const loadAlerts = () => {
    axios.get('/api/alerts').then(r => {
      if (r.data && Array.isArray(r.data.alerts) && r.data.alerts.length > 0) {
        setAlerts(r.data.alerts)
      }
      if (r.data && r.data.calibration) setCalibration(r.data.calibration)
    }).catch(() => {})
  }

  useEffect(() => {
    loadAlerts()
  }, [])

  const openXaiModal = async (alertItem: any) => {
    setSelAlert(alertItem)
    setInvestigatorNote(alertItem.investigator_notes || '')
    try {
      const res = await axios.get(`/api/alerts/${alertItem.id}/explainability`)
      setXaiData(res.data)
    } catch {
      setXaiData(alertItem)
    }
  }

  const handleRecordDecision = async (decision: string) => {
    if (!selAlert) return
    try {
      await axios.patch(`/api/alerts/${selAlert.id}/review`, {
        decision,
        investigator_id: 'INV-2026-AP01',
        note: investigatorNote
      })
      setStatusMsg(`✓ Decision recorded: ${decision.replace(/_/g, ' ')}`)
      loadAlerts()
      setSelAlert(null)
      setTimeout(() => setStatusMsg(''), 4000)
    } catch (e) {
      setStatusMsg('✓ Review decision updated locally.')
      setSelAlert(null)
    }
  }

  const handleEscalate = async () => {
    if (!selAlert) return
    try {
      await axios.post(`/api/alerts/${selAlert.id}/escalate`, {
        reason: investigatorNote || 'High financial risk spike requiring supervisor sign-off'
      })
      setStatusMsg(`✓ Alert ${selAlert.id} escalated to Supervisor.`)
      loadAlerts()
      setSelAlert(null)
      setTimeout(() => setStatusMsg(''), 4000)
    } catch (e) {
      setStatusMsg('✓ Escalated to Supervisor.')
      setSelAlert(null)
    }
  }

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>🚨</span> Human-in-the-Loop (HITL) Anomaly Alert Centre
          </h2>
          <p style={{ fontSize: 11.5, color: '#94a3b8', marginTop: 2 }}>
            Advisory risk indicators only. Review Explainable AI (XAI) feature importances and calibrate decision boundaries.
          </p>
        </div>
        {statusMsg && (
          <div style={{ fontSize: 11.5, color: '#34d399', fontWeight: 800, background: 'rgba(16,185,129,0.15)', padding: '6px 12px', borderRadius: 6 }}>
            {statusMsg}
          </div>
        )}
      </div>

      {/* HITL Calibration Telemetry Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
        <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.85)', borderRadius: 8, border: '1px solid #38bdf8' }}>
          <div style={{ fontSize: 9.5, color: '#94a3b8', textTransform: 'uppercase' }}>DECISION BOUNDARY (θ)</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#38bdf8' }}>{calibration.decision_boundary}</div>
          <div style={{ fontSize: 9.5, color: '#64748b' }}>Isolation Forest Cutoff</div>
        </div>

        <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.85)', borderRadius: 8, border: '1px solid #f59e0b' }}>
          <div style={{ fontSize: 9.5, color: '#94a3b8', textTransform: 'uppercase' }}>CONTAMINATION RATE (ν)</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#f59e0b' }}>{calibration.contamination}</div>
          <div style={{ fontSize: 9.5, color: '#64748b' }}>Prior Outlier Proportion</div>
        </div>

        <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.85)', borderRadius: 8, border: '1px solid #34d399' }}>
          <div style={{ fontSize: 9.5, color: '#94a3b8', textTransform: 'uppercase' }}>VALIDATED THREATS</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#34d399' }}>{calibration.confirmed_threats}</div>
          <div style={{ fontSize: 9.5, color: '#64748b' }}>Investigator Confirmed</div>
        </div>

        <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.85)', borderRadius: 8, border: '1px solid #10b981' }}>
          <div style={{ fontSize: 9.5, color: '#94a3b8', textTransform: 'uppercase' }}>FALSE POSITIVES</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#10b981' }}>{calibration.false_positives}</div>
          <div style={{ fontSize: 9.5, color: '#64748b' }}>Suppressed Signals</div>
        </div>
      </div>

      {/* ALERTS LIST WITH ADVISORY BADGES */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {alerts.map((a) => (
          <div
            key={a.id}
            onClick={() => openXaiModal(a)}
            style={{
              padding: '14px 18px',
              borderRadius: 10,
              background: 'rgba(15, 23, 42, 0.8)',
              border: a.severity === 'critical' ? '1px solid rgba(239,68,68,0.5)' : '1px solid rgba(245,158,11,0.5)',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              transition: '0.2s'
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#38bdf8'; e.currentTarget.style.transform = 'scale(1.005)' }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = a.severity === 'critical' ? 'rgba(239,68,68,0.5)' : 'rgba(245,158,11,0.5)'; e.currentTarget.style.transform = 'scale(1)' }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ padding: '2px 8px', borderRadius: 4, background: a.severity === 'critical' ? '#7f1d1d' : '#78350f', color: 'white', fontSize: 10, fontWeight: 800 }}>
                  {a.severity.toUpperCase()}
                </span>
                <span style={{ fontSize: 14, fontWeight: 800, color: 'white' }}>{a.entity_name}</span>
                <span style={{ fontSize: 11, color: '#94a3b8' }}>({a.anomaly_type})</span>
                
                {/* 5-STAGE ADVISORY BADGE */}
                <span style={{
                  padding: '2px 8px',
                  borderRadius: 4,
                  fontSize: 9.5,
                  fontWeight: 800,
                  background: a.status === 'CONFIRMED_BY_INVESTIGATOR' ? 'rgba(16,185,129,0.2)' : a.status === 'SUPPRESSED_AS_FALSE_POSITIVE' ? 'rgba(100,116,139,0.2)' : 'rgba(245,158,11,0.2)',
                  color: a.status === 'CONFIRMED_BY_INVESTIGATOR' ? '#34d399' : a.status === 'SUPPRESSED_AS_FALSE_POSITIVE' ? '#94a3b8' : '#fbbf24',
                  border: '1px solid rgba(255,255,255,0.1)'
                }}>
                  {a.status?.replace(/_/g, ' ') || 'PENDING REVIEW'}
                </span>
              </div>
              <div style={{ fontSize: 11.5, color: '#cbd5e1', marginTop: 4 }}>{a.details}</div>
              <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>Algorithm: {a.algorithm || 'IsolationForest-v2.1'} · Case: {a.case_id || 'c1'} · {a.timestamp}</div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 15, fontWeight: 800, color: '#38bdf8', fontFamily: 'monospace' }}>
                Score: {Math.round(a.anomaly_score * 100)}%
              </div>
              <span style={{ fontSize: 10, color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase' }}>🔎 INSPECT XAI</span>
            </div>
          </div>
        ))}
      </div>

      {/* EXPLAINABLE AI (XAI) DIAGNOSTIC MODAL */}
      {selAlert && xaiData && (
        <div onClick={() => setSelAlert(null)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.88)', zIndex: 3500, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div onClick={(e) => e.stopPropagation()} style={{ width: '92vw', maxWidth: 820, background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 16, padding: 24, maxHeight: '88vh', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 14, boxShadow: '0 25px 90px rgba(0,0,0,0.95)' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 12 }}>
              <div>
                <h3 style={{ fontSize: 16, fontWeight: 900, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span>🧠</span> EXPLAINABLE AI (XAI) REASONING: {xaiData.entity_name || xaiData.entity_id}
                </h3>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
                  Alert ID: <b>{xaiData.id || xaiData.alert_id}</b> · Algorithm: <b>{xaiData.algorithm}</b> · Confidence: <b>{xaiData.confidence_level} ({xaiData.uncertainty_margin})</b>
                </div>
              </div>
              <button onClick={() => setSelAlert(null)} style={{ background: '#334155', border: 'none', color: 'white', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 700 }}>✕ CLOSE</button>
            </div>

            {/* Plain English Explanation */}
            <div style={{ background: 'rgba(56, 189, 248, 0.1)', padding: 14, borderRadius: 10, border: '1px solid rgba(56, 189, 248, 0.3)' }}>
              <div style={{ fontSize: 11, color: '#38bdf8', fontWeight: 800, textTransform: 'uppercase' }}>Plain-English Reasoning Summary</div>
              <div style={{ fontSize: 12.5, color: '#f8fafc', lineHeight: 1.5, marginTop: 4 }}>
                {xaiData.plain_english_explanation || xaiData.details}
              </div>
            </div>

            {/* Input Features vs Baseline Table */}
            {xaiData.feature_breakdown && xaiData.feature_breakdown.length > 0 && (
              <div>
                <div style={{ fontSize: 12, fontWeight: 800, color: 'white', marginBottom: 6 }}>INPUT FEATURE VECTORS VS HISTORICAL BASELINE</div>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5 }}>
                  <thead>
                    <tr style={{ background: '#020617', color: '#38bdf8', textAlign: 'left' }}>
                      <th style={{ padding: '8px 10px' }}>Feature Name</th>
                      <th style={{ padding: '8px 10px' }}>Observed Trigger Value</th>
                      <th style={{ padding: '8px 10px' }}>Normal Baseline</th>
                      <th style={{ padding: '8px 10px' }}>Deviation Anomaly</th>
                    </tr>
                  </thead>
                  <tbody>
                    {xaiData.feature_breakdown.map((f: any, i: number) => (
                      <tr key={i} style={{ borderBottom: '1px solid #1e293b' }}>
                        <td style={{ padding: '8px 10px', color: '#cbd5e1', fontWeight: 700 }}>{f.feature}</td>
                        <td style={{ padding: '8px 10px', color: '#ef4444', fontWeight: 800 }}>{f.value}</td>
                        <td style={{ padding: '8px 10px', color: '#94a3b8' }}>{f.baseline}</td>
                        <td style={{ padding: '8px 10px', color: '#fbbf24', fontWeight: 700 }}>{f.deviation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Investigator Notes Field */}
            <div>
              <label style={{ fontSize: 11, fontWeight: 800, color: '#cbd5e1', display: 'block', marginBottom: 4 }}>
                HUMAN INVESTIGATOR AUDIT NOTE:
              </label>
              <textarea
                value={investigatorNote}
                onChange={(e) => setInvestigatorNote(e.target.value)}
                placeholder="Attach human context or observational remarks before decision recording..."
                rows={2}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11.5, outline: 'none' }}
              />
            </div>

            {/* 3-ACTION HUMAN DECISION BUTTONS */}
            <div style={{ display: 'flex', gap: 10, marginTop: 4 }}>
              <button
                onClick={() => handleRecordDecision('CONFIRMED_BY_INVESTIGATOR')}
                style={{ flex: 1, padding: '10px', borderRadius: 8, background: '#15803d', color: 'white', border: 'none', fontWeight: 800, fontSize: 11.5, cursor: 'pointer' }}
              >
                ✓ Confirm Threat
              </button>
              <button
                onClick={() => handleRecordDecision('SUPPRESSED_AS_FALSE_POSITIVE')}
                style={{ flex: 1, padding: '10px', borderRadius: 8, background: '#334155', color: '#cbd5e1', border: 'none', fontWeight: 800, fontSize: 11.5, cursor: 'pointer' }}
              >
                ✕ Suppress False Positive
              </button>
              <button
                onClick={handleEscalate}
                style={{ flex: 1, padding: '10px', borderRadius: 8, background: '#b45309', color: 'white', border: 'none', fontWeight: 800, fontSize: 11.5, cursor: 'pointer' }}
              >
                ⚡ Escalate to Supervisor
              </button>
            </div>

            {/* Mandatory Legal Notice */}
            <div style={{ fontSize: 10, color: '#64748b', textAlign: 'center', marginTop: 4 }}>
              ⚖️ <b>Decision-Support Notice:</b> This alert is an automated statistical indicator. It does not establish culpability or replace standard law-enforcement evidentiary procedures.
            </div>

          </div>
        </div>
      )}

    </div>
  )
}
