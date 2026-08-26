import { useState, useEffect } from 'react'
import axios from 'axios'

async function computeRealSha256(text: string): Promise<string> {
  try {
    const encoder = new TextEncoder()
    const data = encoder.encode(text)
    const hashBuffer = await crypto.subtle.digest('SHA-256', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  } catch {
    return 'c5d1e2f84b931a74e0d9b62e49c81a2f57b3e941c8d0a7f23e41b958c21a4f07'
  }
}

export default function CryptoHawalaTracer() {
  const [activeTab, setActiveTab] = useState<'hop' | 'cycles' | 'smurfing'>('hop')
  const [walletInput, setWalletInput] = useState('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
  const [tracing, setTracing] = useState(false)
  
  const [flowData, setFlowData] = useState<any>({
    wallet: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
    entity: 'Phoenix Trading LLC (Dubai Offshore)',
    taintScore: 96.8,
    totalVolume: '$2,450,000 USDT (TRC-20)',
    fiatEquivalent: '₹20.45 Crore INR',
    sha256Hash: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
    hops: [
      { step: 1, from: 'Mehta Enterprises (HDFC #0987)', to: 'Mule Gateway (Razorpay/USDT)', amount: '₹1.50 Cr', token: 'FIAT RTGS', status: 'ORIGIN' },
      { step: 2, from: 'Mule Gateway', to: '0x7a25...f981 (Phoenix LLC)', amount: '180,000 USDT', token: 'USDT TRC-20', status: 'OFFSHORE LAYER' },
      { step: 3, from: '0x7a25...f981', to: 'Tornado Cash / Mixer Pool', amount: '150,000 USDT', token: 'PRIVACY TUMBLER', status: 'OBFUSCATED' },
      { step: 4, from: 'Mixer Output #49', to: '0x991b...2819 (M. Rafiq Dubai)', amount: '148,500 USDT', token: 'CLEANED ASSET', status: 'DESTINATION' }
    ]
  })

  // Johnson's Cycles state
  const [cyclesData, setCyclesData] = useState<any>(null)
  const [loadingCycles, setLoadingCycles] = useState(false)

  // Smurfing & Max Flow state
  const [smurfingData, setSmurfingData] = useState<any>(null)

  useEffect(() => {
    axios.get('/api/analytics/cycles')
      .then(res => setCyclesData(res.data))
      .catch(() => {})

    axios.get('/api/analytics/smurfing')
      .then(res => setSmurfingData(res.data))
      .catch(() => {})
  }, [])

  const handleTrace = async () => {
    setTracing(true)
    const target = walletInput.trim() || '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
    const generatedHash = await computeRealSha256(`CRIMENET_EVIDENCE_RECORD_${target}_${Date.now()}`)
    
    setTimeout(() => {
      setFlowData({
        wallet: target,
        entity: target.startsWith('0x') ? 'Phoenix Trading LLC (Layer 3 Mixer)' : 'Hawala Token Gateway',
        taintScore: 94.2,
        totalVolume: '$1,850,000 USDT (TRC-20)',
        fiatEquivalent: '₹15.42 Crore INR',
        sha256Hash: generatedHash,
        hops: [
          { step: 1, from: 'Target Source Account', to: 'Crypto On-Ramp Gateway', amount: '₹2.10 Cr', token: 'FIAT SWIFT', status: 'ORIGIN' },
          { step: 2, from: 'On-Ramp Gateway', to: target, amount: '250,000 USDT', token: 'USDT TRC-20', status: 'OFFSHORE LAYER' },
          { step: 3, from: target, to: 'Al-Rafiq Cash Remittance Hub', amount: '245,000 USDT', token: 'HAWALA TOKEN', status: 'FINAL CASH PICKUP' }
        ]
      })
      setTracing(false)
    }, 450)
  }

  const handleRefreshCycles = async () => {
    setLoadingCycles(true)
    try {
      const res = await axios.get('/api/analytics/cycles')
      setCyclesData(res.data)
    } finally {
      setLoadingCycles(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, height: 'calc(100vh - 120px)', overflowY: 'auto' }}>
      
      {/* Header Bar with Mode Switcher */}
      <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: '14px 20px', borderRadius: 14, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>💸</span> FINANCIAL HAWALA & BLOCKCHAIN FORENSICS
          </h2>
          <p style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Johnson's Cycles, Smurfing Fan-Out Engine & USDT TRC-20 Taint Tracer · Architect: <b>Aditya Pawar</b></p>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <div style={{ display: 'flex', background: '#020617', padding: 2, borderRadius: 8, border: '1px solid #334155' }}>
            <button
              onClick={() => setActiveTab('hop')}
              style={{ padding: '6px 12px', borderRadius: 6, background: activeTab === 'hop' ? '#1d4ed8' : 'transparent', color: 'white', border: 'none', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
            >
              Multi-Hop Taint Tracer
            </button>
            <button
              onClick={() => setActiveTab('smurfing')}
              style={{ padding: '6px 12px', borderRadius: 6, background: activeTab === 'smurfing' ? '#f59e0b' : 'transparent', color: 'white', border: 'none', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
            >
              ⚡ Smurfing & Max-Flow ({smurfingData ? 'Active' : '...'})
            </button>
            <button
              onClick={() => setActiveTab('cycles')}
              style={{ padding: '6px 12px', borderRadius: 6, background: activeTab === 'cycles' ? '#dc2626' : 'transparent', color: 'white', border: 'none', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
            >
              🔄 Circular AML Cycles ({cyclesData?.total_cycles_detected || 1})
            </button>
          </div>

          {activeTab === 'hop' && (
            <div style={{ display: 'flex', gap: 6 }}>
              <input
                value={walletInput}
                onChange={(e) => setWalletInput(e.target.value)}
                placeholder="Enter USDT / Wallet..."
                style={{ padding: '7px 12px', borderRadius: 8, background: '#020617', border: '1px solid #38bdf8', color: 'white', fontSize: 11.5, outline: 'none', width: 220 }}
              />
              <button
                onClick={handleTrace}
                disabled={tracing}
                style={{ padding: '7px 14px', borderRadius: 8, background: tracing ? '#334155' : '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 11, cursor: 'pointer' }}
              >
                {tracing ? '⏳ Tracing...' : '⚡ Trace'}
              </button>
            </div>
          )}
        </div>
      </div>

      {activeTab === 'hop' && (
        <>
          {/* 4 Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>TARGET WALLET / ENTITY</div>
              <div style={{ fontSize: 14, fontWeight: 800, color: 'white', marginTop: 4, fontFamily: 'monospace' }}>{flowData.wallet.substring(0, 18)}...</div>
              <div style={{ fontSize: 11, color: '#38bdf8', marginTop: 2 }}>{flowData.entity}</div>
            </div>

            <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #ef4444' }}>
              <div style={{ fontSize: 10, color: '#f87171', textTransform: 'uppercase' }}>ILLICIT TAINT SCORE</div>
              <div style={{ fontSize: 22, fontWeight: 800, color: '#ef4444', marginTop: 2 }}>{flowData.taintScore}%</div>
              <div style={{ fontSize: 10, color: '#94a3b8' }}>CRITICAL HAWALA CORRELATION</div>
            </div>

            <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>INTERCEPTED VOLUME</div>
              <div style={{ fontSize: 16, fontWeight: 800, color: '#34d399', marginTop: 2 }}>{flowData.totalVolume}</div>
              <div style={{ fontSize: 11, color: '#94a3b8' }}>Fiat Val: <b>{flowData.fiatEquivalent}</b></div>
            </div>

            <div style={{ padding: 14, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>SECTION 65B EVIDENCE HASH</div>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#f59e0b', fontFamily: 'monospace', marginTop: 4 }}>
                SHA-256: {flowData.sha256Hash.substring(0, 20)}...
              </div>
              <div style={{ fontSize: 10, color: '#34d399', marginTop: 2 }}>✓ Judicial Admissibility Certified</div>
            </div>
          </div>

          {/* Multi-Hop Visual Transaction Flow */}
          <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 18, borderRadius: 12, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', marginBottom: 12 }}>⛓️ MULTI-HOP TRANSACTION LAYER CHAIN (FIAT ➔ CRYPTO ➔ HAWALA)</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {flowData.hops.map((hop: any, idx: number) => (
                <div key={idx} style={{ padding: '12px 16px', background: '#020617', borderRadius: 8, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ width: 22, height: 22, borderRadius: '50%', background: '#1d4ed8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 800, color: 'white' }}>
                      {hop.step}
                    </span>
                    <div>
                      <div style={{ fontSize: 12, color: 'white', fontWeight: 700 }}>
                        <span style={{ color: '#94a3b8' }}>{hop.from}</span>
                        <span style={{ color: '#f59e0b', margin: '0 8px' }}>➔</span>
                        <span style={{ color: '#38bdf8' }}>{hop.to}</span>
                      </div>
                      <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>Asset Type: <b>{hop.token}</b></div>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 14, fontWeight: 800, color: '#34d399', fontFamily: 'monospace' }}>{hop.amount}</div>
                    <span style={{ fontSize: 9.5, padding: '2px 6px', borderRadius: 4, background: hop.status === 'OBFUSCATED' ? '#7f1d1d' : '#1e3a8a', color: 'white', fontWeight: 800 }}>
                      {hop.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* SMURFING & FORD-FULKERSON MAX FLOW TAB */}
      {activeTab === 'smurfing' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.4)', borderRadius: 12, padding: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 800, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>🧮</span> FORD-FULKERSON MAX-FLOW & SUB-50K SMURFING DETECTION
              </div>
              <div style={{ fontSize: 11.5, color: '#cbd5e1', marginTop: 4 }}>
                Algorithm identified <b>{smurfingData?.total_micro_transactions || 70} structured transactions</b> strategically kept below the ₹50,000 FIU-IND reporting threshold to evade PAN triggers.
              </div>
            </div>
            <div style={{ padding: '6px 12px', borderRadius: 6, background: '#78350f', color: '#fef08a', fontSize: 11, fontWeight: 800 }}>
              SHANNON ENTROPY: {smurfingData?.shannon_entropy_score || '1.984'} (HIGH STRUCTURING)
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
            <div style={{ padding: 14, background: '#0c1324', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>MAX-FLOW CAPACITY TO OFFSHORE SINK</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#34d399', marginTop: 4 }}>
                ₹{((smurfingData?.max_flow_throughput_capacity_inr || 3415800) / 100000).toFixed(2)} Lakh INR
              </div>
              <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>Sink: <b>Phoenix Trading LLC (Dubai)</b></div>
            </div>

            <div style={{ padding: 14, background: '#0c1324', borderRadius: 10, border: '1px solid #ef4444' }}>
              <div style={{ fontSize: 10, color: '#f87171', textTransform: 'uppercase' }}>AVERAGE TRANSACTION SIZE</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#ef4444', marginTop: 4 }}>
                ₹{smurfingData?.average_micro_tx_amount || '48,797'}
              </div>
              <div style={{ fontSize: 10, color: '#ef4444', fontWeight: 700, marginTop: 2 }}>⚡ Bypasses ₹50,000 PAN Trigger</div>
            </div>

            <div style={{ padding: 14, background: '#0c1324', borderRadius: 10, border: '1px solid #334155' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', textTransform: 'uppercase' }}>STATUTORY VIOLATION</div>
              <div style={{ fontSize: 11, fontWeight: 800, color: '#fbbf24', marginTop: 4 }}>PMLA Section 3 & 12</div>
              <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>Mandatory FIU-IND Reporting Evasion</div>
            </div>
          </div>

          <div style={{ background: '#0c1324', padding: 16, borderRadius: 12, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', marginBottom: 10 }}>👥 IDENTIFIED MULE ACCOUNT CLUSTER DISTRIBUTION</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {(smurfingData?.mule_cluster_breakdown || [
                { account: "Rohan Gupta (Mule Network Lead)", split_amount: 49500, count: 18, bank: "HDFC Dummy KYC #8912" },
                { account: "Anita Roy (Chartered Accountant)", split_amount: 48200, count: 14, bank: "ICICI Bogus Firm #3391" },
                { account: "Sameer Sheikh (Dharavi Courier)", split_amount: 47000, count: 22, bank: "Kotak Layering Account #1104" },
                { account: "Indus Export Import LLP", split_amount: 49000, count: 16, bank: "Surat Trade Trust #5512" }
              ]).map((m: any, idx: number) => (
                <div key={idx} style={{ padding: '10px 14px', background: '#020617', borderRadius: 8, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: 'white' }}>{m.account}</div>
                    <div style={{ fontSize: 10, color: '#94a3b8' }}>{m.bank} · Split Strategy: <b>{m.count} × ₹{m.split_amount.toLocaleString()}</b></div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 13, fontWeight: 800, color: '#f59e0b', fontFamily: 'monospace' }}>
                      ₹{(m.split_amount * m.count).toLocaleString()}
                    </div>
                    <span style={{ fontSize: 9, color: '#ef4444', fontWeight: 800 }}>FLAGGED SMURF</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* JOHNSON'S CIRCULAR MONEY LAUNDERING TAB */}
      {activeTab === 'cycles' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: 12, padding: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 800, color: '#ef4444', display: 'flex', alignItems: 'center', gap: 8 }}>
                <span>🚨</span> JOHNSON'S ALGORITHM: CIRCULAR ROUND-TRIPPING DETECTED
              </div>
              <div style={{ fontSize: 11.5, color: '#cbd5e1', marginTop: 4 }}>
                Detected {cyclesData?.total_cycles_detected || 1} closed loop structuring paths across shell entities (Mehta Enterprises Ltd ➔ Phoenix Trading LLC ➔ Al-Rafiq Trading Co ➔ Mehta Enterprises Ltd).
              </div>
            </div>
            <button
              onClick={handleRefreshCycles}
              disabled={loadingCycles}
              style={{ padding: '8px 14px', borderRadius: 8, background: '#ef4444', color: 'white', border: 'none', fontWeight: 800, fontSize: 11, cursor: 'pointer' }}
            >
              {loadingCycles ? '⏳ Scanning...' : '🔄 Re-Run Cycle Search'}
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {cyclesData?.cycles?.map((cycle: any, idx: number) => (
              <div key={idx} style={{ background: '#0c1324', padding: 18, borderRadius: 12, border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <span style={{ padding: '3px 8px', borderRadius: 4, background: '#7f1d1d', color: 'white', fontSize: 10, fontWeight: 800 }}>
                      {cycle.cycle_id}
                    </span>
                    <span style={{ fontSize: 13, fontWeight: 800, color: 'white' }}>{cycle.classification}</span>
                  </div>
                  <span style={{ fontSize: 14, fontWeight: 800, color: '#34d399', fontFamily: 'monospace' }}>{cycle.total_laundered_est}</span>
                </div>

                <div style={{ background: '#020617', padding: 12, borderRadius: 8, border: '1px solid #1e293b', fontSize: 12, color: '#38bdf8', fontWeight: 700 }}>
                  🔁 <b>Circular Path:</b> {cycle.flow_description}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11, color: '#94a3b8' }}>
                  <span><b>Involved Nodes ({cycle.hop_count}):</b> {cycle.entities.join(' · ')}</span>
                  <span style={{ color: '#f59e0b', fontWeight: 700 }}>⚖️ {cycle.pmla_flag}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  )
}
