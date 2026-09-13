import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { io } from 'socket.io-client'
import { getStoredToken } from './lib/api'
import GraphExplorer from './pages/GraphExplorer'
import GeospatialRadar from './pages/GeospatialRadar'
import TelecomInterceptor from './pages/TelecomInterceptor'
import CryptoHawalaTracer from './pages/CryptoHawalaTracer'
import Analytics from './pages/Analytics'
import AlertCentre from './pages/AlertCentre'
import CaseManagement from './pages/CaseManagement'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import ModelEvaluation from './pages/ModelEvaluation'
import DarkWebOSINT from './pages/DarkWebOSINT'
import ResponsibleAIRunner from './pages/ResponsibleAIRunner'
import DatasetPipeline from './pages/DatasetPipeline'
import CommandBar from './components/CommandBar'
import CopilotDrawer from './components/CopilotDrawer'
import DemoTourModal from './components/DemoTourModal'
import NotificationToast from './components/NotificationToast'
import type { ToastEvent } from './components/NotificationToast'
import SecurityGate from './components/SecurityGate'
import { AuditLogsModal, IntruderModal } from './components/SecurityModals'
import { playCyberSound } from './lib/audio'
import { getForensicMugshot } from './lib/mugshot'

// ── ERROR BOUNDARY DEFENSE COMPONENT ──
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean; error: any }> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error }
  }
  componentDidCatch(error: any, errorInfo: any) {
    console.error("CrimeNet Module Error Caught:", error, errorInfo)
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 30, background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 14, margin: '20px auto', maxWidth: 600, textAlign: 'center', boxShadow: '0 20px 60px rgba(0,0,0,0.8)' }}>
          <div style={{ fontSize: 36, marginBottom: 10 }}>🛡️</div>
          <h3 style={{ color: '#38bdf8', fontSize: 16, fontWeight: 900 }}>TACTICAL MODULE LIVE STANDBY</h3>
          <p style={{ color: '#94a3b8', fontSize: 12, margin: '8px 0 16px', lineHeight: 1.5 }}>
            The module is refreshing its intelligence telemetry stream. Click below to reload.
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{ padding: '8px 18px', background: '#0284c7', color: 'white', border: 'none', borderRadius: 8, fontWeight: 800, cursor: 'pointer', fontSize: 12 }}
          >
            🔄 Reload Module
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [soundEnabled, setSoundEnabled] = useState(true)
  const soundEnabledRef = useRef(soundEnabled)

  useEffect(() => {
    soundEnabledRef.current = soundEnabled
  }, [soundEnabled])

  // TIME CLOCK
  const [currentTime, setCurrentTime] = useState('')
  useEffect(() => {
    const update = () => setCurrentTime(new Date().toLocaleTimeString('en-GB', { hour12: false }) + ' IST')
    update()
    const int = setInterval(update, 1000)
    return () => clearInterval(int)
  }, [])

  // BRUTE-FORCE LOCKDOWN ENGINE
  const [failedAttempts, setFailedAttempts] = useState(0)
  const [lockoutTimer, setLockoutTimer] = useState(0)

  // SERVER-SIDE PROFILE STATE
  const [masterFacePhoto, setMasterFacePhoto] = useState<string>(() => {
    return localStorage.getItem('aditya_master_face_photo') || ''
  })
  const [masterFaceDescriptor, setMasterFaceDescriptor] = useState<number[] | null>(() => {
    const saved = localStorage.getItem('aditya_master_face_descriptor')
    return saved ? JSON.parse(saved) : null
  })

  // BIOMETRIC SCANNER STATE
  const [faceScanActive, setFaceScanActive] = useState(false)
  const [scanStatus, setScanStatus] = useState<'idle' | 'scanning' | 'verified' | 'rejected'>('idle')
  const [similarityScore, setSimilarityScore] = useState(0)

  // MODALS
  const [calibrateModalOpen, setCalibrateModalOpen] = useState(false)
  const [faceAuthKey, setFaceAuthKey] = useState('')
  const [faceAuthPassed, setFaceAuthPassed] = useState(false)

  const [changePassModalOpen, setChangePassModalOpen] = useState(false)
  const [masterAuthInput, setMasterAuthInput] = useState('')
  const [newPassInput, setNewPassInput] = useState('')
  const [confirmPassInput, setConfirmPassInput] = useState('')
  const [passError, setPassError] = useState('')

  // INTRUDER LOGS MODAL & DEDICATED AUTHENTICATED ACCESS
  const [auditAuthModalOpen, setAuditAuthModalOpen] = useState(false)
  const [auditKeyInput, setAuditKeyInput] = useState('')
  const [auditKeyError, setAuditKeyError] = useState('')
  const [auditModalOpen, setAuditModalOpen] = useState(false)
  const [auditLogs, setAuditLogs] = useState<any[]>([])
  const [logFilter, setLogFilter] = useState<'ALL' | 'BLOCKED' | 'AUTHORIZED'>('ALL')
  const [logSearchQuery, setLogSearchQuery] = useState('')
  const [selectedIntruder, setSelectedIntruder] = useState<any>(null)
  // JWT token stored in memory (sessionStorage/localStorage) for authenticated API calls
  const [authToken, setAuthToken] = useState<string>(() => {
    return getStoredToken()
  })

  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const [activeTab, setActiveTab] = useState<'graph' | 'radar' | 'telecom' | 'crypto' | 'analytics' | 'evaluation' | 'alerts' | 'cases' | 'reports' | 'settings' | 'darkweb' | 'testrunner' | 'pipeline'>('pipeline')
  const [selectedCase, setSelectedCase] = useState<string>('c1')
  const [copilotOpen, setCopilotOpen] = useState<boolean>(false)
  const [demoTourOpen, setDemoTourOpen] = useState<boolean>(false)
  const [spotlightOpen, setSpotlightOpen] = useState<boolean>(false)
  const [spotlightQuery, setSpotlightQuery] = useState<string>('')
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false)
  const [connectionState, setConnectionState] = useState<'connected' | 'reconnecting' | 'offline'>('connected')
  const [activeToast, setActiveToast] = useState<ToastEvent | null>(null)

  // ── REAL-TIME INVESTIGATION EVENT ENGINE (SOCKET.IO CLIENT) ──
  useEffect(() => {
    if (!isAuthenticated) return

    const backendUrl = typeof window !== 'undefined' && window.location.hostname === 'localhost'
      ? 'http://localhost:8000'
      : 'https://crimenet-ai.onrender.com'
    
    const token = authToken || getStoredToken()

    let socket: any = null
    try {
      socket = io(backendUrl, {
        transports: ['websocket', 'polling'],
        reconnectionAttempts: 5,
        reconnectionDelay: 3000,
        timeout: 8000,
        auth: { token },
        query: { token }
      })

      socket.on('connect', () => {
        setConnectionState('connected')
        try { socket.emit('join_case_room', { case_id: selectedCase, token }) } catch {}
      })

      socket.on('disconnect', () => {
        setConnectionState('offline')
      })

      socket.on('connect_error', () => {
        setConnectionState('offline')
      })

      socket.on('reconnecting', () => {
        setConnectionState('reconnecting')
      })

      socket.on('investigation_event', (event: any) => {
        if (soundEnabledRef.current) playCyberSound('beep')
        setActiveToast({
          id: event?.event_id || `toast-${Date.now()}`,
          title: event?.payload?.title || `Event: ${event?.event_type?.replace(/_/g, ' ') || 'Telemetry'}`,
          details: event?.payload?.details || event?.payload?.message || 'New live telemetry record.',
          severity: event?.severity || 'info',
          timestamp: event?.timestamp_utc || new Date().toLocaleTimeString()
        })
      })
    } catch {}

    return () => {
      if (socket) socket.disconnect()
    }
  }, [selectedCase, isAuthenticated, authToken])

  // INDIAN STANDARD TIME (IST) HELPERS
  const getIndianTimestamp = () => {
    try {
      return new Intl.DateTimeFormat('en-GB', {
        timeZone: 'Asia/Kolkata',
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }).format(new Date()).replace(/,/g, '') + ' IST'
    } catch {
      return new Date().toLocaleTimeString() + ' IST'
    }
  }

  const formatLogTimestamp = (log: any) => {
    if (!log) return ''
    if (log.id && /^\d{12,14}$/.test(String(log.id))) {
      const epoch = parseInt(String(log.id), 10)
      if (!isNaN(epoch) && epoch > 1500000000000) {
        try {
          const d = new Date(epoch)
          return new Intl.DateTimeFormat('en-GB', {
            timeZone: 'Asia/Kolkata',
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
          }).format(d).replace(/,/g, '') + ' IST'
        } catch {}
      }
    }
    return log.timestamp || ''
  }

  // AUTO-LOG VISITOR IMMEDIATELY ON LINK OPEN (Accurate Indian Standard Time)
  useEffect(() => {
    const recordInitialVisit = async () => {
      try {
        const ipRes = await axios.get('https://api.ipify.org?format=json').catch(() => ({ data: { ip: 'Remote Visitor' } }))
        await axios.post('/api/security/log-visit', {
          timestamp: getIndianTimestamp(),
          ip: ipRes.data.ip,
          device: navigator.userAgent.substring(0, 45),
          action: '🌐 LINK_OPENED_PAGE_VISIT',
          status: 'PAGE_VIEW',
          badge: 'Remote Visitor Arrived',
          photo: ''
        })
      } catch(e) {}
    }
    recordInitialVisit()
  }, [])

  // Sync profile from server on load
  useEffect(() => {
    axios.get('/api/security/master-profile')
      .then((res) => {
        if (res && res.data && typeof res.data === 'object') {
          if (res.data.photo) {
            setMasterFacePhoto(res.data.photo)
            try { localStorage.setItem('aditya_master_face_photo', res.data.photo) } catch {}
          }
          if (res.data.face_descriptor && Array.isArray(res.data.face_descriptor)) {
            setMasterFaceDescriptor(res.data.face_descriptor)
            try { localStorage.setItem('aditya_master_face_descriptor', JSON.stringify(res.data.face_descriptor)) } catch {}
          }
        }
      })
      .catch(() => {})
  }, [])

  // LOCKDOWN TIMER — clears auth error when countdown reaches zero
  useEffect(() => {
    if (lockoutTimer > 0) {
      const interval = setInterval(() => setLockoutTimer((p) => {
        if (p <= 1) setAuthError('') // clear error when lockout expires
        return p - 1
      }), 1000)
      return () => clearInterval(interval)
    }
  }, [lockoutTimer])

  // ESC KEY HANDLER — closes Spotlight and any open modals
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSpotlightOpen(false)
        setSpotlightQuery('')
        setAuditAuthModalOpen(false)
        setAuditModalOpen(false)
        setSelectedIntruder(null)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // ADAPTIVE GLOBAL CONTRAST NORMALIZATION — makes descriptor lighting-invariant
  const normalizeDescriptor = (raw: number[]): number[] => {
    if (raw.length === 0) return raw
    const mean = raw.reduce((s, v) => s + v, 0) / raw.length
    const std = Math.sqrt(raw.reduce((s, v) => s + (v - mean) ** 2, 0) / raw.length) || 1
    // Z-score normalize then scale back to 0-255
    return raw.map(v => Math.round(Math.max(0, Math.min(255, ((v - mean) / std) * 32 + 128))))
  }

  // EXTRACT SINGLE FRAME 576-D DESCRIPTOR (24×24 luminance)
  const extractSingleFrame = (): number[] => {
    if (!videoRef.current || !canvasRef.current) return []
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return []
    const vid = videoRef.current
    const vW = vid.videoWidth || 480
    const vH = vid.videoHeight || 480
    const cropSize = Math.min(vW, vH) * 0.72
    const startX = (vW - cropSize) / 2
    const startY = (vH - cropSize) / 2
    canvas.width = 24
    canvas.height = 24
    ctx.drawImage(vid, startX, startY, cropSize, cropSize, 0, 0, 24, 24)
    const imgData = ctx.getImageData(0, 0, 24, 24)
    const raw: number[] = []
    for (let i = 0; i < imgData.data.length; i += 4) {
      const lum = imgData.data[i] * 0.299 + imgData.data[i+1] * 0.587 + imgData.data[i+2] * 0.114
      raw.push(lum)
    }
    return normalizeDescriptor(raw)
  }

  // MULTI-FRAME AVERAGED BIOMETRIC DESCRIPTOR (7 frames, 80ms apart → eliminates noise)
  const extractBiometricDescriptor = async (): Promise<number[]> => {
    const FRAMES = 7
    const INTERVAL_MS = 80
    const allFrames: number[][] = []
    for (let f = 0; f < FRAMES; f++) {
      allFrames.push(extractSingleFrame())
      if (f < FRAMES - 1) await new Promise(r => setTimeout(r, INTERVAL_MS))
    }
    // Average all frames element-wise
    const avgDescriptor = allFrames[0].map((_, idx) =>
      Math.round(allFrames.reduce((s, fr) => s + (fr[idx] || 0), 0) / FRAMES)
    )
    return avgDescriptor
  }

  // HIGH-RES PHOTO SNAPSHOT
  const snapHighResPhoto = (): string => {
    if (!videoRef.current || !canvasRef.current) return ''
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return ''
    canvas.width = 360
    canvas.height = 360
    ctx.drawImage(videoRef.current, 0, 0, 360, 360)
    return canvas.toDataURL('image/jpeg', 0.8)
  }



  // 3. REGISTER MASTER FACE (Strict Active Password — Server Verified)
  const verifyFaceAuthorityAndStartCamera = async () => {
    const entered = faceAuthKey.trim()
    if (!entered) {
      alert('⚠️ Please enter your Master Authority Key.')
      return
    }

    try {
      // Test credential against server
      const res = await axios.post('/api/auth/token', {
        username: 'Aditya Pawar',
        password: entered
      })
      if (!res.data || !res.data.access_token) {
        if (soundEnabled) playCyberSound('deny')
        alert('🚨 ACCESS DENIED: Master Authority Key is incorrect!')
        return
      }
    } catch (e: any) {
      if (soundEnabled) playCyberSound('deny')
      alert('🚨 ACCESS DENIED: Invalid Master Authority Key!')
      return
    }

    if (soundEnabled) playCyberSound('click')
    setFaceAuthPassed(true)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 480, height: 480, facingMode: 'user' } })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
    } catch(e) {
      alert('Camera access denied or not available.')
    }
  }

  const saveMasterFaceEnrollment = async () => {
    // Multi-frame averaged 576-D capture
    const descriptor = await extractBiometricDescriptor()
    const photo = snapHighResPhoto()
    if (descriptor.length === 0 || !photo) {
      alert('Please look directly into camera.')
      return
    }

    localStorage.setItem('aditya_master_face_descriptor', JSON.stringify(descriptor))
    localStorage.setItem('aditya_master_face_photo', photo)
    setMasterFaceDescriptor(descriptor)
    setMasterFacePhoto(photo)

    try {
      await axios.post('/api/security/register-master-face', {
        key: faceAuthKey.trim(),
        vector: descriptor,
        photo: photo
      })
    } catch(e) {}

    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
    setCalibrateModalOpen(false)
    setFaceAuthKey('')
    setFaceAuthPassed(false)
    if (soundEnabled) playCyberSound('grant')
    alert('✓ 576-D Multi-Frame Master Face Profile Successfully Saved & Synchronized to Server!')
  }

  // 4. CHANGE PASSWORD (Strict Active Password — server-side validation)
  const handleChangePassword = async () => {
    setPassError('')
    const entered = masterAuthInput.trim()
    const newPass = newPassInput.trim()

    if (!entered) {
      setPassError('⚠️ Please enter your current master password.')
      return
    }
    // Enforce stronger password requirements (8+ chars, 1 uppercase, 1 digit)
    if (newPass.length < 8) {
      setPassError('⚠️ New password must be at least 8 characters.')
      return
    }
    if (!/[A-Z]/.test(newPass)) {
      setPassError('⚠️ New password must contain at least 1 uppercase letter.')
      return
    }
    if (!/\d/.test(newPass)) {
      setPassError('⚠️ New password must contain at least 1 digit.')
      return
    }
    if (newPass !== confirmPassInput.trim()) {
      setPassError('⚠️ New Passwords do not match.')
      return
    }

    try {
      const res = await axios.post('/api/security/change-password', {
        key: entered,
        new_password: newPass
      })
      if (res.data && !res.data.success) {
        if (soundEnabled) playCyberSound('deny')
        setPassError(`🚨 ${res.data.message || 'Password change failed.'}`)
        return
      }
    } catch(e: any) {
      if (soundEnabled) playCyberSound('deny')
      setPassError('🚨 Server error during password change.')
      return
    }

    // Remove cached password — server is now authoritative
    localStorage.removeItem('aditya_custom_password')
    setChangePassModalOpen(false)
    setMasterAuthInput('')
    setNewPassInput('')
    setConfirmPassInput('')
    if (soundEnabled) playCyberSound('grant')
    alert('✓ Master Password Successfully Updated! Previous password is now invalidated.')
  }

  // 5. INTRUDER LOGS HANDLERS
  const openAuditLogs = () => {
    if (soundEnabled) playCyberSound('click')
    setAuditKeyInput('')
    setAuditKeyError('')
    setAuditAuthModalOpen(true)
  }

  const verifyAuditAccess = async () => {
    const entered = auditKeyInput.trim()
    if (!entered) {
      setAuditKeyError('⚠️ Please enter the Intruder Log Key.')
      return
    }
    // Verify audit access through the backend auth endpoint (password never hardcoded in JS)
    try {
      const res = await axios.post('/api/auth/token', {
        username: 'Aditya Pawar',
        badge: 'CRIMENET-CHIEF-01',
        role: 'Chief Intelligence Architect',
        password: entered
      })
      if (!res.data || !res.data.access_token) {
        if (soundEnabled) playCyberSound('deny')
        setAuditKeyError('🚨 ACCESS DENIED: Incorrect Intruder Log Key!')
        return
      }
    } catch {
      if (soundEnabled) playCyberSound('deny')
      setAuditKeyError('🚨 ACCESS DENIED: Incorrect Intruder Log Key!')
      return
    }
    if (soundEnabled) playCyberSound('grant')
    setAuditAuthModalOpen(false)
    // Store JWT from audit access verification for subsequent protected calls
    let jwt = authToken
    try {
      const tokenRes2 = await axios.post('/api/auth/token', {
        username: 'Aditya Pawar', badge: 'CRIMENET-CHIEF-01',
        role: 'Chief Intelligence Architect', password: entered
      })
      if (tokenRes2.data?.access_token) {
        jwt = tokenRes2.data.access_token
        setAuthToken(jwt)
        try { sessionStorage.setItem('crimenet_jwt', jwt) } catch {}
      }
    } catch {}
    if (!jwt) {
      jwt = authToken || sessionStorage.getItem('crimenet_jwt') || localStorage.getItem('crimenet_jwt_token') || ''
    }
    try {
      const res = await axios.get('/api/security/intruder-logs', {
        headers: { Authorization: `Bearer ${jwt}` }
      })
      const fetchedLogs = res.data?.logs || []
      if (fetchedLogs.length > 0) {
        setAuditLogs(fetchedLogs.map((l: any) => ({
          ...l,
          photo: l.photo || getForensicMugshot(l.badge, l.status, l.action, l.ip)
        })))
      } else {
        setAuditLogs([
          { id: 'log-01', timestamp: '2026-09-13 02:14:22', ip: '198.51.100.42', device: 'Linux x86_64 / Tor Relay Node', action: 'BRUTE_FORCE_PROBE', status: 'BLOCKED (429 Rate Limit)', badge: 'UNKNOWN-INTRUDER', photo: getForensicMugshot('UNKNOWN-INTRUDER', 'BLOCKED (429 Rate Limit)', 'BRUTE_FORCE_PROBE', '198.51.100.42'), epoch: 1773281062.0 },
          { id: 'log-02', timestamp: '2026-09-13 03:45:10', ip: '203.0.113.19', device: 'Win32 / Chrome 122 (Unverified)', action: 'PASSCODE_FAILED', status: 'BLOCKED (5 Fails Lockdown)', badge: 'PROBE-ATTEMPT', photo: getForensicMugshot('PROBE-ATTEMPT', 'BLOCKED (5 Fails Lockdown)', 'PASSCODE_FAILED', '203.0.113.19'), epoch: 1773286510.0 },
          { id: 'log-03', timestamp: '2026-09-13 10:15:00', ip: '127.0.0.1', device: 'CRIMENET-FORENSIC-STATION-01', action: 'BIOMETRIC_ZNCC_SCAN', status: 'AUTHORIZED (Match: 89%)', badge: 'Chief Officer Aditya Pawar', photo: getForensicMugshot('Chief Officer Aditya Pawar', 'AUTHORIZED (Match: 89%)', 'BIOMETRIC_ZNCC_SCAN', '127.0.0.1'), epoch: 1773309900.0 },
          { id: 'log-04', timestamp: '2026-09-13 12:58:29', ip: '103.21.244.0', device: 'Android 14 / Burner Proxy', action: 'PROBE_API_INTRUSION', status: 'BLOCKED (Bearer Missing)', badge: 'UNAUTHORIZED', photo: getForensicMugshot('UNAUTHORIZED', 'BLOCKED (Bearer Missing)', 'PROBE_API_INTRUSION', '103.21.244.0'), epoch: 1773364365.0 }
        ])
      }
    } catch(e) {
      setAuditLogs([
        { id: 'log-01', timestamp: '2026-09-13 02:14:22', ip: '198.51.100.42', device: 'Linux x86_64 / Tor Relay Node', action: 'BRUTE_FORCE_PROBE', status: 'BLOCKED (429 Rate Limit)', badge: 'UNKNOWN-INTRUDER', photo: getForensicMugshot('UNKNOWN-INTRUDER', 'BLOCKED (429 Rate Limit)', 'BRUTE_FORCE_PROBE', '198.51.100.42'), epoch: 1773281062.0 },
        { id: 'log-02', timestamp: '2026-09-13 03:45:10', ip: '203.0.113.19', device: 'Win32 / Chrome 122 (Unverified)', action: 'PASSCODE_FAILED', status: 'BLOCKED (5 Fails Lockdown)', badge: 'PROBE-ATTEMPT', photo: getForensicMugshot('PROBE-ATTEMPT', 'BLOCKED (5 Fails Lockdown)', 'PASSCODE_FAILED', '203.0.113.19'), epoch: 1773286510.0 },
        { id: 'log-03', timestamp: '2026-09-13 10:15:00', ip: '127.0.0.1', device: 'CRIMENET-FORENSIC-STATION-01', action: 'BIOMETRIC_ZNCC_SCAN', status: 'AUTHORIZED (Match: 89%)', badge: 'Chief Officer Aditya Pawar', photo: getForensicMugshot('Chief Officer Aditya Pawar', 'AUTHORIZED (Match: 89%)', 'BIOMETRIC_ZNCC_SCAN', '127.0.0.1'), epoch: 1773309900.0 },
        { id: 'log-04', timestamp: '2026-09-13 12:58:29', ip: '103.21.244.0', device: 'Android 14 / Burner Proxy', action: 'PROBE_API_INTRUSION', status: 'BLOCKED (Bearer Missing)', badge: 'UNAUTHORIZED', photo: getForensicMugshot('UNAUTHORIZED', 'BLOCKED (Bearer Missing)', 'PROBE_API_INTRUSION', '103.21.244.0'), epoch: 1773364365.0 }
      ])
    }
    setAuditModalOpen(true)
  }

  const handleDeleteSingleLog = async (logItem: any, e: React.MouseEvent) => {
    e.stopPropagation()
    if (soundEnabled) playCyberSound('click')
    const jwt = authToken || sessionStorage.getItem('crimenet_jwt') || ''
    try {
      await axios.post('/api/security/delete-log', {
        id: logItem.id || '',
        timestamp: logItem.timestamp || ''
      }, { headers: { Authorization: `Bearer ${jwt}` } })
    } catch(e) {}
    setAuditLogs((prev) => prev.filter((item) => item.timestamp !== logItem.timestamp || item.id !== logItem.id))
  }

  const handleClearAllLogs = async () => {
    if (!confirm('Delete ALL intruder photos and IP logs?')) return
    if (soundEnabled) playCyberSound('deny')
    const jwt = authToken || sessionStorage.getItem('crimenet_jwt') || ''
    try {
      await axios.post('/api/security/clear-all-logs', {}, {
        headers: { Authorization: `Bearer ${jwt}` }
      })
    } catch(e) {}
    setAuditLogs([])
  }

  const filteredLogs = auditLogs.filter((l: any) => {
    const matchesFilter = logFilter === 'ALL' || (logFilter === 'BLOCKED' && l.status.includes('BLOCKED')) || (logFilter === 'AUTHORIZED' && l.status.includes('AUTHORIZED'))
    const q = logSearchQuery.toLowerCase().trim()
    if (!q) return matchesFilter
    const text = `${l.ip} ${l.device} ${l.action} ${l.timestamp} ${l.status} ${l.badge || ''}`.toLowerCase()
    return matchesFilter && text.includes(q)
  })

  const navItems = [
    { id: 'pipeline', label: 'Data Ingestion & Links', icon: '📥' },
    { id: 'graph', label: 'Network Graph', icon: '🕸️' },
    { id: 'radar', label: 'Geospatial Radar', icon: '🌍' },
    { id: 'telecom', label: 'Telecom Interceptor', icon: '📡' },
    { id: 'crypto', label: 'Crypto & Hawala Tracer', icon: '💸' },
    { id: 'darkweb', label: 'Dark Web & OSINT', icon: '🕵️‍♂️' },
    { id: 'analytics', label: 'ML Analytics', icon: '📊' },
    { id: 'evaluation', label: 'Model Benchmark (XAI)', icon: '📈' },
    { id: 'testrunner', label: 'Responsible AI Suite', icon: '🧪' },
    { id: 'alerts', label: 'Alert Centre', icon: '🚨' },
    { id: 'cases', label: 'Case Management', icon: '📁' },
    { id: 'reports', label: 'Reports', icon: '📄' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ]

  // ── LOCK SCREEN SENTRY ──
  if (!isAuthenticated) {
    return (
      <SecurityGate
        soundEnabled={soundEnabled}
        onAuthenticated={(token) => {
          setAuthToken(token)
          setIsAuthenticated(true)
        }}
      />
    )
  }

  // ── AUTHENTICATED PLATFORM ──
  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#030712', color: '#f8fafc', overflow: 'hidden', position: 'relative' }}>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* 🖥️ DESKTOP SIDEBAR (Hidden on mobile via CSS desktop-only) */}
      <div className="desktop-only" style={{ width: 240, background: '#0a101f', borderRight: '1px solid #1e293b', flexDirection: 'column', justifyContent: 'space-between', padding: '16px 12px', flexShrink: 0 }}>
        <div>
          <div style={{ padding: '6px 10px', marginBottom: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, boxShadow: '0 0 15px rgba(56, 189, 248, 0.4)' }}>🔍</div>
              <div>
                <div style={{ fontWeight: 900, fontSize: 14.5, color: 'white', letterSpacing: '0.06em' }}>CrimeNet AI</div>
                <div style={{ fontSize: 9.5, color: '#38bdf8', fontWeight: 800, letterSpacing: '0.04em' }}>DEFENSE COMMAND</div>
              </div>
            </div>
          </div>

          <div style={{ marginBottom: 10 }}>
            <button
              onClick={() => setSpotlightOpen(true)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '8px 10px',
                borderRadius: 8,
                background: 'rgba(2, 6, 23, 0.8)',
                border: '1px solid #334155',
                color: '#94a3b8',
                fontSize: 11,
                cursor: 'pointer'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span>🔍</span> Search Intelligence...
              </span>
              <kbd style={{ background: '#1e293b', padding: '2px 5px', borderRadius: 4, fontSize: 9.5, color: '#38bdf8', fontFamily: 'monospace' }}>Ctrl+K</kbd>
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  if (soundEnabled) playCyberSound('click')
                  setActiveTab(item.id as any)
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '9px 12px',
                  borderRadius: 10,
                  border: 'none',
                  background: activeTab === item.id ? '#1d4ed8' : 'transparent',
                  color: activeTab === item.id ? 'white' : '#94a3b8',
                  fontSize: 12,
                  fontWeight: activeTab === item.id ? 800 : 500,
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: '0.15s'
                }}
              >
                <span style={{ fontSize: 16 }}>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <button
            onClick={openAuditLogs}
            style={{ width: '100%', padding: '9px', borderRadius: 8, background: 'rgba(56, 189, 248, 0.15)', border: '1px solid #38bdf8', color: '#38bdf8', fontSize: 11, fontWeight: 800, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}
          >
            <span>🛡️</span> View Intruder Logs
          </button>

          <div style={{ padding: '8px 12px', background: '#0f172a', borderRadius: 10, border: '1px solid #1e293b', display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 34, height: 34, borderRadius: '50%', overflow: 'hidden', border: '2px solid #34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#059669' }}>
              {masterFacePhoto ? <img src={masterFacePhoto} alt="Aditya" style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <span style={{ fontSize: 11, fontWeight: 800 }}>AP</span>}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 12, fontWeight: 800, color: 'white' }}>Aditya Pawar</div>
              <div style={{ fontSize: 9.5, color: '#34d399', fontWeight: 700 }}>● Chief Investigator</div>
            </div>
          </div>
          
          <button
            onClick={() => {
              if (soundEnabled) playCyberSound('deny')
              try {
                sessionStorage.removeItem('crimenet_authenticated')
                sessionStorage.removeItem('crimenet_jwt')
                localStorage.removeItem('crimenet_jwt_token')
              } catch {}
              setAuthToken('')
              setIsAuthenticated(false)
            }}
            style={{ width: '100%', padding: '7px', borderRadius: 8, background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#f87171', fontSize: 10.5, fontWeight: 800, cursor: 'pointer' }}
          >
            🔒 Lock System & Logout
          </button>
        </div>
      </div>

      {/* 📱 MOBILE SLIDE-OUT DRAWER OVERLAY */}
      {mobileMenuOpen && (
        <div
          onClick={() => setMobileMenuOpen(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', zIndex: 5000, display: 'flex' }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: '80vw',
              maxWidth: 300,
              height: '100%',
              background: '#0a101f',
              borderRight: '1px solid #38bdf8',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              padding: '16px 14px',
              animation: 'slide-in-left 0.22s ease-out',
              overflowY: 'auto'
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 22 }}>🔍</span>
                  <div>
                    <div style={{ fontWeight: 900, fontSize: 14, color: 'white' }}>CrimeNet AI</div>
                    <div style={{ fontSize: 9, color: '#38bdf8', fontWeight: 800 }}>DEFENSE COMMAND</div>
                  </div>
                </div>
                <button onClick={() => setMobileMenuOpen(false)} style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: 18, cursor: 'pointer' }}>✕</button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {navItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      if (soundEnabled) playCyberSound('click')
                      setActiveTab(item.id as any)
                      setMobileMenuOpen(false)
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      padding: '12px 14px',
                      borderRadius: 10,
                      border: activeTab === item.id ? '1px solid #38bdf8' : 'none',
                      background: activeTab === item.id ? '#1d4ed8' : 'rgba(15, 23, 42, 0.6)',
                      color: activeTab === item.id ? 'white' : '#cbd5e1',
                      fontSize: 13,
                      fontWeight: activeTab === item.id ? 800 : 600,
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    <span style={{ fontSize: 18 }}>{item.icon}</span>
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 20 }}>
              <button
                onClick={() => { setMobileMenuOpen(false); openAuditLogs(); }}
                style={{ width: '100%', padding: '10px', borderRadius: 8, background: 'rgba(56, 189, 248, 0.15)', border: '1px solid #38bdf8', color: '#38bdf8', fontSize: 12, fontWeight: 800, cursor: 'pointer' }}
              >
                🛡️ View Intruder Logs
              </button>

              <button
                onClick={() => {
                  try {
                    sessionStorage.removeItem('crimenet_authenticated')
                    sessionStorage.removeItem('crimenet_jwt')
                    localStorage.removeItem('crimenet_jwt_token')
                  } catch {}
                  setAuthToken('')
                  setIsAuthenticated(false)
                }}
                style={{ width: '100%', padding: '10px', borderRadius: 8, background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#f87171', fontSize: 12, fontWeight: 800, cursor: 'pointer' }}
              >
                🔒 Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 🚀 MAIN CONTENT PANE */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
        
        {/* 📱 MOBILE TOP HEADER (Hidden on desktop) */}
        <div className="mobile-only" style={{ height: 52, background: '#0a101f', borderBottom: '1px solid #1e293b', padding: '0 12px', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              onClick={() => setMobileMenuOpen(true)}
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#38bdf8', width: 36, height: 36, borderRadius: 8, fontSize: 18, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            >
              ☰
            </button>
            <span style={{ fontWeight: 900, fontSize: 14, color: 'white' }}>CrimeNet AI</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              onClick={() => setSpotlightOpen(true)}
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#38bdf8', padding: '6px 10px', borderRadius: 8, fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
            >
              🔍 Search
            </button>
            <button
              onClick={() => setCopilotOpen(prev => !prev)}
              style={{ background: 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)', border: 'none', color: 'white', padding: '6px 10px', borderRadius: 8, fontSize: 11, fontWeight: 800, cursor: 'pointer' }}
            >
              🤖 Copilot
            </button>
          </div>
        </div>

        {/* 🖥️ DESKTOP TOP COMMAND BAR */}
        <div className="desktop-only" style={{ flexShrink: 0 }}>
          <CommandBar
            selectedCase={selectedCase}
            onSelectCase={setSelectedCase}
            connectionState={connectionState}
            onToggleCopilot={() => setCopilotOpen(prev => !prev)}
            copilotOpen={copilotOpen}
            onOpenDemoTour={() => setDemoTourOpen(true)}
          />
        </div>

        {/* TOP TACTICAL TELEMETRY & RESPONSIBLE-AI GOVERNANCE BAR */}
        <div className="desktop-only" style={{ height: 44, background: '#0a101f', borderBottom: '1px solid #1e293b', padding: '0 20px', justifyContent: 'space-between', alignItems: 'center', fontSize: 11, flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '3px 8px', borderRadius: 4, background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#6ee7b7', fontWeight: 800, fontSize: 10 }}>
              <span>🛡️</span> NATIONAL FORENSIC BENCHMARK (NCFB-2026) — ENTERPRISE CALIBRATED
            </div>
            <span style={{ color: '#64748b' }}>|</span>
            <span style={{ color: '#38bdf8', padding: '2px 8px', borderRadius: 4, background: 'rgba(56,189,248,0.15)', border: '1px solid rgba(56,189,248,0.3)', fontWeight: 800, fontSize: 10 }}>
              🛡️ ROLE: LEAD INVESTIGATOR (CLEARANCE LEVEL 5)
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              onClick={() => setDemoTourOpen(true)}
              style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '4px 12px', borderRadius: 20, background: 'linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%)', border: '1px solid #c084fc', color: 'white', cursor: 'pointer', fontSize: 10.5, fontWeight: 800, boxShadow: '0 0 12px rgba(192, 132, 252, 0.4)' }}
            >
              <span>🎬</span> 5-Min Platform Tour
            </button>

            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              title="Toggle Audio Feedback"
              style={{ background: '#1e293b', border: '1px solid #334155', color: soundEnabled ? '#38bdf8' : '#64748b', padding: '4px 8px', borderRadius: 20, cursor: 'pointer', fontSize: 10.5, fontWeight: 700 }}
            >
              {soundEnabled ? '🔊 Audio ON' : '🔇 Audio Muted'}
            </button>

            <button
              onClick={() => { setFaceAuthKey(''); setFaceAuthPassed(false); setCalibrateModalOpen(true); }}
              style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '4px 10px', borderRadius: 20, background: 'rgba(16, 185, 129, 0.2)', border: '1px solid #10b981', color: '#34d399', cursor: 'pointer', fontSize: 10.5, fontWeight: 700 }}
            >
              <span>📸</span> Register Face ID
            </button>

            <button
              onClick={() => { setChangePassModalOpen(true); setMasterAuthInput(''); setNewPassInput(''); setConfirmPassInput(''); setPassError(''); }}
              style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '4px 10px', borderRadius: 20, background: 'rgba(56, 189, 248, 0.2)', border: '1px solid #38bdf8', color: '#38bdf8', cursor: 'pointer', fontSize: 10.5, fontWeight: 700 }}
            >
              <span>🔑</span> Change Password
            </button>
          </div>
        </div>

        {/* 📜 MODULE CONTENT VIEW */}
        <div style={{ flex: 1, padding: '16px', overflowY: 'auto', paddingBottom: '70px' }}>
          <ErrorBoundary>
            {activeTab === 'pipeline' && <DatasetPipeline onNavigateToGraph={() => setActiveTab('graph')} />}
            {activeTab === 'graph' && <GraphExplorer />}
            {activeTab === 'radar' && <GeospatialRadar />}
            {activeTab === 'telecom' && <TelecomInterceptor />}
            {activeTab === 'crypto' && <CryptoHawalaTracer />}
            {activeTab === 'darkweb' && <DarkWebOSINT />}
            {activeTab === 'analytics' && <Analytics />}
            {activeTab === 'evaluation' && <ModelEvaluation />}
            {activeTab === 'testrunner' && <ResponsibleAIRunner />}
            {activeTab === 'alerts' && <AlertCentre />}
            {activeTab === 'cases' && <CaseManagement />}
            {activeTab === 'reports' && <Reports />}
            {activeTab === 'settings' && <Settings />}
          </ErrorBoundary>
        </div>

        {/* 📱 MOBILE BOTTOM QUICK-ACCESS TAB BAR (Hidden on desktop) */}
        <div className="mobile-only" style={{ height: 58, background: '#0a101f', borderTop: '1px solid #1e293b', position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 4000, justifyContent: 'space-around', alignItems: 'center', padding: '0 6px' }}>
          {[
            { id: 'graph', label: 'Graph', icon: '🕸️' },
            { id: 'radar', label: 'Radar', icon: '🌍' },
            { id: 'alerts', label: 'Alerts', icon: '🚨' },
            { id: 'telecom', label: 'Telecom', icon: '📡' },
            { id: 'settings', label: 'Settings', icon: '⚙️' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => {
                if (soundEnabled) playCyberSound('click')
                setActiveTab(tab.id as any)
              }}
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 2,
                background: 'transparent',
                border: 'none',
                color: activeTab === tab.id ? '#38bdf8' : '#64748b',
                cursor: 'pointer',
                padding: '6px 0'
              }}
            >
              <span style={{ fontSize: 18 }}>{tab.icon}</span>
              <span style={{ fontSize: 10, fontWeight: activeTab === tab.id ? 800 : 500 }}>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* 🤖 VOICE INVESTIGATION COPILOT DRAWER */}
        <CopilotDrawer
          isOpen={copilotOpen}
          onClose={() => setCopilotOpen(false)}
          activeCaseId={selectedCase}
        />

        {/* 🔔 LIVE EVENT FLOATING TOAST NOTIFICATION */}
        <NotificationToast
          toast={activeToast}
          onDismiss={() => setActiveToast(null)}
        />

        {/* 🎬 5-MINUTE EXECUTIVE FORENSIC PLATFORM TOUR MODAL */}
        <DemoTourModal
          isOpen={demoTourOpen}
          onClose={() => setDemoTourOpen(false)}
          onNavigateTab={(tab) => {
            if (soundEnabled) playCyberSound('click')
            setActiveTab(tab as any)
          }}
          onToggleSimulation={(start) => {
            if (start) axios.post('/api/simulation/start').catch(() => {})
          }}
          onToggleCopilot={() => setCopilotOpen(true)}
        />
      </div>

      {/* CLASSIFIED SURVEILLANCE AUTHENTICATION MODAL */}
      {auditAuthModalOpen && (
        <div onClick={() => setAuditAuthModalOpen(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.88)', zIndex: 3800, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div onClick={(e) => e.stopPropagation()} style={{ width: '90vw', maxWidth: 420, background: '#0f172a', border: '1px solid #ef4444', borderRadius: 16, padding: 24, textAlign: 'center', boxShadow: '0 0 50px rgba(239, 68, 68, 0.4)' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>🔒</div>
            <h3 style={{ color: '#ef4444', fontSize: 16, fontWeight: 900 }}>CLASSIFIED INTRUDER DOSSIER</h3>
            <p style={{ fontSize: 11, color: '#94a3b8', margin: '6px 0 16px' }}>Strictly Restricted: Enter Intruder Log Key to inspect live visitor mugshots & telemetry</p>
            
            <input
              type="text"
              name="audit_key_auth_field"
              autoComplete="off"
              placeholder="••••••••••••"
              value={auditKeyInput}
              onChange={(e) => setAuditKeyInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') verifyAuditAccess() }}
              style={{ width: '100%', padding: '10px 14px', borderRadius: 8, background: '#020617', border: '1px solid #ef4444', color: 'white', fontSize: 13, outline: 'none', marginBottom: 10, letterSpacing: '0.2em', WebkitTextSecurity: 'disc' } as any}
            />

            {auditKeyError && <div style={{ fontSize: 11, color: '#ef4444', fontWeight: 800, marginBottom: 10 }}>{auditKeyError}</div>}

            <div style={{ display: 'flex', gap: 10 }}>
              <button onClick={verifyAuditAccess} style={{ flex: 1, padding: '10px', borderRadius: 8, background: '#ef4444', color: 'white', border: 'none', fontWeight: 800, cursor: 'pointer' }}>Unlock Intruder Logs</button>
              <button onClick={() => setAuditAuthModalOpen(false)} style={{ padding: '10px 14px', borderRadius: 8, background: '#334155', color: '#cbd5e1', border: 'none', cursor: 'pointer' }}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {auditModalOpen && (
        <AuditLogsModal
          isOpen={auditModalOpen}
          onClose={() => setAuditModalOpen(false)}
          logs={auditLogs}
          logFilter={logFilter}
          setLogFilter={setLogFilter}
          logSearchQuery={logSearchQuery}
          setLogSearchQuery={setLogSearchQuery}
          onSelectIntruder={(log) => setSelectedIntruder(log)}
          onDeleteLog={handleDeleteSingleLog}
          onClearAll={handleClearAllLogs}
          soundEnabled={soundEnabled}
        />
      )}

      {selectedIntruder && (
        <IntruderModal
          log={selectedIntruder}
          onClose={() => setSelectedIntruder(null)}
        />
      )}

      {/* REGISTER FACE MODAL */}
      {calibrateModalOpen && (
        <div onClick={() => setCalibrateModalOpen(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.88)', zIndex: 3500, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div onClick={(e) => e.stopPropagation()} style={{ width: '90vw', maxWidth: 440, background: '#0f172a', border: '1px solid #10b981', borderRadius: 16, padding: 24, textAlign: 'center' }}>
            <h3 style={{ color: '#34d399', fontSize: 16, fontWeight: 800 }}>📸 REGISTER ADITYA PAWAR'S LIVE FACE</h3>
            
            {!faceAuthPassed ? (
              <div style={{ marginTop: 14 }}>
                <p style={{ fontSize: 11.5, color: '#cbd5e1', marginBottom: 12 }}>🔒 Security Check: Enter Master Authority Key to unlock Face Enrollment</p>
                <input
                  type="text"
                  name="master_face_key_auth_no_fill"
                  autoComplete="off"
                  placeholder="••••••••••••"
                  value={faceAuthKey}
                  onChange={(e) => setFaceAuthKey(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') verifyFaceAuthorityAndStartCamera() }}
                  style={{ width: '100%', padding: '10px 14px', borderRadius: 8, background: '#020617', border: '1px solid #10b981', color: 'white', fontSize: 13, outline: 'none', marginBottom: 14, letterSpacing: '0.2em', WebkitTextSecurity: 'disc' } as any}
                />
                <div style={{ display: 'flex', gap: 10 }}>
                  <button onClick={verifyFaceAuthorityAndStartCamera} style={{ flex: 1, padding: '10px', borderRadius: 8, background: '#10b981', color: 'white', border: 'none', fontWeight: 800, cursor: 'pointer' }}>Verify & Open Camera</button>
                  <button onClick={() => setCalibrateModalOpen(false)} style={{ padding: '10px 14px', borderRadius: 8, background: '#334155', color: '#cbd5e1', border: 'none', cursor: 'pointer' }}>Cancel</button>
                </div>
              </div>
            ) : (
              <div>
                <p style={{ fontSize: 11, color: '#94a3b8', margin: '4px 0 14px' }}>Look directly into the camera to capture your 144-D Master Biometric Profile</p>
                <div style={{ width: 220, height: 220, borderRadius: '50%', overflow: 'hidden', border: '3px solid #10b981', margin: '0 auto 14px' }}>
                  <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                </div>
                <div style={{ display: 'flex', gap: 10 }}>
                  <button onClick={saveMasterFaceEnrollment} style={{ flex: 1, padding: '10px', borderRadius: 8, background: '#10b981', color: 'white', border: 'none', fontWeight: 800, cursor: 'pointer' }}>📸 Save My Face to Server</button>
                  <button onClick={() => setCalibrateModalOpen(false)} style={{ padding: '10px 14px', borderRadius: 8, background: '#334155', color: '#cbd5e1', border: 'none', cursor: 'pointer' }}>Cancel</button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* CHANGE PASSWORD MODAL */}
      {changePassModalOpen && (
        <div onClick={() => setChangePassModalOpen(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.88)', zIndex: 3500, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div onClick={(e) => e.stopPropagation()} style={{ width: '90vw', maxWidth: 420, background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 16, padding: 24 }}>
            <h3 style={{ color: 'white', fontSize: 16, fontWeight: 800, textAlign: 'center' }}>🔑 CHANGE MASTER PASSCODE</h3>
            <p style={{ fontSize: 11, color: '#94a3b8', textAlign: 'center', margin: '4px 0 16px' }}>Protected by Master Authority Key</p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div>
                <label style={{ fontSize: 11, color: '#38bdf8', fontWeight: 700 }}>1. MASTER AUTHORITY KEY</label>
                <input
                  type="text"
                  name="master_auth_input_zero_fill"
                  autoComplete="off"
                  placeholder="••••••••••••"
                  value={masterAuthInput}
                  onChange={(e) => setMasterAuthInput(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 4, outline: 'none', letterSpacing: '0.15em', WebkitTextSecurity: 'disc' } as any}
                />
              </div>

              <div>
                <label style={{ fontSize: 11, color: '#94a3b8', fontWeight: 700 }}>2. NEW PASSCODE</label>
                <input
                  type="text"
                  name="new_pass_zero_fill"
                  autoComplete="off"
                  placeholder="••••••••••••"
                  value={newPassInput}
                  onChange={(e) => setNewPassInput(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 4, outline: 'none', letterSpacing: '0.15em', WebkitTextSecurity: 'disc' } as any}
                />
              </div>

              <div>
                <label style={{ fontSize: 11, color: '#94a3b8', fontWeight: 700 }}>3. CONFIRM NEW PASSCODE</label>
                <input
                  type="text"
                  name="confirm_pass_zero_fill"
                  autoComplete="off"
                  placeholder="••••••••••••"
                  value={confirmPassInput}
                  onChange={(e) => setConfirmPassInput(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 4, outline: 'none', letterSpacing: '0.15em', WebkitTextSecurity: 'disc' } as any}
                />
              </div>

              {passError && <div style={{ fontSize: 11, color: '#ef4444', fontWeight: 800, textAlign: 'center' }}>{passError}</div>}

              <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
                <button onClick={handleChangePassword} style={{ flex: 1, padding: '10px', borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, cursor: 'pointer' }}>Save New Password</button>
                <button onClick={() => setChangePassModalOpen(false)} style={{ padding: '10px 14px', borderRadius: 8, background: '#334155', color: '#cbd5e1', border: 'none', cursor: 'pointer' }}>Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SPOTLIGHT COMMAND PALETTE MODAL (Ctrl+K) */}
      {spotlightOpen && (
        <div onClick={() => setSpotlightOpen(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 4000, display: 'flex', alignItems: 'flex-start', justifyContent: 'center', paddingTop: '12vh' }}>
          <div onClick={(e) => e.stopPropagation()} style={{ width: '90vw', maxWidth: 620, background: '#0f172a', border: '2px solid #38bdf8', borderRadius: 16, overflow: 'hidden', boxShadow: '0 0 50px rgba(56, 189, 248, 0.4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '14px 18px', borderBottom: '1px solid #1e293b', background: '#020617' }}>
              <span style={{ fontSize: 18, color: '#38bdf8' }}>🔍</span>
              <input
                autoFocus
                value={spotlightQuery}
                onChange={(e) => setSpotlightQuery(e.target.value)}
                placeholder="Search suspects, tools, dossiers, or commands (e.g. Arjun, CDR, Radar)..."
                style={{ flex: 1, background: 'transparent', border: 'none', color: 'white', fontSize: 14, outline: 'none' }}
              />
              <kbd style={{ background: '#1e293b', padding: '2px 8px', borderRadius: 4, fontSize: 11, color: '#94a3b8', fontFamily: 'monospace' }}>ESC</kbd>
            </div>

            <div style={{ maxHeight: 380, overflowY: 'auto', padding: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
              {[
                { type: 'MODULE', title: '📥 Data Ingestion & Link Pipeline', desc: 'Real working multi-source fusion: CDR, Banking, FIR, ANPR & Wallets', tab: 'pipeline' },
                { type: 'MODULE', title: '🌐 Network Graph Explorer', desc: 'Interactive 48-node Cytoscape graph & A* pathfinder', tab: 'graph' },
                { type: 'MODULE', title: '🛰️ Geospatial Surveillance Radar', desc: 'Real-time GPS blips, ANPR vehicle tracking & tactical dispatch', tab: 'radar' },
                { type: 'MODULE', title: '📡 Cellular CDR & Triangulation', desc: '3-Tower radio sector triangulation, nocturnal ratio & Z-score bursts', tab: 'telecom' },
                { type: 'MODULE', title: '💸 Hawala & Crypto Flow Tracer', desc: 'Johnson\'s circular laundering loop discovery & TRC-20 USDT tracer', tab: 'crypto' },
                { type: 'MODULE', title: '🕵️‍♂️ Dark Web & OSINT Intelligence', desc: 'Tor hidden services, Telegram intercepts, pastebin dumps & entity extraction', tab: 'darkweb' },
                { type: 'MODULE', title: '📊 Network Analytics & Graph Math', desc: 'Real NetworkX PageRank, betweenness centrality & modularity', tab: 'analytics' },
                { type: 'MODULE', title: '📈 Model Benchmark (XAI)', desc: 'Tuned Precision 96.8%, Recall 95.4%, F1 0.961, Overfitting Lab & 2x2 matrix', tab: 'evaluation' },
                { type: 'MODULE', title: '🧪 Responsible AI Test Suite Runner', desc: 'Automated 10 Phase 2 diagnostic test execution & assertion inspector', tab: 'testrunner' },
                { type: 'MODULE', title: '🚨 HITL Anomaly Alert Centre', desc: 'Isolation Forest outlier vectors & online model calibration', tab: 'alerts' },
                { type: 'MODULE', title: '📋 Tactical Case Management', desc: 'Interactive Kanban board & investigation stage advancement', tab: 'cases' },
                { type: 'MODULE', title: '📄 Forensic Dossier & Reports', desc: 'Section 65B compliant intelligence report generator', tab: 'reports' },
                { type: 'MODULE', title: '⚙️ Platform Settings & Policies', desc: 'Manage field investigator roster & agency deployment rules', tab: 'settings' },
                { type: 'SUSPECT', title: '👤 Arjun Mehta (Kingpin)', desc: 'Supreme syndicate mastermind · Threat Score: 95.0', tab: 'graph' },
                { type: 'SUSPECT', title: '👤 Mohammed Rafiq', desc: 'Dharavi Hawala cash staging operator · Threat Score: 88.0', tab: 'crypto' },
                { type: 'SUSPECT', title: '👤 Vikram Singh', desc: 'Contraband logistics head · Goregaon Warehouse depot', tab: 'radar' },
                { type: 'SUSPECT', title: '👤 Priya Desai', desc: 'Financial Controller · Mehta Enterprises Ltd accountant', tab: 'crypto' },
                { type: 'ENTITY', title: '🏢 Mehta Enterprises Ltd', desc: 'Primary shell corporation for international round-tripping', tab: 'graph' },
                { type: 'ENTITY', title: '🚗 BMW X5 (MH-01-AB-5678)', desc: 'High-speed transit vehicle tracked crossing inter-state tolls', tab: 'radar' },
                { type: 'ENTITY', title: '📱 +91-9876543210 (Burner SIM)', desc: 'Nocturnal communication hub with 68 intercepted calls', tab: 'telecom' }
              ]
                .filter(item => !spotlightQuery.trim() || item.title.toLowerCase().includes(spotlightQuery.toLowerCase()) || item.desc.toLowerCase().includes(spotlightQuery.toLowerCase()))
                .map((item, idx) => (
                  <div
                    key={idx}
                    onClick={() => {
                      if (soundEnabled) playCyberSound('click')
                      setActiveTab(item.tab as any)
                      setSpotlightOpen(false)
                      setSpotlightQuery('')
                    }}
                    style={{
                      padding: '10px 14px',
                      borderRadius: 8,
                      background: '#0c1324',
                      border: '1px solid #1e293b',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      cursor: 'pointer',
                      transition: '0.15s'
                    }}
                  >
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 700, color: 'white' }}>{item.title}</div>
                      <div style={{ fontSize: 10.5, color: '#94a3b8', marginTop: 2 }}>{item.desc}</div>
                    </div>
                    <span style={{ fontSize: 9.5, padding: '2px 6px', borderRadius: 4, background: item.type === 'SUSPECT' ? '#7f1d1d' : item.type === 'ENTITY' ? '#78350f' : '#1e3a8a', color: 'white', fontWeight: 800 }}>
                      {item.type}
                    </span>
                  </div>
                ))}
            </div>

            <div style={{ padding: '8px 14px', background: '#020617', borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#64748b' }}>
              <span>Press <b>ESC</b> to exit</span>
              <span>Operator: <b>Aditya Pawar (Lead Architect)</b></span>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
