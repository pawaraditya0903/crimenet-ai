import { useEffect, useState } from 'react'
import axios from 'axios'

export default function AlertCentre() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [selAlert, setSelAlert] = useState<any>(null)
  const [statusMsg, setStatusMsg] = useState('')
  const [calibration, setCalibration] = useState<any>({
    decision_boundary: 0.82,
    contamination: 0.03,
    confirmed_threats: 3,
    false_positives: 0,
    last_updated: 'Live Engine Active'
  })

  useEffect(() => {
    axios.get('/api/alerts').then(r => {
      setAlerts(r.data.alerts || [])
      if (r.data.calibration) setCalibration(r.data.calibration)
    })
  }, [])

  const handleVerify = async (id: string) => {
    const res = await axios.post(`/api/alerts/${id}/verify`)
    if (res.data.calibration) setCalibration(res.data.calibration)
    setStatusMsg(`✓ Alert ${id} confirmed as REAL THREAT. Decision boundary updated to ${res.data.calibration?.decision_boundary || 0.84}!`)
    setTimeout(() => setStatusMsg(''), 3500)
    setSelAlert(null)
  }

  const handleFalsePositive = async (id: string) => {
    const res = await axios.post(`/api/alerts/${id}/false-positive`)
    if (res.data.calibration) setCalibration(res.data.calibration)
    setAlerts(alerts.filter(a => a.id !== id))
    setStatusMsg(`✓ Alert ${id} marked as False Positive. Contamination rate adjusted to ${res.data.calibration?.contamination || 0.025}.`)
    setTimeout(() => setStatusMsg(''), 3500)
    setSelAlert(null)
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800, color: 'white' }}>🚨 Human-in-the-Loop (HITL) Anomaly Alert Centre</h2>
          <p style={{ fontSize: 12, color: '#94a3b8' }}>Review Isolation Forest outlier vectors and refine ML decision boundaries with active feedback.</p>
        </div>
        {statusMsg && <div style={{ fontSize: 11, color: '#34d399', fontWeight: 700 }}>{statusMsg}</div>}
      </div>

      {/* HITL Calibration Telemetry Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
        <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.85)', borderRadius: 8, border: '1px solid #38bdf8' }}>
          <div style={{ fontSize: 9.5, color: '#94a3b8', textTransform: 'uppercase' }}>DECISION BOUNDARY</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#38bdf8' }}>{calibration.decision_boundary}</div>
          <div style={{ fontSize: 9.5, color: '#64748b' }}>Isolation Forest Threshold</div>
        </div>

        <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.85)', borderRadius: 8, border: '1px solid #f59e0b' }}>
          <div style={{ fontSize: 9.5, color: '#94a3b8', textTransform: 'uppercase' }}>CONTAMINATION RATE</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#f59e0b' }}>{calibration.contamination}</div>
          <div style={{ fontSize: 9.5, color: '#64748b' }}>Outlier Priors</div>
        </div>

        <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.85)', borderRadius: 8, border: '1px solid #ef4444' }}>
          <div style={{ fontSize: 9.5, color: '#94a3b8', textTransform: 'uppercase' }}>CONFIRMED THREATS</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#ef4444' }}>{calibration.confirmed_threats}</div>
          <div style={{ fontSize: 9.5, color: '#64748b' }}>Active Warrants</div>
        </div>

        <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.85)', borderRadius: 8, border: '1px solid #10b981' }}>
          <div style={{ fontSize: 9.5, color: '#94a3b8', textTransform: 'uppercase' }}>FALSE POSITIVES</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: '#10b981' }}>{calibration.false_positives}</div>
          <div style={{ fontSize: 9.5, color: '#64748b' }}>Suppressed Signals</div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {alerts.map((a) => (
          <div
            key={a.id}
            onClick={() => setSelAlert(a)}
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
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ padding: '2px 8px', borderRadius: 4, background: a.severity === 'critical' ? '#ef4444' : '#f59e0b', color: 'white', fontSize: 10, fontWeight: 800 }}>
                  {a.severity.toUpperCase()}
                </span>
                <span style={{ fontSize: 14, fontWeight: 800, color: 'white' }}>{a.entity_name}</span>
                <span style={{ fontSize: 11, color: '#94a3b8' }}>({a.anomaly_type})</span>
              </div>
              <div style={{ fontSize: 12, color: '#cbd5e1', marginTop: 4 }}>{a.details}</div>
            </div>
            
            <div style={{ display: 'flex', gap: 6 }}>
              <button
                onClick={(e) => { e.stopPropagation(); handleVerify(a.id); }}
                style={{ padding: '6px 10px', borderRadius: 6, background: '#10b981', color: 'white', border: 'none', fontWeight: 700, fontSize: 10.5, cursor: 'pointer' }}
              >
                ✓ Confirm Threat
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); handleFalsePositive(a.id); }}
                style={{ padding: '6px 10px', borderRadius: 6, background: '#334155', color: '#cbd5e1', border: 'none', fontWeight: 700, fontSize: 10.5, cursor: 'pointer' }}
              >
                False Positive
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Incident Modal */}
      {selAlert && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ width: '90vw', maxWidth: 620, background: '#0f172a', border: '1px solid #ef4444', borderRadius: 14, padding: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 10 }}>
              <div style={{ fontSize: 16, fontWeight: 800, color: '#ef4444' }}>🚨 INCIDENT VERIFICATION: {selAlert.entity_name}</div>
              <button onClick={() => setSelAlert(null)} style={{ background: '#334155', border: 'none', color: 'white', padding: '4px 10px', borderRadius: 6, cursor: 'pointer' }}>✕</button>
            </div>
            <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 10, fontSize: 12, color: '#cbd5e1' }}>
              <div><b>Anomaly Vector:</b> {selAlert.anomaly_type}</div>
              <div><b>Isolation Forest Score:</b> <span style={{ color: '#ef4444', fontWeight: 800 }}>{Math.round(selAlert.anomaly_score * 100)}% Outlier Confidence</span></div>
              <div><b>Details:</b> {selAlert.details}</div>
              <div style={{ background: '#020617', padding: 10, borderRadius: 8, fontSize: 11, color: '#38bdf8' }}>
                <b>Human-In-The-Loop Active Learning:</b> Confirming this alert trains the system to penalize similar nocturnal transfers across shell company accounts.
              </div>
            </div>
            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button onClick={() => handleVerify(selAlert.id)} style={{ flex: 1, padding: 10, borderRadius: 8, background: '#dc2626', color: 'white', border: 'none', fontWeight: 800, cursor: 'pointer' }}>⚡ Confirm Real Threat & Issue Warrant</button>
              <button onClick={() => handleFalsePositive(selAlert.id)} style={{ padding: '10px 16px', borderRadius: 8, background: '#334155', color: '#cbd5e1', border: 'none', cursor: 'pointer' }}>Mark False Positive</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
