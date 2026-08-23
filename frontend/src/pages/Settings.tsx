import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Settings() {
  const [investigators, setInvestigators] = useState<any[]>([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [newName, setNewName] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [newRole, setNewRole] = useState('Cyber Forensics & CDR Analyst')
  const [newClearance, setNewClearance] = useState('Top Secret / Level 5')
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  
  // Enterprise Settings
  const [agency, setAgency] = useState('State Crime Branch — Cyber & Financial Crime Cell')
  const [jurisdiction, setJurisdiction] = useState('Western Region Headquarters (Mumbai)')
  const [retention, setRetention] = useState('90 Days Active Buffer')
  const [telegramAlerts, setTelegramAlerts] = useState(true)
  const [smsRaidBroadcast, setSmsRaidBroadcast] = useState(true)
  const [saved, setSaved] = useState(false)

  const SKILL_OPTIONS = [
    "Telecom CDR & Tower Triangulation",
    "PMLA & Hawala Financial Auditing",
    "Cyber Forensics & Dark Web Tracing",
    "Armed Tactical Raid Operations",
    "OSINT & Facial Recognition",
    "Informant Handling & Interrogation",
    "Cryptocurrency & Blockchain Forensics",
    "ANPR Vehicle Toll Interception"
  ]

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/investigators').then(r => setInvestigators(r.data.investigators || []))
  }, [])

  const toggleSkill = (skill: string) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill))
    } else {
      setSelectedSkills([...selectedSkills, skill])
    }
  }

  const handleAddInvestigator = async () => {
    if (!newName.trim()) return
    const res = await axios.post('http://127.0.0.1:8000/api/investigators', {
      name: newName,
      email: newEmail || `${newName.toLowerCase().replace(/\s+/g, '')}@crimenet.ai`,
      role: newRole,
      clearance: newClearance,
      skills: selectedSkills.length > 0 ? selectedSkills : ["Field Investigation"]
    })
    setInvestigators([...investigators, res.data.investigator])
    setNewName('')
    setNewEmail('')
    setSelectedSkills([])
    setShowAddModal(false)
  }

  const handleDeleteInvestigator = async (id: string) => {
    await axios.delete(`http://127.0.0.1:8000/api/investigators/${id}`)
    setInvestigators(investigators.filter(i => i.id !== id))
  }

  const handleSaveSettings = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20, paddingBottom: 50 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800, color: 'white' }}>⚙️ Platform Settings & Field Investigator Roster</h2>
          <p style={{ fontSize: 12, color: '#94a3b8' }}>Manage specialized investigative personnel, agency jurisdiction, and security policies.</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          style={{ padding: '8px 16px', borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 12, cursor: 'pointer' }}
        >
          + Add Field Investigator
        </button>
      </div>

      {/* Field Investigators Roster */}
      <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
        <div style={{ fontSize: 13, fontWeight: 800, color: '#38bdf8', marginBottom: 14 }}>👮 ACTIVE FIELD INVESTIGATORS & SPECIALIZED SKILLS</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {investigators.map((inv) => (
            <div
              key={inv.id}
              style={{
                padding: '14px 18px',
                borderRadius: 10,
                background: '#0c1324',
                border: '1px solid #334155',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 14, fontWeight: 800, color: 'white' }}>{inv.name}</span>
                  <span style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(56,189,248,0.15)', color: '#38bdf8', borderRadius: 4, fontWeight: 700 }}>{inv.badge}</span>
                  <span style={{ fontSize: 10, padding: '2px 6px', background: 'rgba(239,68,68,0.15)', color: '#f87171', borderRadius: 4, fontWeight: 700 }}>{inv.clearance}</span>
                </div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 3 }}>{inv.role} • {inv.email}</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
                  {(inv.skills || []).map((sk: string, idx: number) => (
                    <span key={idx} style={{ fontSize: 9.5, padding: '2px 8px', background: 'rgba(16,185,129,0.15)', color: '#34d399', borderRadius: 12, border: '1px solid rgba(16,185,129,0.3)' }}>
                      ✓ {sk}
                    </span>
                  ))}
                </div>
              </div>

              {inv.id !== 'inv-1' && (
                <button
                  onClick={() => handleDeleteInvestigator(inv.id)}
                  style={{ padding: '6px 12px', borderRadius: 6, background: '#7f1d1d', color: 'white', border: 'none', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Agency & Jurisdiction Settings */}
      <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
        <div style={{ fontSize: 13, fontWeight: 800, color: '#38bdf8', marginBottom: 14 }}>🏛️ AGENCY JURISDICTION & DEPLOYMENT POLICIES</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Law Enforcement Agency</label>
            <input
              value={agency}
              onChange={(e) => setAgency(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
            />
          </div>
          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Command Jurisdiction</label>
            <input
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
            />
          </div>
          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', display: 'block', marginBottom: 4 }}>CDR & Evidence Retention Policy</label>
            <select
              value={retention}
              onChange={(e) => setRetention(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
            >
              <option value="30 Days Active Buffer">30 Days Active Buffer</option>
              <option value="90 Days Active Buffer">90 Days Active Buffer (Standard)</option>
              <option value="1 Year Extended Archive">1 Year Extended Archive</option>
              <option value="Permanent Judicial Vault">Permanent Judicial Vault</option>
            </select>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, justifyContent: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'white', cursor: 'pointer' }}>
              <input type="checkbox" checked={telegramAlerts} onChange={(e) => setTelegramAlerts(e.target.checked)} />
              <span>Enable Instant Telegram Tactical Alerts</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'white', cursor: 'pointer' }}>
              <input type="checkbox" checked={smsRaidBroadcast} onChange={(e) => setSmsRaidBroadcast(e.target.checked)} />
              <span>Broadcast SMS on Critical Raid Escalation</span>
            </label>
          </div>
        </div>

        <button
          onClick={handleSaveSettings}
          style={{
            marginTop: 18,
            padding: '12px 24px',
            borderRadius: 8,
            background: saved ? '#059669' : '#1d4ed8',
            color: 'white',
            border: 'none',
            fontWeight: 800,
            fontSize: 13,
            cursor: 'pointer'
          }}
        >
          {saved ? '✓ System Configuration Saved!' : 'Save System Configuration'}
        </button>
      </div>

      {/* Add Investigator Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ width: '90vw', maxWidth: 600, background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 14, padding: 24 }}>
            <h3 style={{ color: 'white', fontSize: 16, fontWeight: 800, marginBottom: 14 }}>Add Specialized Field Investigator</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div>
                <label style={{ fontSize: 11, color: '#94a3b8' }}>Investigator Name</label>
                <input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Inspector Ramesh Kadam..."
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 4 }}
                />
              </div>

              <div>
                <label style={{ fontSize: 11, color: '#94a3b8' }}>Specialization Role</label>
                <input
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 4 }}
                />
              </div>

              <div>
                <label style={{ fontSize: 11, color: '#94a3b8' }}>Security Clearance Level</label>
                <select
                  value={newClearance}
                  onChange={(e) => setNewClearance(e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 4 }}
                >
                  <option value="Top Secret / Level 5">Top Secret / Level 5</option>
                  <option value="Secret / Level 4">Secret / Level 4</option>
                  <option value="Confidential / Level 3">Confidential / Level 3</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: 11, color: '#94a3b8', display: 'block', marginBottom: 6 }}>Select Specialized Skillsets</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  {SKILL_OPTIONS.map((sk, i) => (
                    <div
                      key={i}
                      onClick={() => toggleSkill(sk)}
                      style={{
                        padding: '8px 10px',
                        borderRadius: 6,
                        background: selectedSkills.includes(sk) ? 'rgba(37,99,235,0.3)' : '#020617',
                        border: selectedSkills.includes(sk) ? '1px solid #38bdf8' : '1px solid #334155',
                        color: selectedSkills.includes(sk) ? '#38bdf8' : '#94a3b8',
                        fontSize: 11,
                        cursor: 'pointer',
                        fontWeight: selectedSkills.includes(sk) ? 700 : 400
                      }}
                    >
                      {selectedSkills.includes(sk) ? '✓ ' : '+ '} {sk}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button onClick={handleAddInvestigator} style={{ flex: 1, padding: 12, borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, cursor: 'pointer' }}>Add to Squad</button>
              <button onClick={() => setShowAddModal(false)} style={{ padding: '12px 18px', borderRadius: 8, background: '#334155', color: 'white', border: 'none', cursor: 'pointer' }}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
