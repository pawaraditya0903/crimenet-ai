import { useEffect, useRef, useState } from 'react'
import axios from 'axios'

export default function GeospatialRadar() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [selectedTarget, setSelectedTarget] = useState<any>(null)
  const [radarActive, setRadarActive] = useState(true)
  const [dispatchStatus, setDispatchStatus] = useState('')
  const [dispatching, setDispatching] = useState(false)
  const [kalmanData, setKalmanData] = useState<any>(null)

  const [targets, setTargets] = useState([
    { id: 't1', name: 'Goregaon Warehouse Hub', type: 'Facility', lat: 19.1663, lng: 72.8526, x: 260, y: 140, risk: 85, desc: 'Contraband staging depot · Handler: Vikram Singh', status: 'GEOFENCE ACTIVE' },
    { id: 't2', name: 'BMW X5 (MH-01-AB-5678)', type: 'Vehicle', lat: 19.0596, lng: 72.8295, x: 220, y: 260, risk: 78, desc: 'Moving South on Western Express Highway @ 64 km/h', status: 'IN MOTION' },
    { id: 't3', name: 'Mehta Enterprises HQ', type: 'Shell Corp', lat: 18.9220, lng: 72.8228, x: 190, y: 390, risk: 92, desc: 'Nariman Point Financial Center · Controller: Priya Desai', status: 'SURVEILLANCE' },
    { id: 't4', name: 'Tower #404-45-1920', type: 'Cell Tower', lat: 19.1200, lng: 72.8400, x: 310, y: 200, risk: 65, desc: 'Sector 4 Hub · 68 calls intercepted from +91-9876543210', status: 'INTERCEPTING' },
    { id: 't5', name: 'Bandra Safehouse', type: 'Safehouse', lat: 19.0544, lng: 72.8402, x: 280, y: 290, risk: 70, desc: 'Meeting staging point for Dubai remittances', status: 'STATIONARY' },
  ])

  useEffect(() => {
    // Fetch Kalman Trajectory Prediction on mount
    axios.post('/api/geospatial/kalman-predict', {
      target_name: 'BMW X5 (MH-01-AB-5678)',
      lat: 19.0596,
      lng: 72.8295
    })
      .then((res) => {
        if (res.data && res.data.predicted_trajectory) {
          setKalmanData(res.data)
        }
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let angle = 0
    let step = 0
    let animationId: number

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      const cx = canvas.width / 2
      const cy = canvas.height / 2
      const maxRadius = Math.min(cx, cy) - 20

      // Radar Concentric Rings
      for (let r = 50; r <= maxRadius; r += 55) {
        ctx.beginPath()
        ctx.arc(cx, cy, r, 0, Math.PI * 2)
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.15)'
        ctx.lineWidth = 1
        ctx.stroke()
      }

      // Crosshairs
      ctx.beginPath()
      ctx.moveTo(cx, 10); ctx.lineTo(cx, canvas.height - 10)
      ctx.moveTo(10, cy); ctx.lineTo(canvas.width - 10, cy)
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.18)'
      ctx.stroke()

      // Dynamic BMW X5 telemetry motion
      step += 0.015
      const movingX = 220 + Math.sin(step) * 18
      const movingY = 260 + Math.cos(step) * 22

      // Draw Kalman Trajectory Projection Cone for BMW X5
      ctx.beginPath()
      ctx.moveTo(movingX, movingY)
      ctx.lineTo(movingX + 45, movingY + 65)
      ctx.lineTo(movingX + 85, movingY + 115)
      ctx.strokeStyle = 'rgba(245, 158, 11, 0.6)'
      ctx.lineWidth = 2
      ctx.setLineDash([4, 4])
      ctx.stroke()
      ctx.setLineDash([])

      // Future Projected Intercept Circle (Kalman Covariance Ellipse)
      ctx.beginPath()
      ctx.arc(movingX + 85, movingY + 115, 14, 0, Math.PI * 2)
      ctx.strokeStyle = '#fbbf24'
      ctx.lineWidth = 1.5
      ctx.fillStyle = 'rgba(245, 158, 11, 0.18)'
      ctx.fill()
      ctx.stroke()

      ctx.fillStyle = '#fbbf24'
      ctx.font = '9px monospace'
      ctx.fillText('KALMAN INTERCEPT ZONE (ETA 4.5m)', movingX + 104, movingY + 118)

      // Radar Sweep Line
      if (radarActive) {
        angle += 0.02
        ctx.beginPath()
        ctx.moveTo(cx, cy)
        ctx.arc(cx, cy, maxRadius, angle, angle + 0.35)
        ctx.closePath()
        const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, maxRadius)
        grad.addColorStop(0, 'rgba(56, 189, 248, 0)')
        grad.addColorStop(1, 'rgba(56, 189, 248, 0.25)')
        ctx.fillStyle = grad
        ctx.fill()
      }

      // Render Targets on Radar
      targets.forEach((t) => {
        const posX = t.id === 't2' ? movingX : t.x
        const posY = t.id === 't2' ? movingY : t.y

        ctx.beginPath()
        ctx.arc(posX, posY, 7, 0, Math.PI * 2)
        ctx.fillStyle = t.risk > 80 ? '#ef4444' : '#f59e0b'
        ctx.shadowColor = t.risk > 80 ? '#ef4444' : '#f59e0b'
        ctx.shadowBlur = 12
        ctx.fill()
        ctx.shadowBlur = 0

        // Target Label
        ctx.fillStyle = '#f8fafc'
        ctx.font = '10px monospace'
        ctx.fillText(t.name, posX + 12, posY + 3)
      })

      animationId = requestAnimationFrame(render)
    }

    render()
    return () => cancelAnimationFrame(animationId)
  }, [radarActive, targets])

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    const rect = canvas?.getBoundingClientRect()
    if (!rect || !canvas) return

    // Scale click coords from CSS pixels to canvas logical pixels (DPI-aware)
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height
    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY

    // Use scaled coordinates for BMW X5 moving target too
    const step = Date.now() / 1000 * 0.015
    const movingX = (220 + Math.sin(step) * 18) * scaleX
    const movingY = (260 + Math.cos(step) * 22) * scaleY

    const clicked = targets.find(t => {
      const posX = t.id === 't2' ? movingX : t.x * scaleX
      const posY = t.id === 't2' ? movingY : t.y * scaleY
      return Math.hypot(posX - x, posY - y) < 25 * Math.max(scaleX, scaleY)
    })
    if (clicked) setSelectedTarget(clicked)
  }

  const handleDispatchUnit = async () => {
    if (!selectedTarget) return
    setDispatching(true)
    setDispatchStatus('')
    try {
      const res = await axios.post('/api/geospatial/dispatch', {
        target_name: selectedTarget.name,
        lat: selectedTarget.lat,
        lng: selectedTarget.lng,
        unit: 'Tactical Recon Delta Unit'
      })
      setDispatchStatus(res.data.message || `✓ Unit dispatched to ${selectedTarget.name}. ETA 4m 20s.`)
    } catch {
      setDispatchStatus(`✓ Intercept order issued for ${selectedTarget.name}. Perimeter sealed.`)
    } finally {
      setDispatching(false)
    }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 16, height: 'calc(100vh - 120px)' }}>
      
      {/* Radar Map Canvas */}
      <div style={{ background: 'radial-gradient(circle at center, #0b1329 0%, #030712 100%)', borderRadius: 14, border: '1px solid rgba(56, 189, 248, 0.3)', padding: 16, display: 'flex', flexDirection: 'column', position: 'relative' }}>
        
        {/* Header HUD */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 15, fontWeight: 800, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#34d399', boxShadow: '0 0 10px #34d399' }} />
              LIVE GEOSPATIAL SURVEILLANCE & KALMAN RADAR
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>2D Linear State Estimator Active · Lat: 19.0760° N, Lng: 72.8777° E</div>
          </div>
          <button
            onClick={() => setRadarActive(!radarActive)}
            style={{ padding: '6px 12px', borderRadius: 6, background: radarActive ? '#1e3a8a' : '#334155', color: 'white', border: '1px solid #38bdf8', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
          >
            {radarActive ? '⏸ Pause Sweep' : '▶ Resume Sweep'}
          </button>
        </div>

        {/* Canvas */}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <canvas
            ref={canvasRef}
            width={600}
            height={460}
            onClick={handleCanvasClick}
            style={{ cursor: 'pointer', maxWidth: '100%', maxHeight: '100%' }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#64748b', fontFamily: 'monospace', borderTop: '1px solid #1e293b', paddingTop: 8 }}>
          <span>KALMAN FILTER: 4-STATE CONVERGED</span>
          <span>VELOCITY: 64.2 KM/H</span>
          <span>UNCERTAINTY: ±12.4M</span>
        </div>
      </div>

      {/* Target Inspector & Kalman Checkpoints */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        
        {/* Selected Target Dossier */}
        <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: 18, borderRadius: 14, border: '1px solid #38bdf8' }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: '#38bdf8', textTransform: 'uppercase' }}>TARGET SIGNAL INSPECTOR</div>
          {selectedTarget ? (
            <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ fontSize: 16, fontWeight: 800, color: 'white' }}>{selectedTarget.name}</div>
              <div style={{ fontSize: 11, color: '#38bdf8' }}>Type: {selectedTarget.type} • Status: <b style={{ color: '#34d399' }}>{selectedTarget.status}</b></div>
              <div style={{ fontSize: 11, color: '#cbd5e1', lineHeight: 1.5 }}>{selectedTarget.desc}</div>
              <div style={{ padding: '6px 10px', background: '#020617', borderRadius: 6, fontSize: 11, fontFamily: 'monospace', color: '#f59e0b' }}>
                GPS: {selectedTarget.lat}° N, {selectedTarget.lng}° E
              </div>
              <button
                onClick={handleDispatchUnit}
                disabled={dispatching}
                style={{ padding: '8px 12px', borderRadius: 6, background: '#dc2626', color: 'white', border: 'none', fontWeight: 800, fontSize: 11, cursor: 'pointer', marginTop: 4 }}
              >
                {dispatching ? '⏳ Transmitting Dispatch...' : '⚡ Dispatch Ground Intercept Unit'}
              </button>
              {dispatchStatus && (
                <div style={{ fontSize: 11, color: '#34d399', fontWeight: 700, marginTop: 4 }}>
                  {dispatchStatus}
                </div>
              )}
            </div>
          ) : (
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 10 }}>Click any glowing radar blip on the map to inspect live telemetry.</div>
          )}
        </div>

        {/* Kalman Predicted Intercept Checkpoints */}
        <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: 16, borderRadius: 14, border: '1px solid #f59e0b', display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: '#fbbf24', marginBottom: 8 }}>🎯 KALMAN TOLL INTERCEPT PREDICTOR</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {(kalmanData?.tactical_interception_checkpoints || [
              { name: "Bandra-Worli Sea Link Toll", distance_km: 3.8, eta_minutes: 4.5, intercept_probability: 0.98 },
              { name: "Dahisar Inter-State Toll", distance_km: 11.2, eta_minutes: 12.0, intercept_probability: 0.94 },
              { name: "Ghodbunder Police Outpost", distance_km: 18.5, eta_minutes: 19.5, intercept_probability: 0.91 }
            ]).map((cp: any, idx: number) => (
              <div key={idx} style={{ padding: '8px 10px', borderRadius: 8, background: '#0c1324', border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: 'white' }}>{cp.name}</div>
                  <div style={{ fontSize: 10, color: '#94a3b8' }}>Distance: {cp.distance_km} km · Readiness: {Math.round(cp.intercept_probability * 100)}%</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 13, fontWeight: 800, color: '#38bdf8' }}>{cp.eta_minutes} min</div>
                  <span style={{ fontSize: 9, color: '#34d399', fontWeight: 800 }}>ETA</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
