import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import GraphExplorer from './pages/GraphExplorer'
import GeospatialRadar from './pages/GeospatialRadar'
import TelecomInterceptor from './pages/TelecomInterceptor'
import CryptoHawalaTracer from './pages/CryptoHawalaTracer'
import Analytics from './pages/Analytics'
import AlertCentre from './pages/AlertCentre'
import CaseManagement from './pages/CaseManagement'
import Reports from './pages/Reports'
import Settings from './pages/Settings'

// ── TACTICAL CYBER AUDIO SYNTHESIZER (WEB AUDIO API) ──
const playCyberSound = (type: 'beep' | 'grant' | 'deny' | 'click' | 'scan') => {
  try {
    const AudioContext = window.AudioContext || (window as any).webkitAudioContext
    if (!AudioContext) return
    const ctx = new AudioContext()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)

    const now = ctx.currentTime
    if (type === 'click') {
      osc.type = 'sine'
      osc.frequency.setValueAtTime(800, now)
      osc.frequency.exponentialRampToValueAtTime(400, now + 0.05)
      gain.gain.setValueAtTime(0.15, now)
      gain.gain.linearRampToValueAtTime(0.01, now + 0.05)
      osc.start(now)
      osc.stop(now + 0.05)
    } else if (type === 'grant') {
      osc.type = 'triangle'
      osc.frequency.setValueAtTime(523.25, now) // C5
      osc.frequency.setValueAtTime(659.25, now + 0.08) // E5
      osc.frequency.setValueAtTime(783.99, now + 0.16) // G5
      osc.frequency.setValueAtTime(1046.50, now + 0.24) // C6
      gain.gain.setValueAtTime(0.2, now)
      gain.gain.linearRampToValueAtTime(0.01, now + 0.45)
      osc.start(now)
      osc.stop(now + 0.45)
    } else if (type === 'deny') {
      osc.type = 'sawtooth'
      osc.frequency.setValueAtTime(220, now)
      osc.frequency.setValueAtTime(140, now + 0.12)
      gain.gain.setValueAtTime(0.3, now)
      gain.gain.linearRampToValueAtTime(0.01, now + 0.35)
      osc.start(now)
      osc.stop(now + 0.35)
    } else if (type === 'scan') {
      osc.type = 'sine'
      osc.frequency.setValueAtTime(600, now)
      osc.frequency.linearRampToValueAtTime(1200, now + 0.15)
      gain.gain.setValueAtTime(0.1, now)
      gain.gain.linearRampToValueAtTime(0.01, now + 0.15)
      osc.start(now)
      osc.stop(now + 0.15)
    }
  } catch(e) {}
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [pinCode, setPinCode] = useState('')
  const [badgeId, setBadgeId] = useState('INV-2026-AP01')
  const [authError, setAuthError] = useState('')
  const [soundEnabled, setSoundEnabled] = useState(true)

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

  // INTRUDER LOGS MODAL & DEDICATED PASSWORD LOCK (Aditya@09)
  const [auditAuthModalOpen, setAuditAuthModalOpen] = useState(false)
  const [auditKeyInput, setAuditKeyInput] = useState('')
  const [auditKeyError, setAuditKeyError] = useState('')
  const [auditModalOpen, setAuditModalOpen] = useState(false)
  const [auditLogs, setAuditLogs] = useState<any[]>([])
  const [logFilter, setLogFilter] = useState<'ALL' | 'BLOCKED' | 'AUTHORIZED'>('ALL')
  const [selectedIntruder, setSelectedIntruder] = useState<any>(null)

  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const [activeTab, setActiveTab] = useState<'graph' | 'radar' | 'telecom' | 'crypto' | 'analytics' | 'alerts' | 'cases' | 'reports' | 'settings'>('graph')
  const [spotlightOpen, setSpotlightOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  // Sync profile from server on load
  useEffect(() => {
    axios.get('/api/security/master-profile').then((res) => {
      if (res.data.photo) {
        setMasterFacePhoto(res.data.photo)
        localStorage.setItem('aditya_master_face_photo', res.data.photo)
      }
    }).catch(() => {})
  }, [])

  // LOCKDOWN TIMER
  useEffect(() => {
    if (lockoutTimer > 0) {
      const interval = setInterval(() => setLockoutTimer((p) => p - 1), 1000)
      return () => clearInterval(interval)
    }
  }, [lockoutTimer])

  // EXTRACT 144-D SPATIAL BIOMETRIC MATRIX
  const extractBiometricDescriptor = (): number[] => {
    if (!videoRef.current || !canvasRef.current) return []
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return []

    canvas.width = 12
    canvas.height = 12
    ctx.drawImage(videoRef.current, 0, 0, 12, 12)
    const imgData = ctx.getImageData(0, 0, 12, 12)
    const descriptor: number[] = []

    for (let i = 0; i < imgData.data.length; i += 4) {
      const lum = imgData.data[i] * 0.299 + imgData.data[i+1] * 0.587 + imgData.data[i+2] * 0.114
      descriptor.push(Math.round(lum))
    }
    return descriptor
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

  // ZERO-MEAN NORMALIZED CROSS CORRELATION (ZNCC)
  const computeZNCC = (vecA: number[], vecB: number[]): number => {
    if (!vecA || !vecB || vecA.length !== vecB.length || vecA.length === 0) return 0
    const meanA = vecA.reduce((sum, v) => sum + v, 0) / vecA.length
    const meanB = vecB.reduce((sum, v) => sum + v, 0) / vecB.length

    let dot = 0, varA = 0, varB = 0
    for (let i = 0; i < vecA.length; i++) {
      const a = vecA[i] - meanA
      const b = vecB[i] - meanB
      dot += a * b
      varA += a * a
      varB += b * b
    }

    if (varA === 0 || varB === 0) return 0
    const r = dot / (Math.sqrt(varA) * Math.sqrt(varB))
    if (r < 0) return 0
    return Math.round(r * 100)
  }

  // 1. BIOMETRIC FACE VERIFICATION
  const startBiometricScan = async () => {
    if (lockoutTimer > 0) return
    try {
      if (soundEnabled) playCyberSound('scan')
      setFaceScanActive(true)
      setScanStatus('scanning')
      setAuthError('')

      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 480, height: 480, facingMode: 'user' } })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
      }

      setTimeout(async () => {
        const liveVec = extractBiometricDescriptor()
        const photo = snapHighResPhoto()
        const ipRes = await axios.get('https://api.ipify.org?format=json').catch(() => ({ data: { ip: 'Remote' } }))

        const saved = masterFaceDescriptor
        const znccScore = saved ? computeZNCC(liveVec, saved) : 0
        setSimilarityScore(znccScore)

        if (saved && znccScore >= 65) {
          if (soundEnabled) playCyberSound('grant')
          setScanStatus('verified')
          setFailedAttempts(0)

          try {
            await axios.post('/api/security/log-visit', {
              ip: ipRes.data.ip,
              device: navigator.userAgent.substring(0, 45),
              action: `FACEID_MATCH_${znccScore}%`,
              status: 'AUTHORIZED',
              badge: 'Aditya Pawar (Chief Architect)',
              photo: photo
            })
          } catch(e) {}

          setTimeout(() => {
            if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
            setIsAuthenticated(true)
            setFaceScanActive(false)
          }, 800)

        } else {
          if (soundEnabled) playCyberSound('deny')
          setScanStatus('rejected')
          setAuthError(`🚨 INTRUDER DETECTED (${znccScore}% match)!`)

          try {
            await axios.post('/api/security/log-visit', {
              ip: ipRes.data.ip,
              device: navigator.userAgent.substring(0, 45),
              action: `INTRUDER_FACE_FAILED_${znccScore}%`,
              status: 'BLOCKED_INTRUDER',
              badge: 'Unauthorized Visitor',
              photo: photo
            })
          } catch(e) {}

          setTimeout(() => {
            if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
            setFaceScanActive(false)
            setScanStatus('idle')
          }, 3500)
        }
      }, 1900)

    } catch (err) {
      setAuthError('⚠️ Camera permission required for face unlock.')
      setFaceScanActive(false)
    }
  }

  // 2. PASSCODE LOGIN (Strictly Aditya@4912)
  const handlePasscodeLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (lockoutTimer > 0) return

    const entered = pinCode.trim()
    const isOk = entered === 'Aditya@4912' || entered.toLowerCase() === 'aditya@4912'
    const ipRes = await axios.get('https://api.ipify.org?format=json').catch(() => ({ data: { ip: 'Remote' } }))

    await axios.post('/api/security/log-visit', {
      ip: ipRes.data.ip,
      device: navigator.userAgent.substring(0, 45),
      action: isOk ? 'PASSCODE_SUCCESS' : `WRONG_PASSCODE_ATTEMPT_#${failedAttempts + 1}`,
      status: isOk ? 'AUTHORIZED' : 'BLOCKED_INTRUDER',
      badge: isOk ? 'Aditya Pawar' : 'Failed Passcode Attempt',
      photo: ''
    }).catch(() => {})

    if (isOk) {
      if (soundEnabled) playCyberSound('grant')
      setIsAuthenticated(true)
      setFailedAttempts(0)
      setAuthError('')
    } else {
      if (soundEnabled) playCyberSound('deny')
      const newFails = failedAttempts + 1
      setFailedAttempts(newFails)

      if (newFails >= 3) {
        setLockoutTimer(30)
        setAuthError('🚨 HARDWARE LOCKDOWN: 3 Failed Attempts! Locked for 30 seconds.')
      } else {
        setAuthError(`🚨 ACCESS DENIED: Invalid Passcode. (${3 - newFails} attempts remaining)`)
      }
      setTimeout(() => { if (lockoutTimer <= 0) setAuthError('') }, 4000)
    }
  }

  // 3. REGISTER MASTER FACE (Strictly Aditya@4912)
  const verifyFaceAuthorityAndStartCamera = async () => {
    const entered = faceAuthKey.trim()
    if (entered !== 'Aditya@4912' && entered.toLowerCase() !== 'aditya@4912') {
      if (soundEnabled) playCyberSound('deny')
      alert('🚨 ACCESS DENIED: Master Authority Key is incorrect!')
      return
    }
    if (soundEnabled) playCyberSound('click')
    setFaceAuthPassed(true)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 480, height: 480, facingMode: 'user' } })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
      }
    } catch(e) {
      alert('Camera access denied or not available.')
    }
  }

  const saveMasterFaceEnrollment = async () => {
    const descriptor = extractBiometricDescriptor()
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
        key: 'Aditya@4912',
        vector: descriptor,
        photo: photo
      })
    } catch(e) {}

    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
    setCalibrateModalOpen(false)
    if (soundEnabled) playCyberSound('grant')
    alert('✓ Face Biometrics Successfully Saved and Locked!')
  }

  // 4. CHANGE PASSWORD (Strictly Aditya@4912)
  const handleChangePassword = async () => {
    setPassError('')
    const entered = masterAuthInput.trim()
    if (entered !== 'Aditya@4912' && entered.toLowerCase() !== 'aditya@4912') {
      if (soundEnabled) playCyberSound('deny')
      setPassError('🚨 Master Authority Key is incorrect.')
      return
    }
    if (newPassInput.trim().length < 4) {
      setPassError('⚠️ New password must be at least 4 characters.')
      return
    }
    if (newPassInput.trim() !== confirmPassInput.trim()) {
      setPassError('⚠️ New Passwords do not match.')
      return
    }

    try {
      await axios.post('/api/security/change-password', {
        key: 'Aditya@4912',
        new_password: newPassInput.trim()
      })
    } catch(e) {}

    setChangePassModalOpen(false)
    setMasterAuthInput('')
    setNewPassInput('')
    setConfirmPassInput('')
    if (soundEnabled) playCyberSound('grant')
    alert('✓ Master Password Successfully Updated!')
  }

  // 5. INTRUDER LOGS HANDLERS (Password: Aditya@09)
  const openAuditLogs = () => {
    if (soundEnabled) playCyberSound('click')
    setAuditKeyInput('')
    setAuditKeyError('')
    setAuditAuthModalOpen(true)
  }

  const verifyAuditAccess = async () => {
    const entered = auditKeyInput.trim()
    if (entered !== 'Aditya@09' && entered.toLowerCase() !== 'aditya@09') {
      if (soundEnabled) playCyberSound('deny')
      setAuditKeyError('🚨 ACCESS DENIED: Incorrect Intruder Log Key!')
      return
    }
    if (soundEnabled) playCyberSound('grant')
    setAuditAuthModalOpen(false)
    try {
      const res = await axios.get('/api/security/audit-logs')
      setAuditLogs(res.data.logs || [])
    } catch(e) {
      setAuditLogs([])
    }
    setAuditModalOpen(true)
  }

  const handleDeleteSingleLog = async (logItem: any, e: React.MouseEvent) => {
    e.stopPropagation()
    if (soundEnabled) playCyberSound('click')
    try {
      await axios.post('/api/security/delete-log', {
        id: logItem.id || '',
        timestamp: logItem.timestamp || ''
      })
    } catch(e) {}
    setAuditLogs((prev) => prev.filter((item) => item.timestamp !== logItem.timestamp && item.id !== logItem.id))
  }

  const handleClearAllLogs = async () => {
    if (!confirm('⚠️ Delete ALL intruder photos and IP logs?')) return
    if (soundEnabled) playCyberSound('deny')
    try {
      await axios.post('/api/security/clear-all-logs')
    } catch(e) {}
    setAuditLogs([])
  }

  const filteredLogs = auditLogs.filter((l: any) => {
    if (logFilter === 'BLOCKED') return l.status.includes('BLOCKED')
    if (logFilter === 'AUTHORIZED') return l.status.includes('AUTHORIZED')
    return true
  })

  const navItems = [
    { id: 'graph', label: 'Network Graph', icon: '🕸️' },
    { id: 'radar', label: 'Geospatial Radar', icon: '🌍' },
    { id: 'telecom', label: 'Telecom Interceptor', icon: '📡' },
    { id: 'crypto', label: 'Crypto & Hawala Tracer', icon: '💸' },
    { id: 'analytics', label: 'ML Analytics', icon: '📊' },
    { id: 'alerts', label: 'Alert Centre', icon: '🚨' },
    { id: 'cases', label: 'Case Management', icon: '📁' },
    { id: 'reports', label: 'Reports', icon: '📄' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ]

  // ── LOCK SCREEN ──
  if (!isAuthenticated) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', width: '100vw', background: 'radial-gradient(circle at 50% 30%, #0c1a30 0%, #030712 85%)', color: '#f8fafc', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        
        <div style={{ width: '92vw', maxWidth: 470, background: 'rgba(15, 23, 42, 0.92)', border: lockoutTimer > 0 ? '2px solid #ef4444' : '1px solid rgba(56, 189, 248, 0.5)', borderRadius: 28, padding: 36, boxShadow: lockoutTimer > 0 ? '0 25px 90px rgba(239,68,68,0.6)' : '0 25px 100px rgba(0,0,0,0.95), 0 0 50px rgba(56, 189, 248, 0.25)', backdropFilter: 'blur(30px)' }}>
          
          <div style={{ textAlign: 'center', marginBottom: 22 }}>
            <div style={{ width: 56, height: 56, borderRadius: '50%', background: lockoutTimer > 0 ? 'rgba(239, 68, 68, 0.25)' : 'rgba(37, 99, 235, 0.25)', border: lockoutTimer > 0 ? '2px solid #ef4444' : '2px solid #38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, margin: '0 auto 12px', boxShadow: lockoutTimer > 0 ? '0 0 20px #ef4444' : '0 0 20px #38bdf8' }}>
              {lockoutTimer > 0 ? '🚨' : '🔒'}
            </div>
            <h1 style={{ fontSize: 20, fontWeight: 900, color: 'white', letterSpacing: '0.08em', textTransform: 'uppercase' }}>CRIMENET AI SECURITY GATE</h1>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '3px 10px', borderRadius: 20, background: lockoutTimer > 0 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(56, 189, 248, 0.15)', marginTop: 6, border: lockoutTimer > 0 ? '1px solid #ef4444' : '1px solid #38bdf8' }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: lockoutTimer > 0 ? '#ef4444' : '#34d399', animation: 'pulse 1.5s infinite' }}></span>
              <span style={{ fontSize: 10, color: lockoutTimer > 0 ? '#ef4444' : '#38bdf8', fontWeight: 800, letterSpacing: '0.05em' }}>
                {lockoutTimer > 0 ? `HARDWARE LOCKDOWN: WAITING ${lockoutTimer}s` : 'ZNCC BIOMETRIC SENTRY // ADITYA PAWAR ONLY'}
              </span>
            </div>
          </div>

          {faceScanActive ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 20 }}>
              <div style={{ position: 'relative', width: 230, height: 230, borderRadius: '50%', overflow: 'hidden', border: scanStatus === 'verified' ? '3px solid #10b981' : scanStatus === 'rejected' ? '3px solid #ef4444' : '3px solid #38bdf8', boxShadow: scanStatus === 'verified' ? '0 0 40px #10b981' : scanStatus === 'rejected' ? '0 0 40px #ef4444' : '0 0 40px #38bdf8' }}>
                <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                
                {/* CYBER SCANNING HUD OVERLAY */}
                {scanStatus === 'scanning' && (
                  <div style={{ position: 'absolute', inset: 0, border: '2px dashed rgba(56, 189, 248, 0.6)', borderRadius: '50%', animation: 'spin 4s linear infinite', pointerEvents: 'none' }} />
                )}
              </div>
              <div style={{ marginTop: 14, textAlign: 'center' }}>
                <div style={{ fontSize: 13.5, fontWeight: 900, color: scanStatus === 'verified' ? '#34d399' : scanStatus === 'rejected' ? '#ef4444' : '#38bdf8', letterSpacing: '0.04em' }}>
                  {scanStatus === 'verified' && `✓ MATCH CONFIRMED: ADITYA PAWAR (${similarityScore}%)`}
                  {scanStatus === 'rejected' && `🚨 STRANGER REJECTED (${similarityScore}%): MUGSHOT LOGGED!`}
                  {scanStatus === 'scanning' && `COMPUTING ZERO-MEAN FACIAL CORRELATION...`}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              
              <button
                type="button"
                disabled={lockoutTimer > 0}
                onClick={startBiometricScan}
                style={{
                  width: '100%',
                  padding: '14px',
                  borderRadius: 12,
                  background: lockoutTimer > 0 ? '#334155' : 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)',
                  border: '1px solid #38bdf8',
                  color: 'white',
                  fontWeight: 900,
                  fontSize: 14,
                  cursor: lockoutTimer > 0 ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 10,
                  boxShadow: lockoutTimer > 0 ? 'none' : '0 0 30px rgba(56, 189, 248, 0.45)',
                  transition: '0.2s'
                }}
              >
                <span style={{ fontSize: 20 }}>📸</span>
                <span>Verify Face Biometrics to Unlock</span>
              </button>

              <div style={{ textAlign: 'center', fontSize: 11, color: '#64748b', margin: '2px 0' }}>— OR ENTER CLASSIFIED PASSCODE —</div>

              <div>
                <label style={{ fontSize: 10.5, color: '#94a3b8', fontWeight: 800, letterSpacing: '0.05em' }}>OFFICER BADGE ID</label>
                <input
                  type="text"
                  value={badgeId}
                  onChange={(e) => setBadgeId(e.target.value)}
                  style={{ width: '100%', padding: '10px 14px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, marginTop: 4, outline: 'none', fontFamily: 'monospace' }}
                />
              </div>

              <div>
                <label style={{ fontSize: 10.5, color: '#94a3b8', fontWeight: 800, letterSpacing: '0.05em' }}>SECURITY PASSCODE</label>
                <input
                  type="text"
                  name="auth_field_no_fill_sec"
                  autoComplete="off"
                  disabled={lockoutTimer > 0}
                  placeholder="••••••••••••"
                  value={pinCode}
                  onChange={(e) => setPinCode(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') handlePasscodeLogin() }}
                  style={{ width: '100%', padding: '10px 14px', borderRadius: 8, background: '#020617', border: '1px solid #38bdf8', color: 'white', fontSize: 12, marginTop: 4, outline: 'none', letterSpacing: '0.2em', WebkitTextSecurity: 'disc' } as any}
                />
              </div>

              {authError && (
                <div style={{ fontSize: 11.5, color: authError.startsWith('✓') ? '#34d399' : '#ef4444', fontWeight: 900, textAlign: 'center' }}>
                  {authError}
                </div>
              )}

              <button
                disabled={lockoutTimer > 0}
                onClick={() => handlePasscodeLogin()}
                style={{ width: '100%', padding: '11px', borderRadius: 8, background: lockoutTimer > 0 ? '#1e293b' : '#334155', color: lockoutTimer > 0 ? '#64748b' : '#cbd5e1', border: 'none', fontWeight: 800, fontSize: 12.5, cursor: lockoutTimer > 0 ? 'not-allowed' : 'pointer', marginTop: 4 }}
              >
                ⚡ Authenticate with Passcode
              </button>
            </div>
          )}

          <div style={{ marginTop: 22, textAlign: 'center', fontSize: 10.5, color: '#475569' }}>
            Zero-Mean Facial Correlation Engine · Architect: <b style={{ color: '#cbd5e1' }}>Aditya Pawar</b>
          </div>
        </div>
      </div>
    )
  }

  // ── AUTHENTICATED PLATFORM ──
  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#030712', color: '#f8fafc', overflow: 'hidden' }}>
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <div style={{ width: 240, background: '#0a101f', borderRight: '1px solid #1e293b', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '16px 12px' }}>
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
              setIsAuthenticated(false)
            }}
            style={{ width: '100%', padding: '7px', borderRadius: 8, background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#f87171', fontSize: 10.5, fontWeight: 800, cursor: 'pointer' }}
          >
            🔒 Lock System & Logout
          </button>
        </div>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        {/* TOP TACTICAL TELEMETRY BAR */}
        <div style={{ height: 48, background: '#0a101f', borderBottom: '1px solid #1e293b', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '3px 8px', borderRadius: 4, background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#34d399', fontWeight: 800, fontSize: 10 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#34d399' }}></span>
              DEFCON 3 · ACTIVE RADAR
            </div>
            <span style={{ color: '#64748b' }}>|</span>
            <span style={{ color: '#94a3b8', fontFamily: 'monospace' }}>🕒 {currentTime}</span>
            <span style={{ color: '#64748b' }}>|</span>
            <span style={{ color: '#94a3b8' }}>NODES MONITORED: <b style={{ color: 'white' }}>1,420</b></span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              title="Toggle Audio Feedback"
              style={{ background: '#1e293b', border: '1px solid #334155', color: soundEnabled ? '#38bdf8' : '#64748b', padding: '5px 10px', borderRadius: 20, cursor: 'pointer', fontSize: 11, fontWeight: 700 }}
            >
              {soundEnabled ? '🔊 Audio ON' : '🔇 Audio Muted'}
            </button>

            <button
              onClick={() => { setFaceAuthKey(''); setFaceAuthPassed(false); setCalibrateModalOpen(true); }}
              style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '5px 12px', borderRadius: 20, background: 'rgba(16, 185, 129, 0.2)', border: '1px solid #10b981', color: '#34d399', cursor: 'pointer', fontSize: 11, fontWeight: 700 }}
            >
              <span>📸</span> Register Face ID
            </button>

            <button
              onClick={() => { setChangePassModalOpen(true); setMasterAuthInput(''); setNewPassInput(''); setConfirmPassInput(''); setPassError(''); }}
              style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '5px 12px', borderRadius: 20, background: 'rgba(56, 189, 248, 0.2)', border: '1px solid #38bdf8', color: '#38bdf8', cursor: 'pointer', fontSize: 11, fontWeight: 700 }}
            >
              <span>🔑</span> Change Password
            </button>
          </div>
        </div>

        <div style={{ flex: 1, padding: 20, overflowY: 'auto' }}>
          {activeTab === 'graph' && <GraphExplorer />}
          {activeTab === 'radar' && <GeospatialRadar />}
          {activeTab === 'telecom' && <TelecomInterceptor />}
          {activeTab === 'crypto' && <CryptoHawalaTracer />}
          {activeTab === 'analytics' && <Analytics />}
          {activeTab === 'alerts' && <AlertCentre />}
          {activeTab === 'cases' && <CaseManagement />}
          {activeTab === 'reports' && <Reports />}
          {activeTab === 'settings' && <Settings />}
        </div>
      </div>

      {/* CLASSIFIED SURVEILLANCE AUTHENTICATION MODAL (Password: Aditya@09) */}
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

      {/* INTRUDER LOGS MODAL WITH FILTER TABS */}
      {auditModalOpen && (
        <div onClick={() => setAuditModalOpen(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 3000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div onClick={(e) => e.stopPropagation()} style={{ width: '92vw', maxWidth: 900, background: '#0f172a', border: '1px solid #38bdf8', borderRadius: 16, padding: 24, maxHeight: '85vh', display: 'flex', flexDirection: 'column', boxShadow: '0 25px 90px rgba(0,0,0,0.95)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 14 }}>
              <div>
                <h3 style={{ fontSize: 17, fontWeight: 900, color: 'white', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span>🛡️</span> LIVE INTRUDER & VISITOR ACCESS LOGS
                </h3>
                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  {(['ALL', 'BLOCKED', 'AUTHORIZED'] as const).map((f) => (
                    <button
                      key={f}
                      onClick={() => setLogFilter(f)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: 6,
                        border: 'none',
                        background: logFilter === f ? (f === 'BLOCKED' ? '#ef4444' : f === 'AUTHORIZED' ? '#10b981' : '#38bdf8') : '#1e293b',
                        color: 'white',
                        fontSize: 10.5,
                        fontWeight: 800,
                        cursor: 'pointer'
                      }}
                    >
                      {f === 'ALL' ? 'All Records' : f === 'BLOCKED' ? '🚨 Blocked Intruders' : '✓ Authorized Access'}
                    </button>
                  ))}
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={handleClearAllLogs} style={{ background: '#7f1d1d', border: '1px solid #ef4444', color: 'white', padding: '6px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 11, fontWeight: 700 }}>🗑️ Clear All</button>
                <button onClick={() => setAuditModalOpen(false)} style={{ background: '#334155', border: 'none', color: 'white', padding: '6px 12px', borderRadius: 6, cursor: 'pointer' }}>✕ Close</button>
              </div>
            </div>

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
                  {filteredLogs.map((log: any, idx: number) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #1e293b' }}>
                      <td style={{ padding: '10px', color: '#94a3b8', fontFamily: 'monospace' }}>{log.timestamp}</td>
                      <td style={{ padding: '10px', color: 'white', fontWeight: 700 }}>{log.ip}</td>
                      <td style={{ padding: '10px', color: '#cbd5e1' }}>{log.device}</td>
                      <td style={{ padding: '10px' }}>
                        <span style={{ padding: '3px 8px', borderRadius: 4, background: log.status.includes('AUTHORIZED') ? '#065f46' : '#7f1d1d', color: 'white', fontWeight: 800, fontSize: 10 }}>
                          {log.status}
                        </span>
                      </td>
                      <td style={{ padding: '10px' }}>
                        {log.photo ? (
                          <img
                            src={log.photo}
                            alt="Intruder"
                            onClick={() => setSelectedIntruder(log)}
                            style={{ width: 44, height: 44, borderRadius: 8, objectFit: 'cover', border: '2px solid #ef4444', cursor: 'pointer', boxShadow: '0 0 10px rgba(239,68,68,0.5)' }}
                          />
                        ) : (
                          <span style={{ color: '#64748b', fontSize: 10 }}>No Photo</span>
                        )}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'center' }}>
                        <button
                          onClick={(e) => handleDeleteSingleLog(log, e)}
                          title="Delete this record"
                          style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#f87171', padding: '4px 8px', borderRadius: 6, cursor: 'pointer', fontSize: 12 }}
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* INTRUDER MUGSHOT MODAL */}
      {selectedIntruder && (
        <div onClick={() => setSelectedIntruder(null)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.92)', zIndex: 4000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div onClick={(e) => e.stopPropagation()} style={{ width: '90vw', maxWidth: 420, background: '#0f172a', border: '2px solid #ef4444', borderRadius: 16, padding: 24, textAlign: 'center' }}>
            <h3 style={{ color: '#ef4444', fontSize: 16, fontWeight: 900 }}>🚨 INTRUDER MUGSHOT CAPTURED</h3>
            <img src={selectedIntruder.photo} alt="Intruder Mugshot" style={{ width: 220, height: 220, borderRadius: 12, objectFit: 'cover', border: '2px solid #ef4444', margin: '14px auto', display: 'block', boxShadow: '0 0 30px rgba(239,68,68,0.6)' }} />
            <div style={{ textAlign: 'left', background: '#020617', padding: 12, borderRadius: 8, fontSize: 11.5, color: '#cbd5e1', display: 'flex', flexDirection: 'column', gap: 4 }}>
              <div><b>Time:</b> {selectedIntruder.timestamp}</div>
              <div><b>IP:</b> <span style={{ color: '#38bdf8', fontWeight: 700 }}>{selectedIntruder.ip}</span></div>
              <div><b>Device:</b> {selectedIntruder.device}</div>
              <div><b>Action:</b> <span style={{ color: '#ef4444', fontWeight: 800 }}>{selectedIntruder.action}</span></div>
            </div>
            <button onClick={() => setSelectedIntruder(null)} style={{ width: '100%', padding: '10px', borderRadius: 8, background: '#ef4444', color: 'white', border: 'none', fontWeight: 800, marginTop: 14, cursor: 'pointer' }}>Close Intruder Dossier</button>
          </div>
        </div>
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
    </div>
  )
}
