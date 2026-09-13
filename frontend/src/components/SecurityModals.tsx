import React, { useState } from 'react'
import { getForensicMugshot } from '../lib/mugshot'
import { playCyberSound } from '../lib/audio'

interface IntruderLogsModalProps {
  logs: any[]
  onClose: () => void
  onDeleteLog: (log: any, e: React.MouseEvent) => void
  onClearAll: () => void
  onSelectIntruder: (log: any) => void
  soundEnabled: boolean
}

export const IntruderLogsModal: React.FC<IntruderLogsModalProps> = ({
  logs,
  onClose,
  onDeleteLog,
  onClearAll,
  onSelectIntruder,
  soundEnabled
}) => {
  const [logSearchQuery, setLogSearchQuery] = useState('')
  const [logFilter, setLogFilter] = useState<'ALL' | 'BLOCKED' | 'AUTHORIZED'>('ALL')

  const filteredLogs = logs.filter((l) => {
    const s = (l.status || '').toUpperCase()
    if (logFilter === 'BLOCKED' && !s.includes('BLOCK') && !s.includes('FAIL') && !s.includes('PROBE')) return false
    if (logFilter === 'AUTHORIZED' && !s.includes('AUTH') && !s.includes('VERIFIED')) return false
    if (!logSearchQuery) return true
    const q = logSearchQuery.toLowerCase()
    return (
      (l.ip && l.ip.toLowerCase().includes(q)) ||
      (l.device && l.device.toLowerCase().includes(q)) ||
      (l.action && l.action.toLowerCase().includes(q)) ||
      (l.badge && l.badge.toLowerCase().includes(q))
    )
  })

  const formatLogTimestamp = (log: any): string => {
    if (!log) return 'Just now'
    if (log.epoch) {
      try {
        const d = new Date(log.epoch * 1000)
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-') + ' ' + d.toLocaleTimeString('en-GB', { hour12: false }) + ' IST'
      } catch {}
    }
    if (log.timestamp) {
      if (!log.timestamp.includes('IST')) {
        return `${log.timestamp} IST`
      }
      return log.timestamp
    }
    return 'Just now'
  }

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.85)',
        zIndex: 3500,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '95vw',
          maxWidth: 980,
          maxHeight: '85vh',
          background: '#090e1a',
          border: '1px solid rgba(56, 189, 248, 0.4)',
          borderRadius: 20,
          padding: 24,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 0 50px rgba(0, 0, 0, 0.9), 0 0 30px rgba(56, 189, 248, 0.15)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 14 }}>
          <div>
            <h3 style={{ color: 'white', fontSize: 17, fontWeight: 900, display: 'flex', alignItems: 'center', gap: 8, letterSpacing: '0.04em' }}>
              <span>🛡️</span> LIVE INTRUDER & VISITOR ACCESS LOGS
            </h3>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 3 }}>
              Immutable forensic audit trail · Real-time biometric capture & IP telemetry
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={onClearAll}
              style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#f87171', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 11, fontWeight: 700 }}
            >
              Clear Records
            </button>
            <button
              onClick={onClose}
              style={{ background: '#334155', border: 'none', color: 'white', padding: '6px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 11.5, fontWeight: 700 }}
            >
              ✕ Close
            </button>
          </div>
        </div>

        {/* Filter controls */}
        <div style={{ display: 'flex', gap: 10, marginTop: 14, alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Filter by IP, device, action..."
            value={logSearchQuery}
            onChange={(e) => setLogSearchQuery(e.target.value)}
            style={{ flex: 1, padding: '8px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11.5, outline: 'none' }}
          />
          {(
            [
              { id: 'ALL', label: 'All Records' },
              { id: 'BLOCKED', label: '🚨 Blocked Intruders' },
              { id: 'AUTHORIZED', label: '✓ Authorized Access' }
            ] as const
          ).map((filter) => (
            <button
              key={filter.id}
              onClick={() => {
                if (soundEnabled) playCyberSound('click')
                setLogFilter(filter.id)
              }}
              style={{
                padding: '7px 14px',
                borderRadius: 8,
                background: logFilter === filter.id ? '#0284c7' : '#1e293b',
                color: 'white',
                border: logFilter === filter.id ? '1px solid #38bdf8' : '1px solid transparent',
                cursor: 'pointer',
                fontSize: 11,
                fontWeight: 700
              }}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* Table */}
        <div style={{ flex: 1, overflowY: 'auto', marginTop: 14 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5 }}>
            <thead>
              <tr style={{ background: '#020617', color: '#38bdf8', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px' }}>Timestamp</th>
                <th style={{ padding: '10px 12px' }}>IP Address</th>
                <th style={{ padding: '10px 12px' }}>Device / Model</th>
                <th style={{ padding: '10px 12px' }}>Status & Action</th>
                <th style={{ padding: '10px 12px' }}>Intruder Mugshot</th>
                <th style={{ padding: '10px 12px', textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: 28, color: '#64748b' }}>
                    No security events recorded.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log: any, idx: number) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '10px 12px', color: '#94a3b8', fontFamily: 'monospace' }}>{formatLogTimestamp(log)}</td>
                    <td style={{ padding: '10px 12px', color: 'white', fontWeight: 800, fontFamily: 'monospace' }}>{log.ip}</td>
                    <td style={{ padding: '10px 12px', color: '#cbd5e1', maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={log.device}>{log.device}</td>
                    <td style={{ padding: '10px 12px' }}>
                      <span
                        style={{
                          padding: '3px 8px',
                          borderRadius: 4,
                          background: log.status?.includes('AUTHORIZED') ? '#065f46' : log.status?.includes('MONITORED') ? '#1e3a8a' : '#7f1d1d',
                          color: log.status?.includes('AUTHORIZED') ? '#6ee7b7' : log.status?.includes('MONITORED') ? '#93c5fd' : '#fca5a5',
                          fontWeight: 800,
                          fontSize: 10
                        }}
                      >
                        {log.status?.includes('AUTHORIZED') ? 'AUTHORIZED_OFFICER' : log.status?.includes('MONITORED') ? 'VISITOR_LOGGED' : 'BLOCKED_INTRUDER'}
                      </span>
                    </td>
                    <td style={{ padding: '10px 12px' }}>
                      {(() => {
                        const mugshotSrc = log.photo || getForensicMugshot(log.badge, log.status, log.action, log.ip)
                        const isAuth = (log.status || '').includes('AUTHORIZED')
                        return (
                          <div
                            onClick={() => onSelectIntruder({ ...log, photo: mugshotSrc })}
                            style={{ display: 'inline-flex', alignItems: 'center', gap: 8, cursor: 'pointer', padding: '3px 6px', borderRadius: 8, background: 'rgba(255,255,255,0.03)' }}
                            title="Click to inspect full forensic biometric dossier"
                          >
                            <img
                              src={mugshotSrc}
                              alt="Subject Mugshot"
                              style={{
                                width: 44,
                                height: 44,
                                borderRadius: 6,
                                objectFit: 'cover',
                                border: isAuth ? '2px solid #10b981' : '2px solid #ef4444',
                                boxShadow: isAuth ? '0 0 10px rgba(16,185,129,0.35)' : '0 0 10px rgba(239,68,68,0.45)',
                                display: 'block'
                              }}
                            />
                            <span style={{ fontSize: 9.5, color: isAuth ? '#34d399' : '#f87171', fontWeight: 800 }}>
                              {isAuth ? 'VERIFIED' : 'CAPTURED'}
                            </span>
                          </div>
                        )
                      })()}
                    </td>
                    <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                      <button
                        onClick={(e) => onDeleteLog(log, e)}
                        title="Delete record"
                        style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#f87171', padding: '4px 8px', borderRadius: 4, cursor: 'pointer' }}
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

interface IntruderModalProps {
  log: any | null
  onClose: () => void
}

export const IntruderModal: React.FC<IntruderModalProps> = ({ log, onClose }) => {
  if (!log) return null
  const photoSrc = log.photo || getForensicMugshot(log.badge, log.status, log.action, log.ip)
  const isAuth = (log.status || '').includes('AUTHORIZED')
  const titleText = isAuth ? '🛡️ AUTHORIZED INVESTIGATOR DOSSIER' : '🚨 INTRUDER MUGSHOT CAPTURED'
  const accentColor = isAuth ? '#10b981' : '#ff4d4d'

  // Format timestamp e.g. "23-Aug-2026 13:11:02 IST"
  let formattedTime = log.timestamp || 'Just now'
  if (log.epoch) {
    try {
      const d = new Date(log.epoch * 1000)
      formattedTime = d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-') + ' ' + d.toLocaleTimeString('en-GB', { hour12: false }) + ' IST'
    } catch {}
  } else if (!formattedTime.includes('IST') && formattedTime !== 'Just now') {
    formattedTime = `${formattedTime} IST`
  }

  const actionText = log.action || (isAuth ? 'AUTHORIZED_ACCESS' : 'INTRUDER_FACE_FAILED_0%')

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.92)',
        zIndex: 4000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '92vw',
          maxWidth: 460,
          background: '#0a0f1d',
          border: `2px solid ${accentColor}`,
          borderRadius: 22,
          padding: '24px 26px',
          textAlign: 'center',
          boxShadow: isAuth ? '0 0 60px rgba(16,185,129,0.35)' : '0 0 60px rgba(255, 77, 77, 0.45)'
        }}
      >
        {/* Modal Title matching Sample */}
        <h3 style={{ color: accentColor, fontSize: 17, fontWeight: 900, letterSpacing: '0.04em', margin: '0 0 16px 0', textTransform: 'uppercase' }}>
          {titleText}
        </h3>

        {/* Rounded Mugshot Photo Container with outer glow */}
        <div style={{ position: 'relative', width: 250, height: 250, margin: '0 auto 16px', borderRadius: 16, overflow: 'hidden', border: `2px solid ${accentColor}`, boxShadow: `0 0 25px ${isAuth ? 'rgba(16,185,129,0.45)' : 'rgba(255, 77, 77, 0.5)'}` }}>
          <img
            src={photoSrc}
            alt="Subject Mugshot"
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
          />
        </div>

        {/* Structured Telemetry Details Box matching Sample Screenshot */}
        <div style={{
          textAlign: 'left',
          background: '#050814',
          padding: '14px 18px',
          borderRadius: 12,
          fontSize: 12,
          color: '#cbd5e1',
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          border: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          <div style={{ display: 'flex', gap: 6 }}>
            <b style={{ color: 'white', minWidth: 60 }}>Time:</b>
            <span style={{ color: '#f8fafc' }}>{formattedTime}</span>
          </div>

          <div style={{ display: 'flex', gap: 6 }}>
            <b style={{ color: 'white', minWidth: 60 }}>IP:</b>
            <span style={{ color: '#38bdf8', fontWeight: 800, fontFamily: 'monospace' }}>{log.ip || '127.0.0.1'}</span>
          </div>

          <div style={{ display: 'flex', gap: 6 }}>
            <b style={{ color: 'white', minWidth: 60 }}>Device:</b>
            <span style={{ color: '#cbd5e1', wordBreak: 'break-all' }}>{log.device || 'Workstation'}</span>
          </div>

          <div style={{ display: 'flex', gap: 6 }}>
            <b style={{ color: 'white', minWidth: 60 }}>Action:</b>
            <span style={{ color: accentColor, fontWeight: 800 }}>{actionText}</span>
          </div>
        </div>

        {/* Action Button matching Sample */}
        <button
          onClick={onClose}
          style={{
            width: '100%',
            padding: '12px',
            borderRadius: 10,
            background: isAuth ? '#10b981' : '#ff4747',
            color: 'white',
            border: 'none',
            fontWeight: 800,
            fontSize: 14.5,
            marginTop: 16,
            cursor: 'pointer',
            boxShadow: isAuth ? '0 4px 20px rgba(16,185,129,0.3)' : '0 4px 20px rgba(255, 71, 71, 0.4)',
            transition: '0.2s'
          }}
        >
          Close Intruder Dossier
        </button>
      </div>
    </div>
  )
}

export const AuditLogsModal = IntruderLogsModal
export default IntruderLogsModal
