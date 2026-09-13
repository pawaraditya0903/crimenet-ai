import React from 'react'
import { playCyberSound } from '../lib/audio'
import { getForensicMugshot } from '../lib/mugshot'

interface AuditLogsModalProps {
  isOpen: boolean
  onClose: () => void
  logs: any[]
  logFilter: string
  setLogFilter: (f: string) => void
  logSearchQuery: string
  setLogSearchQuery: (q: string) => void
  onSelectIntruder: (log: any) => void
  onDeleteLog: (log: any, e: React.MouseEvent) => void
  onClearAll: () => void
  soundEnabled: boolean
}

export const AuditLogsModal: React.FC<AuditLogsModalProps> = ({
  isOpen,
  onClose,
  logs,
  logFilter,
  setLogFilter,
  logSearchQuery,
  setLogSearchQuery,
  onSelectIntruder,
  onDeleteLog,
  onClearAll,
  soundEnabled
}) => {
  if (!isOpen) return null

  const filteredLogs = logs.filter((l: any) => {
    const matchesFilter =
      logFilter === 'ALL' ||
      (logFilter === 'BLOCKED' && l.status?.includes('BLOCKED')) ||
      (logFilter === 'AUTHORIZED' && l.status?.includes('AUTHORIZED'))
    const q = logSearchQuery.toLowerCase().trim()
    if (!q) return matchesFilter
    return (
      matchesFilter &&
      ((l.ip && l.ip.toLowerCase().includes(q)) ||
        (l.device && l.device.toLowerCase().includes(q)) ||
        (l.action && l.action.toLowerCase().includes(q)))
    )
  })

  const formatLogTimestamp = (log: any) => {
    if (log.timestamp && log.timestamp !== 'Invalid Date') return log.timestamp
    if (log.epoch) return new Date(log.epoch * 1000).toLocaleString('en-GB') + ' IST'
    return 'Just now'
  }

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.88)',
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
          maxWidth: 960,
          maxHeight: '85vh',
          background: '#0a101f',
          border: '1px solid #38bdf8',
          borderRadius: 16,
          padding: 24,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 0 50px rgba(56, 189, 248, 0.25)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 14 }}>
          <div>
            <h3 style={{ color: 'white', fontSize: 17, fontWeight: 900, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>🛡️</span> FORENSIC INTRUDER LOGS & BIOMETRIC TELEMETRY
            </h3>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
              Immutable audit chain · Tamper-evident incident capture
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
              style={{ background: '#334155', border: 'none', color: 'white', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 11 }}
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
            style={{ flex: 1, padding: '7px 12px', borderRadius: 6, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11.5, outline: 'none' }}
          />
          {(['ALL', 'BLOCKED', 'AUTHORIZED'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => {
                if (soundEnabled) playCyberSound('click')
                setLogFilter(filter)
              }}
              style={{
                padding: '6px 12px',
                borderRadius: 6,
                background: logFilter === filter ? '#0284c7' : '#1e293b',
                color: 'white',
                border: 'none',
                cursor: 'pointer',
                fontSize: 10.5,
                fontWeight: 700
              }}
            >
              {filter}
            </button>
          ))}
        </div>

        {/* Table */}
        <div style={{ flex: 1, overflowY: 'auto', marginTop: 14 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5 }}>
            <thead>
              <tr style={{ background: '#020617', color: '#38bdf8', textAlign: 'left' }}>
                <th style={{ padding: '10px' }}>Timestamp</th>
                <th style={{ padding: '10px' }}>IP Address</th>
                <th style={{ padding: '10px' }}>Device / Model</th>
                <th style={{ padding: '10px' }}>Status & Action</th>
                <th style={{ padding: '10px' }}>Intruder Mugshot</th>
                <th style={{ padding: '10px', textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: 24, color: '#64748b' }}>
                    No security events recorded.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log: any, idx: number) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #1e293b' }}>
                    <td style={{ padding: '10px', color: '#94a3b8', fontFamily: 'monospace' }}>{formatLogTimestamp(log)}</td>
                    <td style={{ padding: '10px', color: 'white', fontWeight: 700 }}>{log.ip}</td>
                    <td style={{ padding: '10px', color: '#cbd5e1' }}>{log.device}</td>
                    <td style={{ padding: '10px' }}>
                      <span
                        style={{
                          padding: '3px 8px',
                          borderRadius: 4,
                          background: log.status?.includes('AUTHORIZED') ? '#065f46' : '#7f1d1d',
                          color: 'white',
                          fontWeight: 800,
                          fontSize: 10
                        }}
                      >
                        {log.status}
                      </span>
                    </td>
                    <td style={{ padding: '10px' }}>
                      {(() => {
                        const mugshotSrc = log.photo || getForensicMugshot(log.badge, log.status, log.action, log.ip)
                        const isAuth = (log.status || '').includes('AUTHORIZED')
                        return (
                          <div
                            onClick={() => onSelectIntruder({ ...log, photo: mugshotSrc })}
                            style={{ display: 'inline-flex', alignItems: 'center', gap: 8, cursor: 'pointer', padding: '2px 4px', borderRadius: 8, background: 'rgba(255,255,255,0.03)' }}
                            title="Click to inspect full forensic biometric dossier"
                          >
                            <img
                              src={mugshotSrc}
                              alt="Subject Mugshot"
                              style={{
                                width: 42,
                                height: 42,
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
                    <td style={{ padding: '10px', textAlign: 'center' }}>
                      <button
                        onClick={(e) => onDeleteLog(log, e)}
                        title="Delete record"
                        style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#f87171', padding: '3px 7px', borderRadius: 4, cursor: 'pointer' }}
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
  const titleText = isAuth ? '🛡️ AUTHORIZED INVESTIGATOR DOSSIER' : '🚨 INTRUDER MUGSHOT & TELEMETRY'
  const borderColor = isAuth ? '#10b981' : '#ef4444'

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
          width: '90vw',
          maxWidth: 440,
          background: '#0f172a',
          border: `2px solid ${borderColor}`,
          borderRadius: 16,
          padding: 24,
          textAlign: 'center',
          boxShadow: `0 0 50px ${isAuth ? 'rgba(16,185,129,0.35)' : 'rgba(239,68,68,0.5)'}`
        }}
      >
        <h3 style={{ color: borderColor, fontSize: 16, fontWeight: 900 }}>{titleText}</h3>
        <div style={{ position: 'relative', width: 220, height: 220, margin: '14px auto' }}>
          <img
            src={photoSrc}
            alt="Subject Mugshot"
            style={{ width: '100%', height: '100%', borderRadius: 12, objectFit: 'cover', border: `2px solid ${borderColor}`, display: 'block' }}
          />
        </div>
        <div style={{ textAlign: 'left', background: '#020617', padding: 12, borderRadius: 8, fontSize: 11.5, color: '#cbd5e1', display: 'flex', flexDirection: 'column', gap: 6, border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#94a3b8' }}>Event Timestamp:</span>
            <b style={{ color: 'white', fontFamily: 'monospace' }}>{log.timestamp || 'Just now'}</b>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#94a3b8' }}>Source IP:</span>
            <b style={{ color: '#38bdf8', fontFamily: 'monospace' }}>{log.ip || '127.0.0.1'}</b>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#94a3b8' }}>Workstation / Agent:</span>
            <b style={{ color: '#e2e8f0' }}>{log.device || 'Workstation'}</b>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#94a3b8' }}>Action Flag:</span>
            <b style={{ color: borderColor }}>{log.action || 'SECURITY_EVENT'}</b>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#94a3b8' }}>Identified Subject:</span>
            <b style={{ color: isAuth ? '#34d399' : '#f87171' }}>{log.badge || (isAuth ? 'Aditya Pawar' : 'Unknown Intruder')}</b>
          </div>
        </div>
        <button
          onClick={onClose}
          style={{ width: '100%', padding: '10px', borderRadius: 8, background: borderColor, color: 'white', border: 'none', fontWeight: 800, marginTop: 14, cursor: 'pointer' }}
        >
          Close Incident Dossier
        </button>
      </div>
    </div>
  )
}
