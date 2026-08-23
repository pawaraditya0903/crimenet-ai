import { useState } from 'react'

export default function TelecomInterceptor() {
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
    }, 600)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, height: 'calc(100vh - 120px)', overflowY: 'auto' }}>
      
      {/* Header Search Bar */}
      <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: '16px 20px', borderRadius: 14, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>📡</span> CELLULAR CDR & IMSI SURVEILLANCE INTERCEPTOR
          </h2>
          <p style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Authorized lawful interception under Section 5(2) Indian Telegraph Act · Operator: <b>Aditya Pawar</b></p>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={targetNumber}
            onChange={(e) => setTargetNumber(e.target.value)}
            placeholder="Enter MSISDN (e.g. 9834702432)..."
            style={{ padding: '8px 14px', borderRadius: 8, background: '#020617', border: '1px solid #38bdf8', color: 'white', fontSize: 12, outline: 'none', width: 220 }}
          />
          <button
            onClick={handleScan}
            disabled={scanActive}
            style={{ padding: '8px 16px', borderRadius: 8, background: scanActive ? '#334155' : '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 12, cursor: 'pointer' }}
          >
            {scanActive ? '⏳ Triangulating...' : '⚡ Scan Target CDR'}
          </button>
        </div>
      </div>

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

    </div>
  )
}
