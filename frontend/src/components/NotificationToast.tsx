import React, { useEffect, useState } from 'react'

export interface ToastEvent {
  id: string
  title: string
  details: string
  severity: 'info' | 'warning' | 'critical'
  timestamp: string
}

interface NotificationToastProps {
  toast: ToastEvent | null
  onDismiss: () => void
}

export default function NotificationToast({ toast, onDismiss }: NotificationToastProps) {
  useEffect(() => {
    if (!toast) return
    const timer = setTimeout(() => {
      onDismiss()
    }, 4500)
    return () => clearTimeout(timer)
  }, [toast, onDismiss])

  if (!toast) return null

  const getBorderColor = () => {
    if (toast.severity === 'critical') return '#ef4444'
    if (toast.severity === 'warning') return '#f59e0b'
    return '#38bdf8'
  }

  const getBgColor = () => {
    if (toast.severity === 'critical') return 'rgba(239, 68, 68, 0.15)'
    if (toast.severity === 'warning') return 'rgba(245, 158, 11, 0.15)'
    return 'rgba(56, 189, 248, 0.15)'
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: 24,
      right: 24,
      width: 340,
      background: '#0f172a',
      border: `1px solid ${getBorderColor()}`,
      borderRadius: 10,
      padding: '12px 16px',
      boxShadow: '0 20px 60px rgba(0,0,0,0.9)',
      zIndex: 5000,
      display: 'flex',
      alignItems: 'flex-start',
      gap: 12,
      animation: 'slideIn 0.3s ease-out',
      color: '#f8fafc',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        width: 32,
        height: 32,
        borderRadius: '50%',
        background: getBgColor(),
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 16,
        flexShrink: 0
      }}>
        {toast.severity === 'critical' ? '🚨' : toast.severity === 'warning' ? '⚠️' : 'ℹ️'}
      </div>

      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: getBorderColor() }}>
          {toast.title}
        </div>
        <div style={{ fontSize: 11, color: '#cbd5e1', marginTop: 2, lineHeight: 1.4 }}>
          {toast.details}
        </div>
        <div style={{ fontSize: 9.5, color: '#64748b', marginTop: 4 }}>
          {toast.timestamp}
        </div>
      </div>

      <button
        onClick={onDismiss}
        style={{
          background: 'transparent',
          border: 'none',
          color: '#94a3b8',
          fontSize: 14,
          cursor: 'pointer'
        }}
      >
        ✕
      </button>
    </div>
  )
}
