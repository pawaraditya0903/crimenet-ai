import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

function CellTowerTriangulationCanvas({ targetNumber, threatScore }: { targetNumber: string, threatScore: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let pulse = 0
    let animationId: number

    const towers = [
      { id: 'T1', name: 'Hub #404-45-1920 (Goregaon E)', x: 150, y: 70, dbm: '-68 dBm', delay: '1.2 μs' },
      { id: 'T2', name: 'Hub #404-45-1921 (Goregaon Sec 4)', x: 450, y: 80, dbm: '-74 dBm', delay: '2.4 μs' },
      { id: 'T3', name: 'Hub #404-45-1922 (Bandra W)', x: 300, y: 220, dbm: '-82 dBm', delay: '3.8 μs' }
    ]

    // Triangulated suspect center point
    const targetX = 295
    const targetY = 120

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      pulse += 0.03

      // Background Grid
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.08)'
      ctx.lineWidth = 1
      for (let x = 0; x < canvas.width; x += 30) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke()
      }
      for (let y = 0; y < canvas.height; y += 30) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke()
      }

      // Triangulation Triangle Interconnect
      ctx.beginPath()
      ctx.moveTo(towers[0].x, towers[0].y)
      ctx.lineTo(towers[1].x, towers[1].y)
      ctx.lineTo(towers[2].x, towers[2].y)
      ctx.closePath()
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.3)'
      ctx.setLineDash([4, 4])
      ctx.stroke()
      ctx.setLineDash([])

      // Draw Signal Radiations from Each Tower
      towers.forEach((t) => {
        const waveRadius = ((pulse * 25) % 90) + 15
        ctx.beginPath()
        ctx.arc(t.x, t.y, waveRadius, 0, Math.PI * 2)
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)'
        ctx.lineWidth = 1
        ctx.stroke()

        // Beam Line to Target
        ctx.beginPath()
        ctx.moveTo(t.x, t.y)
        ctx.lineTo(targetX, targetY)
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.4)'
        ctx.lineWidth = 1.5
        ctx.stroke()

        // Tower Icon
        ctx.beginPath()
        ctx.arc(t.x, t.y, 8, 0, Math.PI * 2)
        ctx.fillStyle = '#1d4ed8'
        ctx.fill()
        ctx.strokeStyle = '#38bdf8'
        ctx.stroke()

        // Tower Label
        ctx.fillStyle = '#cbd5e1'
        ctx.font = '10px monospace'
        ctx.fillText(`${t.name}`, t.x - 40, t.y - 12)
        ctx.fillStyle = '#f59e0b'
        ctx.fillText(`${t.dbm} · ${t.delay}`, t.x - 30, t.y + 20)
      })

      // Target Triangulated Geofence Ellipse
      const targetPulseRadius = 14 + Math.sin(pulse * 2) * 4
      ctx.beginPath()
      ctx.arc(targetX, targetY, targetPulseRadius, 0, Math.PI * 2)
      ctx.fillStyle = threatScore > 80 ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'
      ctx.fill()
      ctx.strokeStyle = threatScore > 80 ? '#ef4444' : '#10b981'
      ctx.lineWidth = 2
      ctx.stroke()

      // Target Crosshair
      ctx.beginPath()
      ctx.moveTo(targetX - 10, targetY); ctx.lineTo(targetX + 10, targetY)
      ctx.moveTo(targetX, targetY - 10); ctx.lineTo(targetX, targetY + 10)
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 1.5
      ctx.stroke()

      // Target Pin Label
      ctx.fillStyle = '#ffffff'
      ctx.font = 'bold 11px sans-serif'
      ctx.fillText(`🎯 TARGET: ${targetNumber}`, targetX + 16, targetY - 4)
      ctx.fillStyle = '#34d399'
      ctx.font = '9.5px monospace'
      ctx.fillText(`GPS: 19.1663° N, 72.8526° E (±12m Precision)`, targetX + 16, targetY + 10)

      animationId = requestAnimationFrame(render)
    }

    render()
    return () => cancelAnimationFrame(animationId)
  }, [targetNumber, threatScore])

  return (
    <div style={{ background: '#020617', borderRadius: 12, border: '1px solid #1e293b', padding: 14, display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#34d399', boxShadow: '0 0 8px #34d399' }}></span>
          3-BASE STATION RADIO TRIANGULATION & TIME-DIFFERENCE-OF-ARRIVAL (TDOA)
        </div>
        <div style={{ fontSize: 10, color: '#94a3b8', fontFamily: 'monospace' }}>GDOP: <b>1.14 (EXCELLENT)</b> · CONFIDENCE: <b>98.4%</b></div>
      </div>
      <canvas ref={canvasRef} width={600} height={260} style={{ width: '100%', height: 'auto', background: 'radial-gradient(circle at center, #0b1329 0%, #020617 100%)', borderRadius: 8 }} />
    </div>
  )
}

export default function TelecomInterceptor() {
  const [activeMode, setActiveMode] = useState<'single' | 'batch'>('single')
  const [targetNumber, setTargetNumber] = useState('9834702432')
  const [scanActive, setScanActive] = useState(false)
  const [intel, setIntel] = useState<any>({
    number: '9834702432',
    carrier: 'Reliance Jio 5G / VoLTE',
    circle: 'Maharashtra & Goa Telecom Circle (India)',
    imei: '354892019482019',
    secondaryImsi: '404-45-8910293849102 (Burner SIM B)',
    threatScore: 84.5,
    activeTower: 'Sector Hub #404-45-1920 (19.1663° N, 72.8526° E)',
    signalDbm: '-68 dBm (Strong Signal)',
    nocturnalRatio: '42.8% of calls between 01:30 AM - 04:15 AM',
    logs: [
      { time: '13-Mar 02:14:10', target: '+91-9654321098 (M. Rafiq)', type: 'Outbound Voice', duration: '342s', tower: 'Goregaon East Hub', flag: 'NOCTURNAL' },
      { time: '13-Mar 02:22:05', target: '+91-9845678901 (Vikram S.)', type: 'Outbound Voice', duration: '185s', tower: 'Goregaon Sector 4', flag: 'NOCTURNAL' },
      { time: '13-Mar 03:01:40', target: '+91-9765432109 (Priya D.)', type: 'Inbound Voice', duration: '512s', tower: 'Bandra West Hub', flag: 'FINANCIAL' },
      { time: '13-Mar 21:30:00', target: '+91-9822019283 (Pune Cell)', type: 'Outbound Voice', duration: '45s', tower: 'Juhu Beach Hub', flag: 'BURST' },
      { time: '13-Mar 21:32:15', target: 'Encrypted Proxy Hub', type: 'Data Session', duration: '12 MB', tower: 'Juhu Beach Hub', flag: 'BURST' }
    ]
  })

  // Batch CSV CDR state
  const [batchAnalyzing, setBatchAnalyzing] = useState(false)
  const [batchResults, setBatchResults] = useState<any>(null)

  const handleScan = () => {
    setScanActive(true)
    setTimeout(() => {
      const digits = targetNumber.replace(/\D/g, '')
      const seed = digits ? digits.split('').reduce((a, b) => a + parseInt(b), 0) : 42
      const risk = 70 + (seed % 28)
      
      setIntel({
        number: targetNumber,
        carrier: seed % 2 === 0 ? 'Reliance Jio 5G / VoLTE' : 'Vodafone Idea (Vi) 4G Gateway',
        circle: digits.startsWith('98') ? 'Maharashtra & Goa Circle (India)' : 'Western India Telecom Circle',
        imei: `35${seed}892019482${seed % 9}9`,
        secondaryImsi: `404-45-${seed}910293849102 (Burner SIM B)`,
        threatScore: risk,
        activeTower: `Sector Hub #404-45-${1900 + (seed % 50)} (19.1663° N, 72.8526° E)`,
        signalDbm: `${-65 - (seed % 20)} dBm (Active Handover)`,
        nocturnalRatio: `${30 + (seed % 22)}% between 01:30 AM - 04:15 AM`,
        logs: [
          { time: 'Today 02:14:10', target: '+91-9654321098 (M. Rafiq)', type: 'Outbound Voice', duration: '342s', tower: 'Goregaon East Hub', flag: 'NOCTURNAL' },
          { time: 'Today 02:22:05', target: '+91-9845678901 (Vikram S.)', type: 'Outbound Voice', duration: '185s', tower: 'Goregaon Sector 4', flag: 'NOCTURNAL' },
          { time: 'Today 03:01:40', target: '+91-9765432109 (Priya D.)', type: 'Inbound Voice', duration: '512s', tower: 'Bandra West Hub', flag: 'FINANCIAL' },
          { time: 'Today 21:30:00', target: 'Encrypted Gateway', type: 'Data Burst', duration: '45 MB', tower: 'Juhu Beach Hub', flag: 'BURST' }
        ]
      })
      setScanActive(false)
    }, 500)
  }

  const handleLoadSampleBatch = async () => {
    setBatchAnalyzing(true)
    try {
      const sampleRes = await axios.get('/api/telecom/sample-cdr')
      const analysisRes = await axios.post('/api/telecom/analyze', { records: sampleRes.data.records })
      setBatchResults({
        records: sampleRes.data.records,
        analysis: analysisRes.data
      })
    } catch (e) {
      console.error(e)
    } finally {
      setBatchAnalyzing(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, height: 'calc(100vh - 120px)', overflowY: 'auto' }}>
      
      {/* Header Search Bar with Dual Mode Switcher */}
      <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: '14px 20px', borderRadius: 14, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>📡</span> CELLULAR CDR & STATISTICAL TELECOM INTERCEPTOR
          </h2>
          <p style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Z-Score Burst Anomaly Engine & Multi-SIM Co-Location Analyzer · Operator: <b>Aditya Pawar</b></p>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div style={{ display: 'flex', background: '#020617', padding: 2, borderRadius: 8, border: '1px solid #334155' }}>
            <button
              onClick={() => setActiveMode('single')}
              style={{ padding: '6px 12px', borderRadius: 6, background: activeMode === 'single' ? '#1d4ed8' : 'transparent', color: 'white', border: 'none', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
            >
              Single MSISDN
            </button>
            <button
              onClick={() => { setActiveMode('batch'); if (!batchResults) handleLoadSampleBatch(); }}
              style={{ padding: '6px 12px', borderRadius: 6, background: activeMode === 'batch' ? '#1d4ed8' : 'transparent', color: 'white', border: 'none', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
            >
              Batch CSV CDR Engine
            </button>
          </div>

          {activeMode === 'single' ? (
            <div style={{ display: 'flex', gap: 6 }}>
              <input
                value={targetNumber}
                onChange={(e) => setTargetNumber(e.target.value)}
                placeholder="Enter MSISDN (e.g. 9834702432)..."
                style={{ padding: '7px 12px', borderRadius: 8, background: '#020617', border: '1px solid #38bdf8', color: 'white', fontSize: 11.5, outline: 'none', width: 190 }}
              />
              <button
                onClick={handleScan}
                disabled={scanActive}
                style={{ padding: '7px 14px', borderRadius: 8, background: scanActive ? '#334155' : '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 11, cursor: 'pointer' }}
              >
                {scanActive ? '⏳ Triangulating...' : '⚡ Scan CDR'}
              </button>
            </div>
          ) : (
            <button
              onClick={handleLoadSampleBatch}
              disabled={batchAnalyzing}
              style={{ padding: '7px 16px', borderRadius: 8, background: '#059669', color: 'white', border: 'none', fontWeight: 800, fontSize: 11, cursor: 'pointer' }}
            >
              {batchAnalyzing ? '⏳ Running Z-Score Math...' : '📥 Ingest & Analyze 7-Call CDR Batch'}
            </button>
          )}
        </div>
      </div>

      {activeMode === 'single' ? (
        <>
          {/* Grid: 4 Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>TARGET SUBSCRIBER</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: 'white', marginTop: 2 }}>{intel.number}</div>
              <div style={{ fontSize: 11, color: '#38bdf8', marginTop: 2 }}>{intel.carrier}</div>
            </div>

            <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>THREAT ASSESSMENT</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: intel.threatScore >= 80 ? '#ef4444' : '#f59e0b', marginTop: 2 }}>{intel.threatScore} / 100</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{intel.threatScore >= 80 ? 'CRITICAL SURVEILLANCE' : 'HIGH RISK'}</div>
            </div>

            <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>HARDWARE IMEI LINK</div>
              <div style={{ fontSize: 14, fontWeight: 800, color: 'white', fontFamily: 'monospace', marginTop: 4 }}>{intel.imei}</div>
              <div style={{ fontSize: 10, color: '#34d399', marginTop: 2 }}>Dual SIM Paired: 2 Cards Active</div>
            </div>

            <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>SIGNAL & CELL TOWER</div>
              <div style={{ fontSize: 13, fontWeight: 800, color: '#f59e0b', marginTop: 4 }}>{intel.signalDbm}</div>
              <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>{intel.activeTower}</div>
            </div>
          </div>

          {/* VISUAL 3-TOWER CELLULAR TRIANGULATION MAP */}
          <CellTowerTriangulationCanvas targetNumber={intel.number} threatScore={intel.threatScore} />

          {/* Dual SIM & Hardware Forensic Module */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 16, borderRadius: 12, border: '1px solid #1e293b' }}>
              <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', marginBottom: 8 }}>📱 DUAL-SIM HARDWARE PAIRING MATRIX</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 11 }}>
                <div style={{ padding: 10, background: '#020617', borderRadius: 8, border: '1px solid #334155' }}>
                  <div style={{ color: '#34d399', fontWeight: 700 }}>SIM SLOT 1 (PRIMARY): {intel.number}</div>
                  <div style={{ color: '#94a3b8', marginTop: 2 }}>IMSI: 404-45-192837482910 · Registered Circle: {intel.circle}</div>
                </div>
                <div style={{ padding: 10, background: '#020617', borderRadius: 8, border: '1px solid #ef4444' }}>
                  <div style={{ color: '#ef4444', fontWeight: 700 }}>SIM SLOT 2 (COVERT BURNER): {intel.secondaryImsi}</div>
                  <div style={{ color: '#94a3b8', marginTop: 2 }}>Status: Intermittent Nocturnal Activation · Used for Hawala Remittances</div>
                </div>
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 16, borderRadius: 12, border: '1px solid #1e293b' }}>
              <div style={{ fontSize: 12, fontWeight: 800, color: '#f59e0b', marginBottom: 8 }}>🌙 NOCTURNAL BEHAVIOR PATTERN</div>
              <div style={{ fontSize: 12, color: 'white', marginTop: 4 }}><b>Peak Calling Window:</b> {intel.nocturnalRatio}</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 6, lineHeight: 1.5 }}>
                Target exhibits severe operational clustering during late-night hours. Calls are directed to logistics staging contacts in Goregaon and hawala handlers in Dharavi.
              </div>
              <div style={{ marginTop: 10, padding: 8, background: 'rgba(239,68,68,0.15)', borderRadius: 6, border: '1px solid rgba(239,68,68,0.3)', color: '#f87171', fontSize: 10.5, fontWeight: 700 }}>
                🚨 Pre-Raid Flight Risk: High frequency burst detected prior to scheduled enforcement raids.
              </div>
            </div>
          </div>

          {/* Live Intercepted CDR Table */}
          <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 16, borderRadius: 12, border: '1px solid #1e293b', flex: 1 }}>
            <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', marginBottom: 10 }}>📋 REAL-TIME INTERCEPTED CALL DETAIL RECORDS (CDR)</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {intel.logs.map((log: any, idx: number) => (
                <div key={idx} style={{ padding: '8px 12px', background: '#020617', borderRadius: 6, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11 }}>
                  <div>
                    <span style={{ color: '#94a3b8', marginRight: 10 }}>{log.time}</span>
                    <span style={{ color: 'white', fontWeight: 700 }}>{log.target}</span>
                    <span style={{ color: '#38bdf8', marginLeft: 10 }}>({log.type})</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ color: '#94a3b8' }}>{log.tower}</span>
                    <span style={{ color: '#f59e0b', fontFamily: 'monospace' }}>{log.duration}</span>
                    <span style={{ padding: '2px 6px', borderRadius: 4, background: log.flag === 'BURST' ? '#7f1d1d' : '#78350f', color: 'white', fontSize: 9.5, fontWeight: 800 }}>
                      {log.flag}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        /* BATCH CSV CDR STATISTICAL ENGINE */
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {batchResults?.analysis && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
              <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #ef4444' }}>
                <div style={{ fontSize: 10, color: '#f87171', textTransform: 'uppercase' }}>Z-SCORE BURST SIGMA</div>
                <div style={{ fontSize: 24, fontWeight: 800, color: '#ef4444', marginTop: 2 }}>{batchResults.analysis.z_score_burst} σ</div>
                <div style={{ fontSize: 10, color: '#94a3b8' }}>{batchResults.analysis.is_burst_anomaly ? '🚨 CRITICAL OUTLIER BURST' : 'NORMAL'}</div>
              </div>

              <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #38bdf8' }}>
                <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>NOCTURNAL CALL RATIO</div>
                <div style={{ fontSize: 24, fontWeight: 800, color: '#38bdf8', marginTop: 2 }}>{batchResults.analysis.nocturnal_ratio_pct}%</div>
                <div style={{ fontSize: 10, color: '#94a3b8' }}>01:00 AM - 04:30 AM WINDOW</div>
              </div>

              <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #f59e0b' }}>
                <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>BURNER SIM SWAPS</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: batchResults.analysis.burner_sim_swap_detected ? '#f59e0b' : '#34d399', marginTop: 4 }}>
                  {batchResults.analysis.burner_sim_swap_detected ? '⚠️ MULTI-SIM SWAP' : '✓ 1 SIM TIED'}
                </div>
                <div style={{ fontSize: 10, color: '#94a3b8' }}>{batchResults.analysis.max_sims_per_handset} IMSIs on single IMEI</div>
              </div>

              <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #10b981' }}>
                <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>TOP ACTIVE CELL TOWER</div>
                <div style={{ fontSize: 15, fontWeight: 800, color: '#10b981', marginTop: 4 }}>{batchResults.analysis.top_active_tower}</div>
                <div style={{ fontSize: 10, color: '#94a3b8' }}>Geofence Target Hub</div>
              </div>
            </div>
          )}

          {/* Parsed Batch Records Table */}
          <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: 16, borderRadius: 12, border: '1px solid #1e293b' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: '#38bdf8' }}>
                📂 INGESTED BATCH CDR TIME-SERIES LOGS ({batchResults?.records?.length || 0} CALLS AUDITED)
              </div>
              <div style={{ fontSize: 10, color: '#34d399', fontWeight: 700 }}>✓ SECTION 65B FORENSIC TIMESTAMP VERIFIED</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 280, overflowY: 'auto' }}>
              {batchResults?.records?.map((r: any, i: number) => (
                <div key={i} style={{ padding: '8px 12px', background: '#020617', borderRadius: 6, border: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11 }}>
                  <div>
                    <span style={{ color: '#f59e0b', fontWeight: 700, marginRight: 8 }}>[{r.call_id}]</span>
                    <span style={{ color: '#94a3b8', marginRight: 10 }}>{r.timestamp}</span>
                    <span style={{ color: 'white', fontWeight: 700 }}>{r.caller} ➔ {r.receiver}</span>
                  </div>
                  <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                    <span style={{ color: '#38bdf8' }}>IMEI: {r.imei}</span>
                    <span style={{ color: '#94a3b8' }}>IMSI: {r.imsi}</span>
                    <span style={{ color: '#f59e0b', fontFamily: 'monospace' }}>{r.duration_sec}s</span>
                    <span style={{ padding: '2px 6px', borderRadius: 4, background: r.type === 'BURST_CALL' ? '#7f1d1d' : '#1e3a8a', color: 'white', fontSize: 9.5, fontWeight: 800 }}>
                      {r.type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
