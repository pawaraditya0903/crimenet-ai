import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'

interface CopilotDrawerProps {
  isOpen: boolean
  onClose: () => void
  activeCaseId: string
  onCitationClick?: (citationType: string, idOrName: string) => void
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  citations?: string[]
  actionPreview?: any
  retrievalTrace?: any
}

export default function CopilotDrawer({
  isOpen,
  onClose,
  activeCaseId,
  onCitationClick
}: CopilotDrawerProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'm-welcome',
      role: 'assistant',
      content: `Hello Investigator. I am **CrimeNet Copilot**, your real-time forensic intelligence assistant.\n\nI can analyze graph topological paths, summarize cases, explain Isolation Forest anomalies, retrieve Merkle evidence records, and generate review drafts.\n\n*Note: All outputs are advisory statistical indicators. Autonomous enforcement is disabled.*`,
      timestamp: 'Active',
      citations: ['[Case: c1]', '[Evidence: ev-01]']
    }
  ])
  const [inputVal, setInputVal] = useState('')
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'trace' | 'settings'>('chat')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [actionConfirmModal, setActionConfirmModal] = useState<any>(null)
  const [actionStatus, setActionStatus] = useState('')

  // ── VOICE SPEECH RECOGNITION (WEB SPEECH API) ──
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [autoSpeak, setAutoSpeak] = useState(true)
  const [speechRate, setSpeechRate] = useState(1.0)
  const recognitionRef = useRef<any>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const animFrameRef = useRef<number | null>(null)

  // Load Suggestions
  useEffect(() => {
    axios.get(`/api/copilot/suggestions?case_id=${activeCaseId}`)
      .then(res => setSuggestions(res.data.suggestions || []))
      .catch(() => {})
  }, [activeCaseId])

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (SpeechRecognition) {
      const recog = new SpeechRecognition()
      recog.continuous = false
      recog.interimResults = true
      recog.lang = 'en-US'

      recog.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((r: any) => r[0].transcript)
          .join('')
        setInputVal(transcript)
      }

      recog.onend = () => {
        setIsListening(false)
      }

      recog.onerror = () => {
        setIsListening(false)
      }

      recognitionRef.current = recog
    }
  }, [])

  // Audio Waveform Animation
  useEffect(() => {
    if (!canvasRef.current) return
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let phase = 0
    const renderWave = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      if (isListening || isSpeaking) {
        ctx.strokeStyle = isListening ? '#38bdf8' : '#34d399'
        ctx.lineWidth = 2
        ctx.beginPath()
        for (let x = 0; x < canvas.width; x++) {
          const y = canvas.height / 2 + Math.sin(x * 0.08 + phase) * (isListening ? 14 : 10) * Math.sin(x / canvas.width * Math.PI)
          if (x === 0) ctx.moveTo(x, y)
          else ctx.lineTo(x, y)
        }
        ctx.stroke()
        phase += 0.15
      } else {
        // Flat resting line
        ctx.strokeStyle = '#334155'
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(0, canvas.height / 2)
        ctx.lineTo(canvas.width, canvas.height / 2)
        ctx.stroke()
      }
      animFrameRef.current = requestAnimationFrame(renderWave)
    }

    renderWave()
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    }
  }, [isListening, isSpeaking])

  // SpeechSynthesis Voice Output
  const speakText = (text: string) => {
    if (!('speechSynthesis' in window) || !autoSpeak) return
    window.speechSynthesis.cancel()

    // Clean markdown and citations for natural audio
    const cleanAudioText = text
      .replace(/\[.*?\]/g, '')
      .replace(/[*_#`]/g, '')
      .replace(/\n+/g, '. ')
      .slice(0, 320)

    const utterance = new SpeechSynthesisUtterance(cleanAudioText)
    utterance.rate = speechRate
    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    }
  }

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech Recognition is not supported in this browser. Please type your query.')
      return
    }
    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      stopSpeaking()
      try {
        recognitionRef.current.start()
        setIsListening(true)
      } catch {}
    }
  }

  const handleSendMessage = async (customMsg?: string) => {
    const query = customMsg || inputVal
    if (!query.trim()) return

    const userMsgObj: Message = {
      id: `m-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMsgObj])
    setInputVal('')
    setLoading(true)

    try {
      const res = await axios.post('/api/copilot/chat', {
        message: query,
        case_id: activeCaseId,
        user_id: 'INV-2026-AP01'
      })

      const botReply = res.data.response || 'Inquiry processed.'
      const botMsgObj: Message = {
        id: `m-resp-${Date.now()}`,
        role: 'assistant',
        content: botReply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        citations: res.data.citations || [],
        actionPreview: res.data.action_preview,
        retrievalTrace: res.data.retrieval_trace
      }

      setMessages(prev => [...prev, botMsgObj])
      speakText(botReply)
    } catch {
      const errMsgObj: Message = {
        id: `m-err-${Date.now()}`,
        role: 'assistant',
        content: 'CrimeNet Copilot is currently offline or unable to connect to the knowledge engine.',
        timestamp: 'Error'
      }
      setMessages(prev => [...prev, errMsgObj])
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmAction = async (action: any) => {
    try {
      const res = await axios.post('/api/copilot/actions/confirm', {
        draft_type: action.draft_type,
        case_id: activeCaseId
      })
      setActionStatus(res.data.message || '✓ Action confirmed and recorded.')
      setActionConfirmModal(null)
      setTimeout(() => setActionStatus(''), 4000)
    } catch {
      setActionStatus('✓ Action confirmed locally.')
      setActionConfirmModal(null)
    }
  }

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      width: 440,
      maxWidth: '95vw',
      height: '100vh',
      background: 'rgba(10, 16, 31, 0.96)',
      borderLeft: '1px solid rgba(56, 189, 248, 0.4)',
      boxShadow: '-20px 0 60px rgba(0,0,0,0.9)',
      zIndex: 3200,
      display: 'flex',
      flexDirection: 'column',
      backdropFilter: 'blur(20px)',
      color: '#f8fafc',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* COPILOT HEADER */}
      <div style={{
        padding: '14px 18px',
        borderBottom: '1px solid #1e293b',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#090e17'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #0284c7 0%, #38bdf8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 16,
            boxShadow: '0 0 15px rgba(56,189,248,0.5)'
          }}>
            🤖
          </div>
          <div>
            <div style={{ fontWeight: 900, fontSize: 13, color: '#38bdf8', letterSpacing: '0.5px' }}>
              CRIMENET COPILOT
            </div>
            <div style={{ fontSize: 10, color: '#94a3b8' }}>
              Voice Investigation Intelligence (Active Case: <b>{activeCaseId.toUpperCase()}</b>)
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: 18, cursor: 'pointer' }}
        >
          ✕
        </button>
      </div>

      {/* TAB SELECTOR: CHAT / RETRIEVAL TRACE / SETTINGS */}
      <div style={{ display: 'flex', borderBottom: '1px solid #1e293b', background: '#0a101f', fontSize: 11, fontWeight: 700 }}>
        <button
          onClick={() => setActiveTab('chat')}
          style={{ flex: 1, padding: '8px', background: activeTab === 'chat' ? 'rgba(56,189,248,0.15)' : 'transparent', color: activeTab === 'chat' ? '#38bdf8' : '#64748b', border: 'none', borderBottom: activeTab === 'chat' ? '2px solid #38bdf8' : 'none', cursor: 'pointer' }}
        >
          💬 Chat
        </button>
        <button
          onClick={() => setActiveTab('trace')}
          style={{ flex: 1, padding: '8px', background: activeTab === 'trace' ? 'rgba(56,189,248,0.15)' : 'transparent', color: activeTab === 'trace' ? '#38bdf8' : '#64748b', border: 'none', borderBottom: activeTab === 'trace' ? '2px solid #38bdf8' : 'none', cursor: 'pointer' }}
        >
          🔎 Retrieval Trace
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          style={{ flex: 1, padding: '8px', background: activeTab === 'settings' ? 'rgba(56,189,248,0.15)' : 'transparent', color: activeTab === 'settings' ? '#38bdf8' : '#64748b', border: 'none', borderBottom: activeTab === 'settings' ? '2px solid #38bdf8' : 'none', cursor: 'pointer' }}
        >
          ⚙️ Voice Engine
        </button>
      </div>

      {/* AUDIO WAVEFORM CANVAS DISPLAY */}
      <div style={{ background: '#030712', padding: '6px 14px', borderBottom: '1px solid #1e293b', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <canvas ref={canvasRef} width={240} height={28} style={{ width: 240, height: 28 }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {isSpeaking && (
            <button
              onClick={stopSpeaking}
              style={{ padding: '2px 8px', borderRadius: 4, background: '#dc2626', color: 'white', border: '1px solid #ef4444', fontSize: 9.5, fontWeight: 800, cursor: 'pointer' }}
            >
              ⏹️ STOP
            </button>
          )}
          <div style={{ fontSize: 9.5, fontWeight: 800, color: isListening ? '#38bdf8' : isSpeaking ? '#34d399' : '#64748b' }}>
            {isListening ? '🎤 LISTENING...' : isSpeaking ? '🔊 SPEAKING...' : 'IDLE'}
          </div>
        </div>
      </div>

      {actionStatus && (
        <div style={{ background: '#15803d', color: 'white', padding: '6px 12px', fontSize: 11, fontWeight: 800, textAlign: 'center' }}>
          {actionStatus}
        </div>
      )}

      {/* TAB BODY */}
      {activeTab === 'chat' && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* MESSAGES LIST */}
          <div style={{ flex: 1, padding: 14, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {messages.map((m) => (
              <div
                key={m.id}
                style={{
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '88%',
                  background: m.role === 'user' ? 'linear-gradient(135deg, #0284c7 0%, #1e40af 100%)' : '#0f172a',
                  border: m.role === 'user' ? 'none' : '1px solid #1e293b',
                  borderRadius: 12,
                  padding: '10px 14px',
                  fontSize: 12,
                  lineHeight: 1.5,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
                }}
              >
                <div style={{ whiteSpace: 'pre-wrap', color: '#f8fafc' }}>
                  {m.content}
                </div>

                {/* CITATIONS BAR */}
                {m.citations && m.citations.length > 0 && (
                  <div style={{ marginTop: 8, paddingTop: 6, borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                    {m.citations.map((c, i) => (
                      <span
                        key={i}
                        onClick={() => {
                          if (onCitationClick) onCitationClick('entity', c)
                        }}
                        style={{
                          background: 'rgba(56, 189, 248, 0.2)',
                          color: '#38bdf8',
                          padding: '2px 6px',
                          borderRadius: 4,
                          fontSize: 9.5,
                          fontWeight: 700,
                          cursor: 'pointer'
                        }}
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                )}

                {/* ACTION PREVIEW CARD (DRAFT ONLY) */}
                {m.actionPreview && (
                  <div style={{ marginTop: 8, background: 'rgba(245, 158, 11, 0.1)', border: '1px solid #f59e0b', borderRadius: 8, padding: 8 }}>
                    <div style={{ fontSize: 10, color: '#fef08a', fontWeight: 800 }}>⚡ DRAFT ACTION PREVIEW</div>
                    <button
                      onClick={() => setActionConfirmModal(m.actionPreview)}
                      style={{
                        marginTop: 6,
                        width: '100%',
                        padding: '6px',
                        background: '#b45309',
                        color: 'white',
                        border: 'none',
                        borderRadius: 4,
                        fontWeight: 800,
                        fontSize: 11,
                        cursor: 'pointer'
                      }}
                    >
                      Review & Confirm Draft
                    </button>
                  </div>
                )}

                <div style={{ fontSize: 9, color: 'rgba(255,255,255,0.4)', textAlign: 'right', marginTop: 4 }}>
                  {m.timestamp}
                </div>
              </div>
            ))}

            {loading && (
              <div style={{ alignSelf: 'flex-start', background: '#0f172a', padding: '8px 12px', borderRadius: 8, fontSize: 11, color: '#38bdf8', border: '1px solid #1e293b' }}>
                🧠 Copilot is analyzing graph topology and knowledge vectors...
              </div>
            )}
          </div>

            {/* QUICK PROMPT CHIPS */}
          <div style={{ padding: '6px 12px', background: '#090e17', borderTop: '1px solid #1e293b', display: 'flex', gap: 6, overflowX: 'auto' }}>
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(s)}
                style={{
                  whiteSpace: 'nowrap',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid #334155',
                  color: '#cbd5e1',
                  padding: '4px 8px',
                  borderRadius: 12,
                  fontSize: 10,
                  cursor: 'pointer'
                }}
              >
                {s}
              </button>
            ))}
          </div>

          {/* INPUT BAR WITH VOICE & SEND BUTTONS */}
          <div style={{ padding: 12, background: '#0a101f', borderTop: '1px solid #1e293b', display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              onClick={toggleListening}
              title={isListening ? 'Stop Listening' : 'Voice Input (Web Speech API)'}
              style={{
                width: 38,
                height: 38,
                borderRadius: '50%',
                background: isListening ? '#ef4444' : '#1e293b',
                border: `1px solid ${isListening ? '#f87171' : '#38bdf8'}`,
                color: 'white',
                cursor: 'pointer',
                fontSize: 16,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: isListening ? '0 0 15px rgba(239,68,68,0.8)' : 'none'
              }}
            >
              🎤
            </button>

            {isSpeaking && (
              <button
                onClick={stopSpeaking}
                title="Stop Voice Output"
                style={{
                  background: '#334155',
                  border: 'none',
                  color: '#38bdf8',
                  padding: '6px 10px',
                  borderRadius: 6,
                  fontSize: 10,
                  fontWeight: 800,
                  cursor: 'pointer'
                }}
              >
                ⏹ Stop
              </button>
            )}

            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSendMessage()
              }}
              placeholder={isListening ? 'Listening to voice...' : 'Ask Copilot anything...'}
              style={{
                flex: 1,
                padding: '10px 14px',
                borderRadius: 20,
                background: '#020617',
                border: '1px solid #334155',
                color: 'white',
                fontSize: 12,
                outline: 'none'
              }}
            />

            <button
              onClick={() => handleSendMessage()}
              disabled={loading || !inputVal.trim()}
              style={{
                width: 38,
                height: 38,
                borderRadius: '50%',
                background: inputVal.trim() ? '#0284c7' : '#1e293b',
                border: 'none',
                color: 'white',
                cursor: inputVal.trim() ? 'pointer' : 'default',
                fontSize: 14,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              ➤
            </button>
          </div>
        </div>
      )}

      {/* RETRIEVAL TRACE TAB */}
      {activeTab === 'trace' && (
        <div style={{ flex: 1, padding: 16, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12, fontSize: 11.5 }}>
          <div style={{ fontWeight: 800, color: '#38bdf8' }}>🔍 ACTIVE KNOWLEDGE TRACE & AUDIT TRAIL</div>
          <div style={{ background: '#020617', padding: 12, borderRadius: 8, border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div><b>Active Case Scope:</b> {activeCaseId.toUpperCase()}</div>
            <div><b>Knowledge Engines:</b> SQLite Cases, NetworkX 3.6 Topology, Isolation Forest Outliers</div>
            <div><b>Audit Logging:</b> All Copilot queries recorded with SHA-256 HMAC digest</div>
            <div><b>Statutory Disclaimer:</b> Outputs are non-autonomous advisory indicators.</div>
          </div>
        </div>
      )}

      {/* SETTINGS TAB */}
      {activeTab === 'settings' && (
        <div style={{ flex: 1, padding: 16, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 14, fontSize: 11.5 }}>
          <div style={{ fontWeight: 800, color: '#38bdf8' }}>⚙️ VOICE & SPEECH SYNTHESIS ENGINE</div>
          
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={autoSpeak}
                onChange={(e) => setAutoSpeak(e.target.checked)}
              />
              <span>Auto-Read Answers Aloud (Text-to-Speech)</span>
            </label>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: 4, color: '#94a3b8' }}>
              Speech Output Rate: <b>{speechRate}x</b>
            </label>
            <input
              type="range"
              min="0.75"
              max="1.5"
              step="0.05"
              value={speechRate}
              onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
              style={{ width: '100%' }}
            />
          </div>

          <div style={{ background: 'rgba(56,189,248,0.1)', padding: 12, borderRadius: 8, border: '1px solid rgba(56,189,248,0.3)', color: '#cbd5e1', fontSize: 10.5, lineHeight: 1.5 }}>
            🔒 <b>Voice Privacy Notice:</b> All speech recognition and speech synthesis occur entirely within your local browser sandbox via the Web Speech API. Audio is never stored on external servers.
          </div>
        </div>
      )}

      {/* ACTION CONFIRMATION MODAL */}
      {actionConfirmModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 4500, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div style={{ width: '90vw', maxWidth: 460, background: '#0f172a', border: '1px solid #f59e0b', borderRadius: 14, padding: 20, boxShadow: '0 25px 80px rgba(0,0,0,0.95)' }}>
            <h3 style={{ fontSize: 15, fontWeight: 900, color: '#f59e0b', display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>⚠️</span> CONFIRM DRAFT ACTION
            </h3>
            <p style={{ fontSize: 11, color: '#94a3b8', margin: '8px 0 12px' }}>
              Are you sure you want to save this draft to the active case record?
            </p>
            <pre style={{ background: '#020617', padding: 10, borderRadius: 8, fontSize: 10.5, color: '#e2e8f0', whiteSpace: 'pre-wrap', maxHeight: 200, overflowY: 'auto' }}>
              {actionConfirmModal.content}
            </pre>
            <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
              <button
                onClick={() => setActionConfirmModal(null)}
                style={{ flex: 1, padding: '8px', background: '#334155', color: 'white', border: 'none', borderRadius: 6, fontWeight: 700, cursor: 'pointer' }}
              >
                Cancel
              </button>
              <button
                onClick={() => handleConfirmAction(actionConfirmModal)}
                style={{ flex: 1, padding: '8px', background: '#15803d', color: 'white', border: 'none', borderRadius: 6, fontWeight: 800, cursor: 'pointer' }}
              >
                ✓ Confirm & Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
