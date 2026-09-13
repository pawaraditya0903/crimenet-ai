import React, { useState } from 'react'
import { getForensicMugshot } from '../lib/mugshot'
import { playCyberSound } from '../lib/audio'

interface IntruderLogsModalProps {
  isOpen?: boolean
  logs: any[]
  onClose: () => void
  onSelectIntruder: (log: any) => void
  onDeleteLog?: (log: any, e: React.MouseEvent) => void
  onClearAll?: () => void
  soundEnabled?: boolean
}

export const IntruderLogsModal: React.FC<IntruderLogsModalProps> = ({
  isOpen = false,
  logs,
  onClose,
  onSelectIntruder,
}) => {
  if (!isOpen) return null

  const formatLogTimestamp = (log: any): string => {
    if (!log) return 'Just now'
    if (log.epoch) {
      try {
        const d = new Date(log.epoch * 1000)
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/ /g, '-') + ' ' + d.toLocaleTimeString('en-GB', { hour12: false }) + ' IST'
      } catch {}
    }
    if (log.timestamp) {
      if (!log.timestamp.includes('IST') && log.timestamp !== 'Just now') {
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
          maxWidth: 960,
          maxHeight: '85vh',
          background: '#070d1e',
          border: '1.5px solid #0ea5e9',
          borderRadius: 16,
          padding: '24px 28px',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 0 50px rgba(0, 0, 0, 0.95), 0 0 35px rgba(14, 165, 233, 0.25)'
        }}
      >
        {/* Header matching exact user screenshot */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: 16 }}>
          <div>
            <h3 style={{ color: 'white', fontSize: 18, fontWeight: 900, display: 'flex', alignItems: 'center', gap: 10, letterSpacing: '0.04em', margin: 0 }}>
              <span style={{ fontSize: 20 }}>🛡️</span> LIVE INTRUDER & VISITOR ACCESS LOGS
            </h3>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>
              Real-time IP, device fingerprints & camera mugshots snapped by CrimeNet AI
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#cbd5e1',
              padding: '6px 16px',
              borderRadius: 8,
              cursor: 'pointer',
              fontSize: 12,
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}
          >
            ✕ Close
          </button>
        </div>

        {/* Table */}
        <div style={{ flex: 1, overflowY: 'auto', marginTop: 14 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ background: 'transparent', color: '#38bdf8', textAlign: 'left', borderBottom: '1px solid #1e293b' }}>
                <th style={{ padding: '12px 10px', fontWeight: 800 }}>Timestamp</th>
                <th style={{ padding: '12px 10px', fontWeight: 800 }}>IP Address</th>
                <th style={{ padding: '12px 10px', fontWeight: 800 }}>Device / Model</th>
                <th style={{ padding: '12px 10px', fontWeight: 800 }}>Action & Status</th>
                <th style={{ padding: '12px 10px', fontWeight: 800 }}>Intruder Mugshot</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: 32, color: '#64748b' }}>
                    No security events recorded.
                  </td>
                </tr>
              ) : (
                logs.map((log: any, idx: number) => {
                  const isAuth = (log.status || '').toUpperCase().includes('AUTHORIZED') || (log.action || '').toUpperCase().includes('AUTHORIZED')
                  const hasPhoto = !!log.photo
                  return (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '12px 10px', color: '#94a3b8', fontFamily: 'monospace', fontSize: 11.5 }}>
                        {formatLogTimestamp(log)}
                      </td>
                      <td style={{ padding: '12px 10px', color: 'white', fontWeight: 800, fontFamily: 'monospace', fontSize: 12 }}>
                        {log.ip || '127.0.0.1'}
                      </td>
                      <td style={{ padding: '12px 10px', color: '#94a3b8', maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 11.5 }} title={log.device}>
                        {log.device || 'Mozilla/5.0'}
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        <span
                          style={{
                            display: 'inline-block',
                            padding: '3px 10px',
                            borderRadius: 4,
                            fontSize: 10.5,
                            fontWeight: 900,
                            letterSpacing: '0.04em',
                            background: isAuth ? '#15803d' : '#991b1b',
                            color: '#ffffff'
                          }}
                        >
                          {isAuth ? 'AUTHORIZED' : 'BLOCKED_INTRUDER'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        {hasPhoto ? (
                          <div
                            onClick={() => onSelectIntruder(log)}
                            style={{ cursor: 'pointer', display: 'inline-block' }}
                            title="Click to inspect full forensic biometric dossier"
                          >
                            <img
                              src={log.photo}
                              alt="Mugshot"
                              style={{
                                width: 44,
                                height: 44,
                                borderRadius: 8,
                                objectFit: 'cover',
                                border: '2px solid #ef4444',
                                boxShadow: '0 0 10px rgba(239, 68, 68, 0.7)',
                                display: 'block'
                              }}
                            />
                          </div>
                        ) : (
                          <span style={{ color: '#64748b', fontSize: 11.5 }}>No Photo</span>
                        )}
                      </td>
                    </tr>
                  )
                })
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
