import React, { useState, useEffect } from 'react'
import axios from 'axios'

interface CommandBarProps {
  selectedCase: string
  onSelectCase: (caseId: string) => void
  connectionState: 'connected' | 'reconnecting' | 'offline'
  onToggleCopilot: () => void
  copilotOpen: boolean
  onSelectEntity?: (name: string) => void
  onOpenDemoTour?: () => void
}

export default function CommandBar({
  selectedCase,
  onSelectCase,
  connectionState,
  onToggleCopilot,
  copilotOpen,
  onSelectEntity,
  onOpenDemoTour
}: CommandBarProps) {
  const [utcTime, setUtcTime] = useState('')
  const [istTime, setIstTime] = useState('')
  const [spotlightOpen, setSpotlightOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [notifsOpen, setNotifsOpen] = useState(false)
  const [notifications, setNotifications] = useState<any[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [simRunning, setSimRunning] = useState(false)
  const [simSpeed, setSimSpeed] = useState(1.0)

  // Dual Clocks
  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setUtcTime(now.toUTCString().slice(17, 25) + ' UTC')
      setIstTime(now.toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour12: false }) + ' IST')
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  // Load Notifications
  const loadNotifs = async () => {
    try {
      const res = await axios.get('/api/notifications')
      setNotifications(res.data.notifications || [])
      setUnreadCount(res.data.unread_count || 0)
    } catch {}
  }

  useEffect(() => {
    loadNotifs()
    const notifTimer = setInterval(loadNotifs, 10000)
    return () => clearInterval(notifTimer)
  }, [])

  // Keyboard shortcut Ctrl+K / Cmd+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setSpotlightOpen(prev => !prev)
      }
      if (e.key === 'Escape') {
        setSpotlightOpen(false)
        setNotifsOpen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Global Search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([])
      return
    }
    axios.get(`/api/entities/search?q=${encodeURIComponent(searchQuery)}`)
      .then(res => setSearchResults(res.data.results || []))
      .catch(() => {})
  }, [searchQuery])

  // Simulation Controls
  const toggleSimulation = async () => {
    try {
      if (simRunning) {
        await axios.post('/api/simulation/pause')
        setSimRunning(false)
      } else {
        await axios.post('/api/simulation/start')
        setSimRunning(true)
      }
    } catch {}
  }

  const changeSpeed = async (speed: number) => {
    setSimSpeed(speed)
    try {
      await axios.post('/api/simulation/speed', { speed })
    } catch {}
  }

  return (
    <>
      <div style={{
        height: 52,
        background: 'linear-gradient(90deg, #090e17 0%, #0d1527 100%)',
        borderBottom: '1px solid rgba(56, 189, 248, 0.2)',
        padding: '0 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: 11.5,
        color: '#94a3b8',
        zIndex: 100
      }}>
        {/* Left Side: Case Selector & Global Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* Active Case Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#020617', padding: '4px 10px', borderRadius: 6, border: '1px solid #1e293b' }}>
            <span style={{ color: '#38bdf8', fontWeight: 800 }}>📁 CASE:</span>
            <select
              value={selectedCase}
              onChange={(e) => onSelectCase(e.target.value)}
              style={{ background: 'transparent', color: '#f8fafc', border: 'none', fontWeight: 700, fontSize: 11, outline: 'none', cursor: 'pointer' }}
            >
              <option value="all" style={{ background: '#0f172a' }}>All Active Cases (Master View)</option>
              <option value="c1" style={{ background: '#0f172a' }}>c1 - Operation Blue Thunder</option>
              <option value="c2" style={{ background: '#0f172a' }}>c2 - Mehta Layering Audit</option>
              <option value="c3" style={{ background: '#0f172a' }}>c3 - Goregaon Surveillance</option>
              <option value="c4" style={{ background: '#0f172a' }}>c4 - Phoenix PMLA Petition</option>
            </select>
          </div>

          {/* Spotlight Search Shortcut */}
          <button
            onClick={() => setSpotlightOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              background: 'rgba(15, 23, 42, 0.9)',
              border: '1px solid #334155',
              color: '#cbd5e1',
              padding: '5px 12px',
              borderRadius: 6,
              cursor: 'pointer',
              fontSize: 11
            }}
          >
            <span>🔍 Search entities, MSISDN, alerts...</span>
            <kbd style={{ background: '#020617', padding: '1px 5px', borderRadius: 4, border: '1px solid #475569', fontSize: 9.5, color: '#38bdf8' }}>Ctrl+K</kbd>
          </button>

          {/* Simulation Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(15, 23, 42, 0.7)', padding: '3px 8px', borderRadius: 6, border: '1px solid #1e293b' }}>
            <button
              onClick={toggleSimulation}
              style={{
                background: simRunning ? '#b91c1c' : '#15803d',
                color: 'white',
                border: 'none',
                padding: '3px 8px',
                borderRadius: 4,
                fontWeight: 800,
                fontSize: 10,
                cursor: 'pointer'
              }}
            >
              {simRunning ? '⏸ Pause Stream' : '▶ Live Stream'}
            </button>
            <span style={{ fontSize: 10, color: '#64748b' }}>Speed:</span>
            {[1, 2, 5].map(s => (
              <button
                key={s}
                onClick={() => changeSpeed(s)}
                style={{
                  background: simSpeed === s ? '#38bdf8' : 'transparent',
                  color: simSpeed === s ? '#020617' : '#94a3b8',
                  border: 'none',
                  padding: '2px 4px',
                  borderRadius: 3,
                  fontWeight: 700,
                  fontSize: 9.5,
                  cursor: 'pointer'
                }}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>

        {/* Right Side: Clocks, Connection Badge, Notifications, Copilot Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {/* Connection Status Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            padding: '3px 8px',
            borderRadius: 4,
            background: connectionState === 'connected' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: `1px solid ${connectionState === 'connected' ? '#10b981' : '#ef4444'}`,
            color: connectionState === 'connected' ? '#34d399' : '#f87171',
            fontWeight: 800,
            fontSize: 10
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: connectionState === 'connected' ? '#34d399' : '#f87171' }}></span>
            {connectionState === 'connected' ? 'SOCKET LIVE' : connectionState.toUpperCase()}
          </div>

          {/* Dual Clocks */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'monospace', fontSize: 10.5, color: '#cbd5e1' }}>
            <span>🕒 {utcTime}</span>
            <span style={{ color: '#475569' }}>|</span>
            <span>{istTime}</span>
          </div>

          {/* Notification Bell */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setNotifsOpen(prev => !prev)}
              style={{
                position: 'relative',
                background: notifsOpen ? '#334155' : '#1e293b',
                border: '1px solid #334155',
                color: 'white',
                padding: '6px 10px',
                borderRadius: 6,
                cursor: 'pointer',
                fontSize: 13
              }}
            >
              🔔
              {unreadCount > 0 && (
                <span style={{
                  position: 'absolute',
                  top: -4,
                  right: -4,
                  background: '#ef4444',
                  color: 'white',
                  borderRadius: '50%',
                  width: 16,
                  height: 16,
                  fontSize: 9,
                  fontWeight: 900,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notification Dropdown */}
            {notifsOpen && (
              <div style={{
                position: 'absolute',
                top: 40,
                right: 0,
                width: 320,
                background: '#0f172a',
                border: '1px solid #38bdf8',
                borderRadius: 10,
                padding: 12,
                boxShadow: '0 20px 50px rgba(0,0,0,0.9)',
                zIndex: 2000
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 8, marginBottom: 8 }}>
                  <span style={{ fontWeight: 800, color: 'white', fontSize: 12 }}>Investigation Notifications</span>
                  <button
                    onClick={async () => {
                      await axios.post('/api/notifications/clear-all')
                      loadNotifs()
                    }}
                    style={{ background: 'transparent', border: 'none', color: '#38bdf8', fontSize: 10, cursor: 'pointer' }}
                  >
                    Clear All
                  </button>
                </div>
                <div style={{ maxHeight: 280, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {notifications.map((n) => (
                    <div key={n.id} style={{ padding: '8px 10px', borderRadius: 6, background: '#020617', border: n.severity === 'critical' ? '1px solid rgba(239,68,68,0.4)' : '1px solid #1e293b', fontSize: 11 }}>
                      <div style={{ fontWeight: 700, color: n.severity === 'critical' ? '#f87171' : '#38bdf8' }}>{n.title}</div>
                      <div style={{ color: '#94a3b8', fontSize: 10, marginTop: 2 }}>{n.details}</div>
                      <div style={{ color: '#64748b', fontSize: 9, marginTop: 3 }}>{n.timestamp} · Case: {n.case_id}</div>
                    </div>
                  ))}
                  {notifications.length === 0 && <div style={{ textAlign: 'center', color: '#64748b', padding: 20, fontSize: 11 }}>No active notifications</div>}
                </div>
              </div>
            )}
          </div>

          {/* 5-Minute Evaluator / Judge Demo Tour Button */}
          {onOpenDemoTour && (
            <button
              onClick={onOpenDemoTour}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                background: 'linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%)',
                border: '1px solid #c084fc',
                color: 'white',
                padding: '6px 12px',
                borderRadius: 20,
                cursor: 'pointer',
                fontWeight: 800,
                fontSize: 11,
                boxShadow: '0 0 15px rgba(192, 132, 252, 0.4)',
                transition: '0.2s'
              }}
              title="Launch 5-Minute Interactive Evaluator & Judge Presentation Tour"
            >
              <span>🎬</span>
              <span>5-MIN JUDGE TOUR</span>
            </button>
          )}

          {/* CrimeNet AI Copilot Toggle Button */}
          <button
            onClick={onToggleCopilot}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: copilotOpen ? 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)' : 'rgba(56, 189, 248, 0.15)',
              border: '1px solid #38bdf8',
              color: copilotOpen ? 'white' : '#38bdf8',
              padding: '6px 14px',
              borderRadius: 20,
              cursor: 'pointer',
              fontWeight: 800,
              fontSize: 11,
              boxShadow: copilotOpen ? '0 0 15px rgba(56,189,248,0.5)' : 'none',
              transition: '0.2s'
            }}
          >
            <span>🎙️</span>
            <span>CRIMENET COPILOT</span>
          </button>
        </div>
      </div>

      {/* GLOBAL SPOTLIGHT SEARCH MODAL (Ctrl+K) */}
      {spotlightOpen && (
        <div onClick={() => setSpotlightOpen(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 4000, display: 'flex', alignItems: 'flex-start', justifyContent: 'center', paddingTop: '12vh' }}>
          <div onClick={e => e.stopPropagation()} style={{ width: '90vw', maxWidth: 600, background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 14, padding: 18, boxShadow: '0 25px 80px rgba(0,0,0,0.95)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, borderBottom: '1px solid #334155', paddingBottom: 10 }}>
              <span style={{ fontSize: 18 }}>🔍</span>
              <input
                autoFocus
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Type suspect name, phone number, vehicle plate, or case ID..."
                style={{ width: '100%', background: 'transparent', border: 'none', color: 'white', fontSize: 14, outline: 'none' }}
              />
              <span style={{ fontSize: 10, color: '#64748b' }}>ESC to close</span>
            </div>

            <div style={{ maxHeight: 300, overflowY: 'auto', marginTop: 10, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {searchResults.map(e => (
                <div
                  key={e.id}
                  onClick={() => {
                    if (onSelectEntity) onSelectEntity(e.name)
                    setSpotlightOpen(false)
                  }}
                  style={{ padding: '10px 12px', background: '#020617', borderRadius: 8, border: '1px solid #1e293b', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                >
                  <div>
                    <div style={{ fontWeight: 800, color: 'white', fontSize: 13 }}>{e.name}</div>
                    <div style={{ color: '#94a3b8', fontSize: 11 }}>{e.role} · {e.city || 'Mumbai'} · {e.phone || 'No MSISDN'}</div>
                  </div>
                  <span style={{ padding: '2px 8px', borderRadius: 4, background: 'rgba(56,189,248,0.2)', color: '#38bdf8', fontSize: 10, fontWeight: 800 }}>
                    SCORE: {e.risk_score || 50}
                  </span>
                </div>
              ))}
              {searchQuery && searchResults.length === 0 && (
                <div style={{ textAlign: 'center', color: '#64748b', padding: 24, fontSize: 12 }}>No matching records found in case database.</div>
              )}
              {!searchQuery && (
                <div style={{ color: '#64748b', fontSize: 11, padding: 8 }}>
                  💡 <b>Quick shortcuts:</b> Type <i>"Arjun"</i>, <i>"Rafiq"</i>, <i>"+91-9876543210"</i>, or <i>"c1"</i>.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
