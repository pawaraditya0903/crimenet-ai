import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Settings() {
  const [activeSubTab, setActiveSubTab] = useState<'security' | 'alerts' | 'theme' | 'forensics' | 'agency' | 'roster'>('security')
  
  // Investigators
  const [investigators, setInvestigators] = useState<any[]>([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [newName, setNewName] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [newRole, setNewRole] = useState('Cyber Forensics & CDR Analyst')
  const [newClearance, setNewClearance] = useState('Top Secret / Level 5')
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  
  // 1. Security & Biometrics
  const [faceSensitivity, setFaceSensitivity] = useState(62)
  const [autoLockTimeout, setAutoLockTimeout] = useState(30)
  const [requirePasswordComplexity, setRequirePasswordComplexity] = useState(true)
  const [multiFrameAveraging, setMultiFrameAveraging] = useState(true)

  // 2. Audio & Alerts
  const [soundEnabled, setSoundEnabled] = useState(true)
  const [audioTheme, setAudioTheme] = useState('tactical')
  const [desktopNotifications, setDesktopNotifications] = useState(true)
  const [toastDuration, setToastDuration] = useState(6)
  const [criticalAlertsOnlySound, setCriticalAlertsOnlySound] = useState(false)

  // 3. Visual & HUD
  const [accentTheme, setAccentTheme] = useState('cyan')
  const [compactMode, setCompactMode] = useState(false)
  const [scanlinesEffect, setScanlinesEffect] = useState(true)
  const [reduceMotion, setReduceMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)

  // 4. Forensics & Analytics Engine
  const [defaultCase, setDefaultCase] = useState('c1')
  const [graphLayout, setGraphLayout] = useState('cose')
  const [simulationTickRate, setSimulationTickRate] = useState(4)
  const [anomalyContamination, setAnomalyContamination] = useState(0.05)
  const [pmlaThresholdInr, setPmlaThresholdInr] = useState(50000)

  // 5. Agency & Jurisdiction
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
    // Load Investigators
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

    // Load Settings
    axios.get('/api/settings')
      .then(r => {
        if (r.data) {
          const d = r.data
          if (d.agency) setAgency(d.agency)
          if (d.jurisdiction) setJurisdiction(d.jurisdiction)
          if (d.retention) setRetention(d.retention)
          if (d.telegram_alerts !== undefined) setTelegramAlerts(d.telegram_alerts)
          if (d.sms_raid_broadcast !== undefined) setSmsRaidBroadcast(d.sms_raid_broadcast)
          
          if (d.face_sensitivity !== undefined) setFaceSensitivity(d.face_sensitivity)
          if (d.auto_lock_timeout !== undefined) setAutoLockTimeout(d.auto_lock_timeout)
          if (d.require_password_complexity !== undefined) setRequirePasswordComplexity(d.require_password_complexity)
          if (d.multi_frame_averaging !== undefined) setMultiFrameAveraging(d.multi_frame_averaging)

          if (d.sound_enabled !== undefined) setSoundEnabled(d.sound_enabled)
          if (d.audio_theme) setAudioTheme(d.audio_theme)
          if (d.desktop_notifications !== undefined) setDesktopNotifications(d.desktop_notifications)
          if (d.toast_duration !== undefined) setToastDuration(d.toast_duration)
          if (d.critical_alerts_only_sound !== undefined) setCriticalAlertsOnlySound(d.critical_alerts_only_sound)

          if (d.accent_theme) setAccentTheme(d.accent_theme)
          if (d.compact_mode !== undefined) setCompactMode(d.compact_mode)
          if (d.scanlines_effect !== undefined) setScanlinesEffect(d.scanlines_effect)
          if (d.reduce_motion !== undefined) setReduceMotion(d.reduce_motion)
          if (d.high_contrast !== undefined) setHighContrast(d.high_contrast)

          if (d.default_case) setDefaultCase(d.default_case)
          if (d.graph_layout) setGraphLayout(d.graph_layout)
          if (d.simulation_tick_rate !== undefined) setSimulationTickRate(d.simulation_tick_rate)
          if (d.anomaly_contamination !== undefined) setAnomalyContamination(d.anomaly_contamination)
          if (d.pmla_threshold_inr !== undefined) setPmlaThresholdInr(d.pmla_threshold_inr)
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
    try {
      const res = await axios.post('/api/investigators', {
        name: newName,
        email: newEmail || `${newName.toLowerCase().replace(/\s+/g, '')}@crimenet.ai`,
        role: newRole,
        clearance: newClearance,
        skills: selectedSkills.length > 0 ? selectedSkills : ["Field Investigation"]
      })
      setInvestigators([...investigators, res.data.investigator])
    } catch {
      setInvestigators([...investigators, {
        id: `inv-${Date.now()}`,
        name: newName,
        email: newEmail || `${newName.toLowerCase().replace(/\s+/g, '')}@crimenet.ai`,
        badge: `INV-2026-${newName.substring(0, 2).toUpperCase()}${Math.floor(Math.random() * 89 + 10)}`,
        role: newRole,
        clearance: newClearance,
        skills: selectedSkills.length > 0 ? selectedSkills : ["Field Investigation"]
      }])
    }
    setNewName('')
    setNewEmail('')
    setSelectedSkills([])
    setShowAddModal(false)
  }

  const handleDeleteInvestigator = async (id: string) => {
    try { await axios.delete(`/api/investigators/${id}`) } catch {}
    setInvestigators(investigators.filter(i => i.id !== id))
  }

  const handleSaveSettings = async () => {
    const payload = {
      agency,
      jurisdiction,
      retention,
      telegram_alerts: telegramAlerts,
      sms_raid_broadcast: smsRaidBroadcast,
      face_sensitivity: faceSensitivity,
      auto_lock_timeout: autoLockTimeout,
      require_password_complexity: requirePasswordComplexity,
      multi_frame_averaging: multiFrameAveraging,
      sound_enabled: soundEnabled,
      audio_theme: audioTheme,
      desktop_notifications: desktopNotifications,
      toast_duration: toastDuration,
      critical_alerts_only_sound: criticalAlertsOnlySound,
      accent_theme: accentTheme,
      compact_mode: compactMode,
      scanlines_effect: scanlinesEffect,
      reduce_motion: reduceMotion,
      high_contrast: highContrast,
      default_case: defaultCase,
      graph_layout: graphLayout,
      simulation_tick_rate: simulationTickRate,
      anomaly_contamination: anomalyContamination,
      pmla_threshold_inr: pmlaThresholdInr
    }

    try {
      await axios.post('/api/settings', payload)
      localStorage.setItem('crimenet_settings', JSON.stringify(payload))
    } catch {}

    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const subTabs = [
    { id: 'security', label: '🔐 Security & Biometrics', desc: 'Face ID sensitivity & session timeouts' },
    { id: 'alerts', label: '🔔 Audio & Alerts', desc: 'Synthesizer sirens & toast notifications' },
    { id: 'theme', label: '🎨 Visual & HUD', desc: 'Accent colors, scanlines & layout density' },
    { id: 'forensics', label: '📊 Forensic Engine', desc: 'Graph algorithms & PMLA thresholds' },
    { id: 'agency', label: '🏛️ Agency & Governance', desc: 'Command hub & retention compliance' },
    { id: 'roster', label: '👮 Field Investigators', desc: 'Clearance roster & tactical skill tags' }
  ]

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20, paddingBottom: 60 }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 900, color: 'white', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span>⚙️</span> Platform Settings & Command Configuration
          </h2>
          <p style={{ fontSize: 12.5, color: '#94a3b8', marginTop: 2 }}>
            Manage biometric security thresholds, tactical telemetry, visual HUD themes, and investigator roster.
          </p>
        </div>
        <button
          onClick={handleSaveSettings}
          style={{
            padding: '10px 22px',
            borderRadius: 10,
            background: saved ? '#059669' : 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)',
            color: 'white',
            border: 'none',
            fontWeight: 800,
            fontSize: 12.5,
            cursor: 'pointer',
            boxShadow: '0 0 20px rgba(56, 189, 248, 0.35)',
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}
        >
          <span>{saved ? '✓' : '💾'}</span>
          <span>{saved ? 'Settings Saved & Synchronized!' : 'Save All Settings'}</span>
        </button>
      </div>

      {/* Sub-Tabs Bar */}
      <div style={{ display: 'flex', gap: 6, overflowX: 'auto', paddingBottom: 4, scrollbarWidth: 'none' }}>
        {subTabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id as any)}
            style={{
              padding: '8px 14px',
              borderRadius: 8,
              border: activeSubTab === tab.id ? '1px solid #38bdf8' : '1px solid #1e293b',
              background: activeSubTab === tab.id ? 'rgba(56, 189, 248, 0.15)' : '#0f172a',
              color: activeSubTab === tab.id ? '#38bdf8' : '#94a3b8',
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: 🔐 SECURITY & BIOMETRICS */}
      {activeSubTab === 'security' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="glass-panel" style={{ padding: 22, borderRadius: 14 }}>
            <div style={{ fontSize: 13.5, fontWeight: 900, color: '#38bdf8', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>📸</span> ZERO-MEAN BIOMETRIC FACE CORRELATION (ZNCC ENGINE)
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <label style={{ fontSize: 12, color: 'white', fontWeight: 700 }}>
                    Biometric Acceptance Threshold ({faceSensitivity}% Similarity Required)
                  </label>
                  <span style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: faceSensitivity <= 65 ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)', color: faceSensitivity <= 65 ? '#34d399' : '#f59e0b', fontWeight: 800 }}>
                    {faceSensitivity <= 65 ? '✓ RECOMMENDED (Adaptive Multi-Frame)' : '⚠️ STRICT (May false-reject on low light)'}
                  </span>
                </div>
                <input
                  type="range"
                  min="45"
                  max="85"
                  value={faceSensitivity}
                  onChange={(e) => setFaceSensitivity(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#38bdf8', cursor: 'pointer' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#64748b', marginTop: 4 }}>
                  <span>45% (Permissive)</span>
                  <span>62% (Optimal Balance)</span>
                  <span>85% (Ultra Strict)</span>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
                <div style={{ padding: 14, borderRadius: 10, background: '#020617', border: '1px solid #1e293b' }}>
                  <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={multiFrameAveraging}
                      onChange={(e) => setMultiFrameAveraging(e.target.checked)}
                      style={{ accentColor: '#38bdf8', width: 16, height: 16 }}
                    />
                    <div>
                      <div style={{ fontWeight: 800 }}>7-Frame Temporal Averaging</div>
                      <div style={{ fontSize: 10.5, color: '#94a3b8' }}>Averages 7 consecutive video frames to cancel noise & shadow shifts</div>
                    </div>
                  </label>
                </div>

                <div style={{ padding: 14, borderRadius: 10, background: '#020617', border: '1px solid #1e293b' }}>
                  <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={requirePasswordComplexity}
                      onChange={(e) => setRequirePasswordComplexity(e.target.checked)}
                      style={{ accentColor: '#38bdf8', width: 16, height: 16 }}
                    />
                    <div>
                      <div style={{ fontWeight: 800 }}>Enforce Strong Master Passcode</div>
                      <div style={{ fontSize: 10.5, color: '#94a3b8' }}>Requires min 8 chars, 1 uppercase letter, 1 digit, and 1 symbol</div>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: 22, borderRadius: 14 }}>
            <div style={{ fontSize: 13.5, fontWeight: 900, color: '#38bdf8', marginBottom: 14 }}>
              ⏱️ SESSION SECURITY & AUTO-LOCKDOWN
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
              <div>
                <label style={{ fontSize: 11.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>
                  Inactivity Auto-Lockout Timer
                </label>
                <select
                  value={autoLockTimeout}
                  onChange={(e) => setAutoLockTimeout(Number(e.target.value))}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
                >
                  <option value="5">5 Minutes (Ultra Secure)</option>
                  <option value="15">15 Minutes</option>
                  <option value="30">30 Minutes (Recommended)</option>
                  <option value="60">60 Minutes</option>
                  <option value="0">Disabled / Never Auto-Lock</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: 11.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>
                  Cryptographic JWT Token Lifespan
                </label>
                <select
                  defaultValue="86400"
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
                >
                  <option value="86400">24 Hours (HMAC-SHA256)</option>
                  <option value="604800">7 Days Standby</option>
                  <option value="3600">1 Hour Session (High Security)</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: 🔔 AUDIO & ALERTS */}
      {activeSubTab === 'alerts' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="glass-panel" style={{ padding: 22, borderRadius: 14 }}>
            <div style={{ fontSize: 13.5, fontWeight: 900, color: '#38bdf8', marginBottom: 14 }}>
              🔊 WEB AUDIO TACTICAL SYNTHESIZER
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
              <div style={{ padding: 14, borderRadius: 10, background: '#020617', border: '1px solid #1e293b' }}>
                <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={soundEnabled}
                    onChange={(e) => setSoundEnabled(e.target.checked)}
                    style={{ accentColor: '#38bdf8', width: 16, height: 16 }}
                  />
                  <div>
                    <div style={{ fontWeight: 800 }}>Tactical Sound Effects</div>
                    <div style={{ fontSize: 10.5, color: '#94a3b8' }}>Play synthesizer beeps, radar pings, and access alerts</div>
                  </div>
                </label>
              </div>

              <div>
                <label style={{ fontSize: 11.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>Audio Sound Palette</label>
                <select
                  value={audioTheme}
                  onChange={(e) => setAudioTheme(e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
                >
                  <option value="tactical">Tactical Cyber (Futuristic Synths)</option>
                  <option value="minimal">Minimalist Subtle (Gentle Blips)</option>
                  <option value="stealth">Stealth / Low Pitch</option>
                </select>
              </div>

              <div style={{ padding: 14, borderRadius: 10, background: '#020617', border: '1px solid #1e293b' }}>
                <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={criticalAlertsOnlySound}
                    onChange={(e) => setCriticalAlertsOnlySound(e.target.checked)}
                    style={{ accentColor: '#38bdf8', width: 16, height: 16 }}
                  />
                  <div>
                    <div style={{ fontWeight: 800 }}>Chime On Critical Threat Only</div>
                    <div style={{ fontSize: 10.5, color: '#94a3b8' }}>Suppress background pings and only sound alarm on red incidents</div>
                  </div>
                </label>
              </div>

              <div>
                <label style={{ fontSize: 11.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>
                  Alert Toast Auto-Dismiss ({toastDuration}s)
                </label>
                <input
                  type="range"
                  min="3"
                  max="15"
                  value={toastDuration}
                  onChange={(e) => setToastDuration(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#38bdf8', cursor: 'pointer' }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: 🎨 VISUAL & HUD THEME */}
      {activeSubTab === 'theme' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="glass-panel" style={{ padding: 22, borderRadius: 14 }}>
            <div style={{ fontSize: 13.5, fontWeight: 900, color: '#38bdf8', marginBottom: 14 }}>
              🎨 CYBER DEFENSE ACCENT COLOR PALETTE
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 12 }}>
              {[
                { id: 'cyan', label: 'Tactical Cyan', color: '#38bdf8', border: '#0284c7' },
                { id: 'red', label: 'Crimson Defense', color: '#ef4444', border: '#b91c1c' },
                { id: 'green', label: 'Matrix Emerald', color: '#10b981', border: '#047857' },
                { id: 'amber', label: 'Amber Intercept', color: '#f59e0b', border: '#b45309' },
                { id: 'purple', label: 'Cyber Violet', color: '#a855f7', border: '#7e22ce' }
              ].map(theme => (
                <div
                  key={theme.id}
                  onClick={() => setAccentTheme(theme.id)}
                  style={{
                    padding: '12px 14px',
                    borderRadius: 10,
                    background: accentTheme === theme.id ? 'rgba(15, 23, 42, 0.9)' : '#020617',
                    border: accentTheme === theme.id ? `2px solid ${theme.color}` : '1px solid #1e293b',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10
                  }}
                >
                  <div style={{ width: 18, height: 18, borderRadius: '50%', background: theme.color, boxShadow: `0 0 10px ${theme.color}` }} />
                  <span style={{ fontSize: 12, fontWeight: 700, color: 'white' }}>{theme.label}</span>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 20, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
              <div style={{ padding: 14, borderRadius: 10, background: '#020617', border: '1px solid #1e293b' }}>
                <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={scanlinesEffect}
                    onChange={(e) => setScanlinesEffect(e.target.checked)}
                    style={{ accentColor: '#38bdf8', width: 16, height: 16 }}
                  />
                  <div>
                    <div style={{ fontWeight: 800 }}>CRT Phosphor Scanline Overlay</div>
                    <div style={{ fontSize: 10.5, color: '#94a3b8' }}>Authentic military CRT monitor scanline texture</div>
                  </div>
                </label>
              </div>

              <div style={{ padding: 14, borderRadius: 10, background: '#020617', border: '1px solid #1e293b' }}>
                <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={compactMode}
                    onChange={(e) => setCompactMode(e.target.checked)}
                    style={{ accentColor: '#38bdf8', width: 16, height: 16 }}
                  />
                  <div>
                    <div style={{ fontWeight: 800 }}>Compact Information Density</div>
                    <div style={{ fontSize: 10.5, color: '#94a3b8' }}>Tighter paddings and denser tables for analyst screens</div>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: 📊 FORENSIC ENGINE */}
      {activeSubTab === 'forensics' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="glass-panel" style={{ padding: 22, borderRadius: 14 }}>
            <div style={{ fontSize: 13.5, fontWeight: 900, color: '#38bdf8', marginBottom: 14 }}>
              🧠 GRAPH ML & FORENSIC PIPELINE ALGORITHMS
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
              <div>
                <label style={{ fontSize: 11.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>Default Graph Topology Engine</label>
                <select
                  value={graphLayout}
                  onChange={(e) => setGraphLayout(e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
                >
                  <option value="cose">COSE Force-Directed (Physics Springs)</option>
                  <option value="concentric">Concentric Centrality Rings (PageRank Hierarchy)</option>
                  <option value="breadthfirst">Breadth-First Command Tree</option>
                  <option value="grid">Orthogonal Grid Matrix</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: 11.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>PMLA Mandatory Threshold Detection</label>
                <select
                  value={pmlaThresholdInr}
                  onChange={(e) => setPmlaThresholdInr(Number(e.target.value))}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
                >
                  <option value="50000">₹50,000 (FIU-IND Statutory Threshold)</option>
                  <option value="25000">₹25,000 (Aggressive Micro-Smurfing)</option>
                  <option value="100000">₹1,00,000 (Macro Wire Structuring)</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: 11.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>Live Background Telemetry Rate</label>
                <select
                  value={simulationTickRate}
                  onChange={(e) => setSimulationTickRate(Number(e.target.value))}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
                >
                  <option value="2">High Frequency (Every 2 Seconds)</option>
                  <option value="4">Standard Operational (Every 4 Seconds)</option>
                  <option value="8">Low Bandwidth (Every 8 Seconds)</option>
                  <option value="0">Paused / On-Demand Only</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: 11.5, color: '#94a3b8', display: 'block', marginBottom: 6 }}>Default Case File on Boot</label>
                <select
                  value={defaultCase}
                  onChange={(e) => setDefaultCase(e.target.value)}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12 }}
                >
                  <option value="c1">Operation Blue Thunder (Cross-border Narcotics & Hawala)</option>
                  <option value="c2">Mehta Enterprises Layering Audit (Offshore Shells)</option>
                  <option value="c3">Goregaon Warehouse Surveillance (Contraband Transit)</option>
                  <option value="c4">Phoenix Trading LLC PMLA Petition (Account Freeze)</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: 🏛️ AGENCY & GOVERNANCE */}
      {activeSubTab === 'agency' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="glass-panel" style={{ padding: 22, borderRadius: 14 }}>
            <div style={{ fontSize: 13.5, fontWeight: 900, color: '#38bdf8', marginBottom: 14 }}>
              🏛️ LAW ENFORCEMENT JURISDICTION & POLICY
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
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
                    <input type="checkbox" checked={telegramAlerts} onChange={(e) => setTelegramAlerts(e.target.checked)} style={{ accentColor: '#38bdf8' }} />
                    Encrypted Telegram Channel
                  </label>
                  <label style={{ fontSize: 12, color: 'white', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
                    <input type="checkbox" checked={smsRaidBroadcast} onChange={(e) => setSmsRaidBroadcast(e.target.checked)} style={{ accentColor: '#38bdf8' }} />
                    Tactical SMS Dispatch
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: 👮 FIELD INVESTIGATORS */}
      {activeSubTab === 'roster' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="glass-panel" style={{ padding: 22, borderRadius: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <div style={{ fontSize: 13.5, fontWeight: 900, color: '#38bdf8' }}>
                👮 ACTIVE FIELD INVESTIGATORS & SPECIALIZED SKILLS
              </div>
              <button
                onClick={() => setShowAddModal(true)}
                style={{ padding: '8px 16px', borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 12, cursor: 'pointer' }}
              >
                + Add Field Investigator
              </button>
            </div>

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
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: 10
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
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
        </div>
      )}

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
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 6 }}>
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
