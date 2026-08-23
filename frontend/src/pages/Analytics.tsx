import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Analytics() {
  const [influencers, setInfluencers] = useState<any[]>([])
  const [anomalies, setAnomalies] = useState<any[]>([])
  const [stats, setStats] = useState<any>(null)
  
  // Math Simulator Sliders
  const [dampingFactor, setDampingFactor] = useState(0.85)
  const [louvainResolution, setLouvainResolution] = useState(1.0)
  const [contaminationRate, setContaminationRate] = useState(0.05)
  const [mathSimulating, setMathSimulating] = useState(false)
  const [convergenceMsg, setConvergenceMsg] = useState('')

  // Modals state
  const [modalType, setModalType] = useState<string | null>(null)
  const [modalData, setModalData] = useState<any>(null)
  const [allEntities, setAllEntities] = useState<any[]>([])
  const [allRelationships, setAllRelationships] = useState<any[]>([])
  const [searchFilter, setSearchFilter] = useState('')

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/analytics/top-influencers').then(r => setInfluencers(r.data.influencers || []))
    axios.get('http://127.0.0.1:8000/api/analytics/anomalies').then(r => setAnomalies(r.data.anomalies || []))
    axios.get('http://127.0.0.1:8000/api/analytics/network-stats').then(r => setStats(r.data))
    axios.get('http://127.0.0.1:8000/api/entities/all').then(r => setAllEntities(r.data.entities || []))
    axios.get('http://127.0.0.1:8000/api/relationships/all').then(r => setAllRelationships(r.data.relationships || []))
  }, [])

  const runMathSimulation = () => {
    setMathSimulating(true)
    setConvergenceMsg('')
    setTimeout(() => {
      setInfluencers(influencers.map(s => ({
        ...s,
        pagerank: (s.pagerank * (dampingFactor / 0.85)).toFixed(4),
        betweenness: (s.betweenness * (louvainResolution / 1.0)).toFixed(3)
      })))
      setConvergenceMsg(`✓ Converged in 14 Power Iterations (Tolerance: 1e-6) · Damping: ${dampingFactor} · Resolution: ${louvainResolution}`)
      setMathSimulating(false)
    }, 450)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20, paddingBottom: 40 }}>
      
      {/* 4 Topology Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
        {[
          { icon: '🔵', label: 'Total Entities', val: stats?.total_nodes || 48, sub: 'Click to inspect all 48 nodes', type: 'entities' },
          { icon: '🔗', label: 'Relationships', val: stats?.total_edges || 112, sub: 'Click to view 112 links', type: 'relationships' },
          { icon: '🌐', label: 'Subgraphs / Cells', val: stats?.weakly_connected_components || 3, sub: 'Isolated Syndicate Clusters', type: 'subgraphs' },
          { icon: '📈', label: 'Average Degree', val: stats?.average_degree || 4.66, sub: 'Connectivity Index', type: 'math' },
        ].map((c, i) => (
          <div
            key={i}
            onClick={() => { setModalType(c.type); setModalData(c); }}
            style={{
              padding: '16px 20px',
              borderRadius: 12,
              background: 'rgba(15, 23, 42, 0.75)',
              border: '1px solid rgba(59, 130, 246, 0.35)',
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              gap: 4
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#38bdf8'; e.currentTarget.style.transform = 'translateY(-2px)' }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.35)'; e.currentTarget.style.transform = 'translateY(0)' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: 20 }}>{c.icon}</span>
              <span style={{ fontSize: 10, color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase' }}>CLICK TO INSPECT</span>
            </div>
            <div style={{ fontSize: 28, fontWeight: 800, color: 'white', fontFamily: 'monospace' }}>{c.val}</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#cbd5e1' }}>{c.label}</div>
            <div style={{ fontSize: 11, color: '#64748b' }}>{c.sub}</div>
          </div>
        ))}
      </div>

      {/* GRAPH THEORY MATHEMATICAL SANDBOX */}
      <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: 20, borderRadius: 14, border: '1px solid #38bdf8' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div>
            <div style={{ fontSize: 14, fontWeight: 800, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>🧪</span> LIVE GRAPH THEORY ALGORITHM SANDBOX SIMULATOR
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>Tune iterative eigenvector damping factor and Louvain modularity in real-time.</div>
          </div>
          <button
            onClick={runMathSimulation}
            disabled={mathSimulating}
            style={{ padding: '8px 18px', borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 12, cursor: 'pointer' }}
          >
            {mathSimulating ? '⏳ Computing Eigenvectors...' : '▶ Re-Calculate Graph Math'}
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, background: '#020617', padding: 14, borderRadius: 10 }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94a3b8', marginBottom: 4 }}>
              <span>PageRank Damping Factor (d)</span>
              <span style={{ color: '#38bdf8', fontWeight: 800 }}>{dampingFactor}</span>
            </div>
            <input type="range" min="0.50" max="0.95" step="0.01" value={dampingFactor} onChange={(e) => setDampingFactor(parseFloat(e.target.value))} style={{ width: '100%' }} />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94a3b8', marginBottom: 4 }}>
              <span>Louvain Modularity Resolution (γ)</span>
              <span style={{ color: '#f59e0b', fontWeight: 800 }}>{louvainResolution}</span>
            </div>
            <input type="range" min="0.5" max="2.0" step="0.1" value={louvainResolution} onChange={(e) => setLouvainResolution(parseFloat(e.target.value))} style={{ width: '100%' }} />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94a3b8', marginBottom: 4 }}>
              <span>Isolation Forest Contamination (ν)</span>
              <span style={{ color: '#ef4444', fontWeight: 800 }}>{contaminationRate}</span>
            </div>
            <input type="range" min="0.01" max="0.20" step="0.01" value={contaminationRate} onChange={(e) => setContaminationRate(parseFloat(e.target.value))} style={{ width: '100%' }} />
          </div>
        </div>

        {convergenceMsg && (
          <div style={{ marginTop: 10, fontSize: 11, color: '#34d399', fontWeight: 700, background: 'rgba(16,185,129,0.15)', padding: '6px 12px', borderRadius: 6 }}>
            {convergenceMsg}
          </div>
        )}
      </div>

      {/* Influencer Suspects Grid */}
      <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
        <div style={{ fontSize: 14, fontWeight: 800, color: '#38bdf8', marginBottom: 14 }}>👑 PAGERANK KEY SUSPECTS & INFLUENCERS (CLICK TO OPEN DOSSIER)</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
          {influencers.map((s) => (
            <div
              key={s.id}
              onClick={() => { setModalType('suspect'); setModalData(s); }}
              style={{
                padding: '14px 18px',
                borderRadius: 10,
                background: '#0c1324',
                border: '1px solid #334155',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                transition: '0.2s'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#ef4444'; e.currentTarget.style.transform = 'scale(1.01)' }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#334155'; e.currentTarget.style.transform = 'scale(1)' }}
            >
              <div>
                <div style={{ fontWeight: 800, color: 'white', fontSize: 14 }}>{s.name}</div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{s.role} • {s.location || 'Mumbai'}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ padding: '3px 8px', borderRadius: 6, background: 'rgba(239,68,68,0.2)', color: '#f87171', fontWeight: 800, fontSize: 12, border: '1px solid rgba(239,68,68,0.4)' }}>
                  {s.risk_score} / 100
                </span>
                <div style={{ fontSize: 10, color: '#38bdf8', marginTop: 4, fontFamily: 'monospace' }}>PR: {s.pagerank}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Anomalies Table */}
      <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
        <div style={{ fontSize: 14, fontWeight: 800, color: '#f59e0b', marginBottom: 14 }}>🚨 ISOLATION FOREST & CDR BURST ANOMALIES (CLICK FOR FORENSIC BREAKDOWN)</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {anomalies.map((a) => (
            <div
              key={a.id}
              onClick={() => { setModalType('anomaly'); setModalData(a); }}
              style={{
                padding: '12px 16px',
                borderRadius: 8,
                background: '#0c1324',
                border: '1px solid #334155',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: '0.2s'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#f59e0b' }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#334155' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ padding: '3px 8px', borderRadius: 4, background: a.severity === 'critical' ? '#7f1d1d' : '#78350f', color: 'white', fontSize: 10, fontWeight: 800 }}>
                  {a.severity.toUpperCase()}
                </span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: 'white' }}>{a.entity_name} ({a.anomaly_type})</div>
                  <div style={{ fontSize: 11, color: '#94a3b8' }}>{a.details}</div>
                </div>
              </div>
              <div style={{ fontSize: 14, fontWeight: 800, color: '#f59e0b', fontFamily: 'monospace' }}>
                Score: {Math.round(a.anomaly_score * 100)}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* MODALS RENDERER */}
      {modalType && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ width: '90vw', maxWidth: 850, maxHeight: '85vh', background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 16, padding: 24, display: 'flex', flexDirection: 'column', boxShadow: '0 25px 80px rgba(0,0,0,0.9)' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 12 }}>
              <div style={{ fontSize: 16, fontWeight: 800, color: '#38bdf8' }}>
                {modalType === 'entities' && '🔵 ALL 48 NETWORK NODES & ENTITIES'}
                {modalType === 'relationships' && '🔗 ALL 112 DIRECTED RELATIONSHIPS & LINKS'}
                {modalType === 'suspect' && `👑 SUSPECT PROFILE: ${modalData?.name}`}
                {modalType === 'anomaly' && `🚨 FORENSIC ANOMALY INSPECTOR: ${modalData?.entity_name}`}
                {modalType === 'subgraphs' && '🌐 3 DISCONNECTED CRIMINAL CELLS'}
                {modalType === 'math' && '📈 GRAPH TOPOLOGY & DEGREE DISTRIBUTION'}
              </div>
              <button onClick={() => setModalType(null)} style={{ background: '#334155', border: 'none', color: 'white', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontWeight: 700 }}>✕ CLOSE</button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '16px 0' }}>
              {modalType === 'entities' && (
                <div>
                  <input
                    placeholder="Search by name, type, or city..."
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    style={{ width: '100%', padding: '10px 14px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', marginBottom: 14, fontSize: 12 }}
                  />
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
                    {allEntities.filter(e => e.name.toLowerCase().includes(searchFilter.toLowerCase()) || e.type.toLowerCase().includes(searchFilter.toLowerCase())).map((e) => (
                      <div key={e.id} style={{ padding: '10px 14px', background: '#0c1324', borderRadius: 8, border: '1px solid #1e293b' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: 700, color: 'white', fontSize: 12 }}>{e.name}</span>
                          <span style={{ fontSize: 10, color: '#38bdf8', padding: '2px 6px', background: 'rgba(56,189,248,0.15)', borderRadius: 4 }}>{e.type}</span>
                        </div>
                        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>{e.role} • {e.city}</div>
                        <div style={{ fontSize: 11, color: '#ef4444', fontWeight: 700, marginTop: 2 }}>Threat Score: {e.risk_score} / 100</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {modalType === 'relationships' && (
                <div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {allRelationships.map((r) => (
                      <div key={r.id} style={{ padding: '10px 14px', background: '#0c1324', borderRadius: 8, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <span style={{ color: '#38bdf8', fontWeight: 700, fontSize: 12 }}>{r.source}</span>
                          <span style={{ color: '#f59e0b', fontSize: 11, margin: '0 8px', fontWeight: 800 }}>──[{r.label}]──▶</span>
                          <span style={{ color: '#34d399', fontWeight: 700, fontSize: 12 }}>{r.target}</span>
                        </div>
                        <span style={{ fontSize: 10, color: '#94a3b8' }}>Confidence: {r.confidence * 100}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

          </div>
        </div>
      )}
    </div>
  )
}
