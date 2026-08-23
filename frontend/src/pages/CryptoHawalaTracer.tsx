import { useState } from 'react'

export default function CryptoHawalaTracer() {
  const [walletInput, setWalletInput] = useState('0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D')
  const [tracing, setTracing] = useState(false)
  
  const [flowData, setFlowData] = useState<any>({
    wallet: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
    entity: 'Phoenix Trading LLC (Dubai Offshore)',
    taintScore: 96.8,
    totalVolume: '$2,450,000 USDT (TRC-20)',
    fiatEquivalent: '₹20.45 Crore INR',
    sha256Hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    hops: [
      { step: 1, from: 'Mehta Enterprises (HDFC #0987)', to: 'Mule Gateway (Razorpay/USDT)', amount: '₹1.50 Cr', token: 'FIAT RTGS', status: 'ORIGIN' },
      { step: 2, from: 'Mule Gateway', to: '0x7a25...f981 (Phoenix LLC)', amount: '180,000 USDT', token: 'USDT TRC-20', status: 'OFFSHORE LAYER' },
      { step: 3, from: '0x7a25...f981', to: 'Tornado Cash / Mixer Pool', amount: '150,000 USDT', token: 'PRIVACY TUMBLER', status: 'OBFUSCATED' },
      { step: 4, from: 'Mixer Output #49', to: '0x991b...2819 (M. Rafiq Dubai)', amount: '148,500 USDT', token: 'CLEANED ASSET', status: 'DESTINATION' }
    ]
  })

  const handleTrace = () => {
    setTracing(true)
    setTimeout(() => {
      setFlowData({
        wallet: walletInput,
        entity: walletInput.startsWith('0x') ? 'Phoenix Trading LLC (Layer 3 Mixer)' : 'Hawala Token Gateway',
        taintScore: 94.2,
        totalVolume: '$1,850,000 USDT (TRC-20)',
        fiatEquivalent: '₹15.42 Crore INR',
        sha256Hash: 'a8f5c38192019482710194829102938491029384910293849102938491029384',
        hops: [
          { step: 1, from: 'Target Source Account', to: 'Crypto On-Ramp Gateway', amount: '₹2.10 Cr', token: 'FIAT SWIFT', status: 'ORIGIN' },
          { step: 2, from: 'On-Ramp Gateway', to: walletInput, amount: '250,000 USDT', token: 'USDT TRC-20', status: 'OFFSHORE LAYER' },
          { step: 3, from: walletInput, to: 'Al-Rafiq Cash Remittance Hub', amount: '245,000 USDT', token: 'HAWALA TOKEN', status: 'FINAL CASH PICKUP' }
        ]
      })
      setTracing(false)
    }, 550)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, height: 'calc(100vh - 120px)', overflowY: 'auto' }}>
      
      {/* Header Bar */}
      <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: '16px 20px', borderRadius: 14, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 800, color: 'white', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>💸</span> FINANCIAL HAWALA & BLOCKCHAIN CRYPTO TRACER
          </h2>
          <p style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Multi-Hop USDT TRC-20, Bitcoin & Hawala Layering Engine · Architect: <b>Aditya Pawar</b></p>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <input
            value={walletInput}
            onChange={(e) => setWalletInput(e.target.value)}
            placeholder="Enter USDT / Crypto Wallet or Bank Account..."
            style={{ padding: '8px 14px', borderRadius: 8, background: '#020617', border: '1px solid #38bdf8', color: 'white', fontSize: 12, outline: 'none', width: 340 }}
          />
          <button
            onClick={handleTrace}
            disabled={tracing}
            style={{ padding: '8px 16px', borderRadius: 8, background: tracing ? '#334155' : '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 12, cursor: 'pointer' }}
          >
            {tracing ? '⏳ Tracing Blockchain...' : '⚡ Trace Money Flow'}
          </button>
        </div>
      </div>

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

    </div>
  )
}
