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
    axios.get('/api/investigators')
      .then(r => {
        if (r.data && r.data.investigators && r.data.investigators.length > 0) {
          setInvestigators(r.data.investigators)
        } else {
          setInvestigators([
            { id: "inv-1", name: "Aditya Pawar", email: "aditya.pawar@crimenet.ai", badge: "INV-2026-AP01", role: "Chief Intelligence Architect & Lead", clearance: "Top Secret / Level 5", skills: ["Telecom CDR & Tower Triangulation", "Cyber Forensics & Dark Web Tracing", "PMLA & Hawala Financial Auditing"] },
            { id: "inv-2", name: "Ramesh Sharma", email: "ramesh.sharma@crimenet.ai", badge: "INV-2026-RS02", role: "Hawala & PMLA Financial Auditor", clearance: "Secret / Level 4", skills: ["PMLA & Hawala Financial Auditing", "Cryptocurrency & Blockchain Forensics"] },
            { id: "inv-3", name: "Suresh Kadam", email: "suresh.kadam@crimenet.ai", badge: "INV-2026-SK03", role: "Cellular CDR & Tower Analyst", clearance: "Secret / Level 4", skills: ["Telecom CDR & Tower Triangulation", "ANPR Vehicle Toll Interception"] }
          ])
        }
      })
      .catch(() => {
        setInvestigators([
          { id: "inv-1", name: "Aditya Pawar", email: "aditya.pawar@crimenet.ai", badge: "INV-2026-AP01", role: "Chief Intelligence Architect & Lead", clearance: "Top Secret / Level 5", skills: ["Telecom CDR & Tower Triangulation", "Cyber Forensics & Dark Web Tracing", "PMLA & Hawala Financial Auditing"] },
          { id: "inv-2", name: "Ramesh Sharma", email: "ramesh.sharma@crimenet.ai", badge: "INV-2026-RS02", role: "Hawala & PMLA Financial Auditor", clearance: "Secret / Level 4", skills: ["PMLA & Hawala Financial Auditing", "Cryptocurrency & Blockchain Forensics"] },
          { id: "inv-3", name: "Suresh Kadam", email: "suresh.kadam@crimenet.ai", badge: "INV-2026-SK03", role: "Cellular CDR & Tower Analyst", clearance: "Secret / Level 4", skills: ["Telecom CDR & Tower Triangulation", "ANPR Vehicle Toll Interception"] }
        ])
      })

    axios.get('/api/settings')
      .then(r => {
        if (r.data) {
          if (r.data.agency) setAgency(r.data.agency)
          if (r.data.jurisdiction) setJurisdiction(r.data.jurisdiction)
          if (r.data.retention) setRetention(r.data.retention)
          if (r.data.telegram_alerts !== undefined) setTelegramAlerts(r.data.telegram_alerts)
          if (r.data.sms_raid_broadcast !== undefined) setSmsRaidBroadcast(r.data.sms_raid_broadcast)
        }
      })
      .catch(() => {})
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
    const res = await axios.post('/api/investigators', {
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
    await axios.delete(`/api/investigators/${id}`)
    setInvestigators(investigators.filter(i => i.id !== id))
  }

  const handleSaveSettings = async () => {
    try {
      await axios.post('/api/settings', {
        agency,
        jurisdiction,
        retention,
        telegram_alerts: telegramAlerts,
        sms_raid_broadcast: smsRaidBroadcast
      })
    } catch {}
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
            <label style={{ fontSize: 11, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Jurisdiction Command Hub</label>
            <input
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
            />
          </div>
          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Forensic Data Retention Policy</label>
            <input
              value={retention}
              onChange={(e) => setRetention(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
            />
          </div>
          <div>
            <label style={{ fontSize: 11, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Emergency Broadcast Channels</label>
            <div style={{ display: 'flex', gap: 16, marginTop: 10 }}>
              <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input type="checkbox" checked={telegramAlerts} onChange={(e) => setTelegramAlerts(e.target.checked)} />
                Encrypted Telegram Channel
              </label>
              <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                <input type="checkbox" checked={smsRaidBroadcast} onChange={(e) => setSmsRaidBroadcast(e.target.checked)} />
                Tactical SMS Dispatch
              </label>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 18, display: 'flex', alignItems: 'center', gap: 14 }}>
          <button
            onClick={handleSaveSettings}
            style={{ padding: '10px 20px', borderRadius: 8, background: '#059669', color: 'white', border: 'none', fontWeight: 800, fontSize: 12, cursor: 'pointer' }}
          >
            Save Security & Deployment Policies
          </button>
          {saved && <span style={{ color: '#34d399', fontSize: 12, fontWeight: 700 }}>✓ Settings Saved & Synchronized Successfully!</span>}
        </div>
      </div>

      {/* Add Investigator Modal */}
      {showAddModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ width: '90vw', maxWidth: 540, background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 14, padding: 24 }}>
            <h3 style={{ color: 'white', fontSize: 15, fontWeight: 800, marginBottom: 14 }}>Add Field Investigator / Officer</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div>
                <label style={{ fontSize: 10.5, color: '#94a3b8' }}>Officer Full Name</label>
                <input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Officer Name..."
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 3 }}
                />
              </div>

              <div>
                <label style={{ fontSize: 10.5, color: '#94a3b8' }}>Official Email</label>
                <input
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="officer@crimenet.ai"
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 3 }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <div>
                  <label style={{ fontSize: 10.5, color: '#94a3b8' }}>Designated Role</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    style={{ width: '100%', padding: '9px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11.5, marginTop: 3 }}
                  >
                    <option value="Cyber Forensics & CDR Analyst">Cyber Forensics & CDR Analyst</option>
                    <option value="Hawala & Financial Crime Auditor">Hawala & Financial Crime Auditor</option>
                    <option value="Tactical Raid Squad Lead">Tactical Raid Squad Lead</option>
                    <option value="Undercover Field Investigator">Undercover Field Investigator</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: 10.5, color: '#94a3b8' }}>Security Clearance</label>
                  <select
                    value={newClearance}
                    onChange={(e) => setNewClearance(e.target.value)}
                    style={{ width: '100%', padding: '9px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11.5, marginTop: 3 }}
                  >
                    <option value="Top Secret / Level 5">Top Secret / Level 5</option>
                    <option value="Secret / Level 4">Secret / Level 4</option>
                    <option value="Confidential / Level 3">Confidential / Level 3</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ fontSize: 10.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>Specialized Tactical Skills</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
                  {SKILL_OPTIONS.map((sk, idx) => (
                    <div
                      key={idx}
                      onClick={() => toggleSkill(sk)}
                      style={{
                        padding: '6px 10px',
                        borderRadius: 6,
                        background: selectedSkills.includes(sk) ? 'rgba(37,99,235,0.3)' : '#020617',
                        border: selectedSkills.includes(sk) ? '1px solid #38bdf8' : '1px solid #334155',
                        color: selectedSkills.includes(sk) ? '#38bdf8' : '#94a3b8',
                        fontSize: 10.5,
                        cursor: 'pointer'
                      }}
                    >
                      {selectedSkills.includes(sk) ? '✓ ' : '+ '}{sk}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10, marginTop: 18 }}>
              <button
                onClick={handleAddInvestigator}
                style={{ flex: 1, padding: 10, borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, cursor: 'pointer' }}
              >
                Save Officer to Roster
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                style={{ padding: '10px 16px', borderRadius: 8, background: '#334155', color: 'white', border: 'none', cursor: 'pointer' }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
