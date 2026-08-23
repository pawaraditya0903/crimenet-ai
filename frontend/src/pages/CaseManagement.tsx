import { useEffect, useState } from 'react'

export default function CaseManagement() {
  const [cases, setCases] = useState<any[]>([
    { id: 'c1', title: 'Operation Blue Thunder', desc: 'Cross-border hawala & narcotics ring', stage: 'active', priority: 'critical', suspects: ['Arjun Mehta', 'Mohammed Rafiq'], squad: 'Alpha Team (Raid Unit)' },
    { id: 'c2', title: 'Mehta Enterprises Audit', desc: 'Shell corporate layering & ₹8.75 Cr round-tripping', stage: 'evidence', priority: 'high', suspects: ['Priya Desai'], squad: 'Forensic Audit Cell' },
    { id: 'c3', title: 'Goregaon Warehouse Surveillance', desc: 'Contraband vehicle transit monitoring', stage: 'warrant', priority: 'critical', suspects: ['Vikram Singh'], squad: 'Tactical Recon Unit' },
    { id: 'c4', title: 'Phoenix Trading LLC PMLA Petition', desc: 'Offshore account freezing under Section 17', stage: 'court', priority: 'high', suspects: ['Arjun Mehta', 'Priya Desai'], squad: 'Legal & Judicial Wing' },
  ])

  const [newTitle, setNewTitle] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [showModal, setShowModal] = useState(false)

  const STAGES = [
    { id: 'evidence', label: '🔍 Evidence Gathering', color: '#38bdf8' },
    { id: 'active', label: '📡 Active Surveillance', color: '#f59e0b' },
    { id: 'warrant', label: '⚡ Warrant / Raid Ready', color: '#ef4444' },
    { id: 'court', label: '⚖️ Court Prosecution', color: '#10b981' }
  ]

  const moveStage = (caseId: string, nextStage: string) => {
    setCases(cases.map(c => c.id === caseId ? { ...c, stage: nextStage } : c))
  }

  const handleCreateCase = () => {
    if (!newTitle.trim()) return
    setCases([...cases, {
      id: `c${cases.length + 1}`,
      title: newTitle,
      desc: newDesc || 'Active case file initiated by Aditya Pawar',
      stage: 'evidence',
      priority: 'high',
      suspects: ['Target Under Identification'],
      squad: 'Cyber & Forensic Cell'
    }])
    setNewTitle('')
    setNewDesc('')
    setShowModal(false)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, height: 'calc(100vh - 120px)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800, color: 'white' }}>📋 Tactical Case Management Kanban Board</h2>
          <p style={{ fontSize: 12, color: '#94a3b8' }}>Lead Commander: <b>Aditya Pawar</b> · Move cases across investigation stages with 1 click.</p>
        </div>
        <button onClick={() => setShowModal(true)} style={{ padding: '8px 16px', borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 12, cursor: 'pointer' }}>
          + Open New Investigation Case
        </button>
      </div>

      {/* 4 Kanban Columns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, flex: 1, overflowY: 'auto' }}>
        {STAGES.map((st) => (
          <div key={st.id} style={{ background: 'rgba(15, 23, 42, 0.75)', borderRadius: 12, border: `1px solid ${st.color}`, padding: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 8 }}>
              <span style={{ fontSize: 12, fontWeight: 800, color: st.color }}>{st.label}</span>
              <span style={{ fontSize: 11, background: '#020617', padding: '2px 6px', borderRadius: 10, color: 'white', fontWeight: 700 }}>
                {cases.filter(c => c.stage === st.id).length}
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, flex: 1, overflowY: 'auto' }}>
              {cases.filter(c => c.stage === st.id).map((c) => (
                <div key={c.id} style={{ background: '#0c1324', borderRadius: 8, padding: 12, border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 13, fontWeight: 800, color: 'white' }}>{c.title}</span>
                    <span style={{ fontSize: 9, padding: '2px 6px', borderRadius: 4, background: c.priority === 'critical' ? '#7f1d1d' : '#1e3a8a', color: 'white', fontWeight: 800 }}>
                      {c.priority.toUpperCase()}
                    </span>
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8' }}>{c.desc}</div>
                  <div style={{ fontSize: 10, color: '#38bdf8', fontWeight: 700 }}>🎯 Suspects: {c.suspects.join(', ')}</div>
                  <div style={{ fontSize: 10, color: '#10b981' }}>👮 Squad: {c.squad}</div>

                  {/* Stage Advance Buttons */}
                  <div style={{ display: 'flex', gap: 4, marginTop: 6, paddingTop: 6, borderTop: '1px solid #1e293b' }}>
                    {st.id !== 'evidence' && (
                      <button onClick={() => moveStage(c.id, STAGES[STAGES.findIndex(s => s.id === st.id) - 1].id)} style={{ flex: 1, padding: 4, borderRadius: 4, background: '#1e293b', border: 'none', color: '#cbd5e1', fontSize: 10, cursor: 'pointer' }}>
                        ◀ Back
                      </button>
                    )}
                    {st.id !== 'court' && (
                      <button onClick={() => moveStage(c.id, STAGES[STAGES.findIndex(s => s.id === st.id) + 1].id)} style={{ flex: 1, padding: 4, borderRadius: 4, background: '#1d4ed8', border: 'none', color: 'white', fontSize: 10, fontWeight: 700, cursor: 'pointer' }}>
                        Advance ▶
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* New Case Modal */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ width: '90vw', maxWidth: 500, background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 14, padding: 24 }}>
            <h3 style={{ color: 'white', fontSize: 15, fontWeight: 800, marginBottom: 12 }}>Open New Investigation Case</h3>
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Case Title (e.g. Operation Falcon Hawala)..."
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginBottom: 10 }}
            />
            <textarea
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Case description and preliminary intelligence..."
              style={{ width: '100%', height: 80, padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginBottom: 14 }}
            />
            <div style={{ display: 'flex', gap: 10 }}>
              <button onClick={handleCreateCase} style={{ flex: 1, padding: 10, borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, cursor: 'pointer' }}>Create Case</button>
              <button onClick={() => setShowModal(false)} style={{ padding: '10px 16px', borderRadius: 8, background: '#334155', color: 'white', border: 'none', cursor: 'pointer' }}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
