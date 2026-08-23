import { useEffect, useRef, useState } from 'react'

export default function GeospatialRadar() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [selectedTarget, setSelectedTarget] = useState<any>(null)
  const [radarActive, setRadarActive] = useState(true)

  const TARGETS = [
    { id: 't1', name: 'Goregaon Warehouse Hub', type: 'Facility', lat: 19.1663, lng: 72.8526, x: 260, y: 140, risk: 85, desc: 'Contraband staging depot · Handler: Vikram Singh', status: 'GEOFENCE ACTIVE' },
    { id: 't2', name: 'BMW X5 (MH-01-AB-5678)', type: 'Vehicle', lat: 19.0596, lng: 72.8295, x: 220, y: 260, risk: 78, desc: 'Moving South on Western Express Highway @ 64 km/h', status: 'IN MOTION' },
    { id: 't3', name: 'Mehta Enterprises HQ', type: 'Shell Corp', lat: 18.9220, lng: 72.8228, x: 190, y: 390, risk: 92, desc: 'Nariman Point Financial Center · Controller: Priya Desai', status: 'SURVEILLANCE' },
    { id: 't4', name: 'Tower #404-45-1920', type: 'Cell Tower', lat: 19.1200, lng: 72.8400, x: 310, y: 200, risk: 65, desc: 'Sector 4 Hub · 68 calls intercepted from +91-9876543210', status: 'INTERCEPTING' },
    { id: 't5', name: 'Bandra Safehouse', type: 'Safehouse', lat: 19.0544, lng: 72.8402, x: 280, y: 290, risk: 70, desc: 'Meeting staging point for Dubai remittances', status: 'STATIONARY' },
  ]

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let angle = 0
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
      TARGETS.forEach((t) => {
        ctx.beginPath()
        ctx.arc(t.x, t.y, 7, 0, Math.PI * 2)
        ctx.fillStyle = t.risk > 80 ? '#ef4444' : '#f59e0b'
        ctx.shadowColor = t.risk > 80 ? '#ef4444' : '#f59e0b'
        ctx.shadowBlur = 12
        ctx.fill()
        ctx.shadowBlur = 0

        // Target Label
        ctx.fillStyle = '#f8fafc'
        ctx.font = '10px monospace'
        ctx.fillText(t.name, t.x + 12, t.y + 3)
      })

      animationId = requestAnimationFrame(render)
    }

    render()
    return () => cancelAnimationFrame(animationId)
  }, [radarActive])

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const clicked = TARGETS.find(t => Math.hypot(t.x - x, t.y - y) < 18)
    if (clicked) setSelectedTarget(clicked)
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16, height: 'calc(100vh - 120px)' }}>
      
      {/* Radar Map Canvas */}
      <div style={{ background: 'radial-gradient(circle at center, #0b1329 0%, #030712 100%)', borderRadius: 14, border: '1px solid rgba(56, 189, 248, 0.3)', padding: 16, display: 'flex', flexDirection: 'column', position: 'relative' }}>
        
        {/* Header HUD */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 15, fontWeight: 800, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#34d399', boxShadow: '0 0 10px #34d399' }} />
              LIVE GEOSPATIAL SURVEILLANCE & SATELLITE RADAR
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Sector: Western Command (Mumbai - Pune Corridor) · GPS Grid: 19.0760° N, 72.8777° E</div>
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
          <span>LAT/LNG ENCRYPTION: AES-256</span>
          <span>CEIR SATELLITE: ACTIVE</span>
          <span>IMSI INTERCEPTION: RUNNING</span>
        </div>
      </div>

      {/* Target Inspector & Feed */}
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
                onClick={() => alert(`Tactical unit dispatched to coordinates: ${selectedTarget.lat}, ${selectedTarget.lng}`)}
                style={{ padding: '8px 12px', borderRadius: 6, background: '#dc2626', color: 'white', border: 'none', fontWeight: 800, fontSize: 11, cursor: 'pointer', marginTop: 4 }}
              >
                ⚡ Dispatch Ground Intercept Unit
              </button>
            </div>
          ) : (
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 10 }}>Click any glowing radar blip on the map to inspect live telemetry.</div>
          )}
        </div>

        {/* Live Interception Stream */}
        <div style={{ flex: 1, background: 'rgba(15, 23, 42, 0.85)', padding: 16, borderRadius: 14, border: '1px solid #1e293b', display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: '#f59e0b', marginBottom: 8 }}>📡 LIVE TELEMETRY INTERCEPTION FEED</div>
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6, fontSize: 10.5, fontFamily: 'monospace', color: '#cbd5e1' }}>
            <div style={{ color: '#34d399' }}>[02:14:10] Tower #404-45-1920: Outgoing handshake +91-9876543210 ➔ +91-9654321098</div>
            <div style={{ color: '#f59e0b' }}>[02:22:05] ANPR Camera #12: BMW X5 passed Dahisar Toll Plaza (64 km/h)</div>
            <div style={{ color: '#38bdf8' }}>[02:45:18] IMSI Catcher: SIM swap detected on secondary IMEI 354892019482019</div>
            <div style={{ color: '#ef4444' }}>[03:00:22] ALERT: Wire transfer ₹1.5 Cr routed to Phoenix Trading LLC</div>
          </div>
        </div>

      </div>
    </div>
  )
}
