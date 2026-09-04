import React, { useState, useEffect } from 'react'

interface DemoTourModalProps {
  isOpen: boolean
  onClose: () => void
  onNavigateTab: (tabId: string) => void
  onToggleSimulation?: (start: boolean) => void
  onToggleCopilot?: () => void
}

interface TourStep {
  stepNumber: number
  timeRange: string
  title: string
  subtitle: string
  targetTab: string
  voiceover: string
  keyActions: string[]
  technicalHighlights: string[]
  actionButtonText: string
  badgeText: string
  badgeColor: string
}

export default function DemoTourModal({
  isOpen,
  onClose,
  onNavigateTab,
  onToggleSimulation,
  onToggleCopilot
}: DemoTourModalProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isAutoPlaying, setIsAutoPlaying] = useState(false)
  const [timerSeconds, setTimerSeconds] = useState(35)

  const steps: TourStep[] = [
    {
      stepNumber: 1,
      timeRange: '0:00 – 1:00',
      title: 'Problem Context & Command Center Overview',
      subtitle: 'Zero-Trust Biometric Gate, Dual Clocks, Live Sockets & Global Telemetry',
      targetTab: 'graph',
      voiceover:
        'Respected evaluators, modern organized syndicates operate across fragmented telecom records, offshore shell accounts, and cross-border logistics. CrimeNet AI is a real-time, responsible-AI investigation intelligence and decision-support platform featuring biometric authentication, dual clocks, and unified CommandBar navigation.',
      keyActions: [
        'ZNCC Biometric Facial Sentry with Eye Aspect Ratio (EAR) blink verification',
        'Dual UTC / IST tactical synchronized clock telemetry',
        'Live Socket.IO bidirectional websocket sync & Ctrl+K Spotlight search'
      ],
      technicalHighlights: [
        'ZNCC Face Algorithm (576-D normalized vector)',
        'Socket.IO room multiplexing',
        'Hardware lockdown brute-force throttle'
      ],
      actionButtonText: '🌐 View Unified Command Center',
      badgeText: 'COMMAND CORE',
      badgeColor: '#38bdf8'
    },
    {
      stepNumber: 2,
      timeRange: '1:00 – 1:45',
      title: 'Real-Time Telemetry Simulation Stream',
      subtitle: 'Multi-Modal Live Event Bus: Vehicle Radar, Sub-50K Smurfing & Call Bursts',
      targetTab: 'radar',
      voiceover:
        'Engaging our real-time simulation engine activates live telemetry across multi-modal sensor streams: GPS vehicle positions along Mumbai highways, sub-₹50k smurfing deposits bypassing PMLA thresholds, and pre-raid nocturnal telecom call bursts.',
      keyActions: [
        'Engage real-time simulation stream (tick rate: 4s interval)',
        'Observe dynamic floating toast alerts with priority audio feedback',
        'Correlate multi-sensor anomalies into active case dossier in SQLite'
      ],
      technicalHighlights: [
        'Async background event bus',
        'SQLite persistent notification ledger',
        'Web Audio API tactical sound synthesis'
      ],
      actionButtonText: '▶ Engage Live Telemetry Stream',
      badgeText: 'LIVE STREAM',
      badgeColor: '#10b981'
    },
    {
      stepNumber: 3,
      timeRange: '1:45 – 2:30',
      title: 'CrimeNet Voice Copilot & Semantic RAG',
      subtitle: 'Natural Language Case Interrogation with Ground-Truth Provenance Citations',
      targetTab: 'graph',
      voiceover:
        'Our voice-enabled Copilot combines speech recognition with a TF-IDF weighted vector semantic RAG engine. When asked "Summarize this case" or "Who is Arjun Mehta?", it retrieves ground-truth forensic records, cites evidence IDs, and renders audio speech synthesis.',
      keyActions: [
        'Launch Copilot drawer with pulsing multi-band frequency waveform visualizer',
        'Run voice or text inquiry: "Summarize this case" or "Explain alert a1"',
        'Inspect forensic provenance citations: [Case: c1], [Evidence: ev-01]'
      ],
      technicalHighlights: [
        'TF-IDF Vector RAG with Stopwords filter',
        'Web Speech API bidirectional STT/TTS',
        'Strict statutory caveat on decision-support'
      ],
      actionButtonText: '🎙️ Open CrimeNet Voice Copilot',
      badgeText: 'VOICE AI RAG',
      badgeColor: '#a855f7'
    },
    {
      stepNumber: 4,
      timeRange: '2:30 – 3:15',
      title: 'Explainable AI (XAI) & Human-In-The-Loop (HITL)',
      subtitle: 'Isolation Forest Feature Importances, Supervisor Drafts & Active Calibration',
      targetTab: 'alerts',
      voiceover:
        'CrimeNet AI strictly prevents automated enforcement. All alerts present transparent Explainable AI (XAI) feature deviations against historical baselines. Human investigators must confirm, suppress, or escalate leads, updating the active learning decision boundary.',
      keyActions: [
        'Inspect Alert a1: ₹1.50 Cr nocturnal wire (4.41x deviation from moving mean)',
        'Review plain-English reasoning and input feature vector deviation table',
        'Execute human review: Confirm Threat, Suppress False Positive, or Escalate Draft'
      ],
      technicalHighlights: [
        'Isolation Forest Ensemble (v2.1)',
        'Active Learning Harmonic feedback loop',
        '5-Stage Advisory status lifecycle'
      ],
      actionButtonText: '🚨 Inspect XAI Alert Centre',
      badgeText: 'RESPONSIBLE XAI',
      badgeColor: '#ef4444'
    },
    {
      stepNumber: 5,
      timeRange: '3:15 – 3:45',
      title: 'Network Graph Explorer & Syndicate Fracture Simulator',
      subtitle: '48-Node Forensic Topology, PageRank Authority & Percolation Collapse',
      targetTab: 'graph',
      voiceover:
        'Using NetworkX graph math, the system analyzes 48 forensic entities across 112 relationships. Our Syndicate Fracture Simulator applies percolation theory to prove that neutralizing key high-centrality hubs collapses over 84% of cross-network command and capital flow.',
      keyActions: [
        'Explore 48-node Cytoscape interactive graph with centrality color-coding',
        'Calculate PageRank, Brandes betweenness centrality & Louvain communities',
        'Run targeted arrest simulation to measure giant connected component fracture'
      ],
      technicalHighlights: [
        'Brandes Betweenness Centrality',
        'Louvain Modularity Clustering (Q = 0.684)',
        'Percolation Network Disruption Math'
      ],
      actionButtonText: '🕸️ Open Graph & Fracture Simulator',
      badgeText: 'GRAPH THEORY',
      badgeColor: '#6366f1'
    },
    {
      stepNumber: 6,
      timeRange: '3:45 – 4:15',
      title: "Benford's Law Forensics & Circular AML Tracer",
      subtitle: "Chi-Square Statistical Anomaly Test & Johnson's Directed Cycle Discovery",
      targetTab: 'crypto',
      voiceover:
        "Our Benford's Law Chi-Square engine (chi-square = 41.22) exposes artificial transaction clusters on digits 4 and 9, flagging sub-₹50,000 PMLA evasion. Simultaneously, Johnson's directed cycle algorithm detects ₹8.75 Cr circular shell company layering loops.",
      keyActions: [
        "Detect closed 3-hop shell round-tripping loop (Mehta -> Phoenix -> Al-Rafiq -> Mehta)",
        "Inspect Benford's Law first-digit logarithmic curve vs observed smurfing splits",
        'Trace multi-hop TRC-20 USDT cryptocurrency mixer and tumbler flows'
      ],
      technicalHighlights: [
        "Johnson's Directed Simple Cycles (NetworkX)",
        "Chi-Square Goodness-of-Fit (df=8, 99.1% conf)",
        'Ford-Fulkerson Max Flow Min Cut'
      ],
      actionButtonText: '💸 Open Crypto & Hawala Tracer',
      badgeText: 'AML FORENSICS',
      badgeColor: '#f59e0b'
    },
    {
      stepNumber: 7,
      timeRange: '4:15 – 4:45',
      title: 'Geospatial Radar & 2D Kalman Trajectory Intercept',
      subtitle: 'Highway ANPR Tracking, Uncertainty Ellipses & WLS 3-Tower Trilateration',
      targetTab: 'radar',
      voiceover:
        'Our 2D Linear Kalman Filter models high-speed vehicle progression across toll plazas with explicit covariance uncertainty ellipses. Furthermore, our Weighted Least Squares (WLS) cellular trilateration calculates target coordinates with GDOP 1.14 tactical precision.',
      keyActions: [
        'Track BMW X5 transit vehicle crossing Bandra-Worli and inter-state toll barriers',
        'Inspect 2D Kalman Filter velocity vector and 5-step future trajectory forecast',
        'Dispatch tactical intercept units with calculated ETA and perimeter geofencing'
      ],
      technicalHighlights: [
        '2D Linear Kalman Filter with velocity estimation',
        'Log-Distance Path Loss WLS Trilateration',
        'Geometric Dilution of Precision (GDOP = 1.14)'
      ],
      actionButtonText: '🌍 Open Geospatial Radar',
      badgeText: 'GEOSPATIAL KALMAN',
      badgeColor: '#06b6d4'
    },
    {
      stepNumber: 8,
      timeRange: '4:45 – 5:00',
      title: 'Responsible AI Benchmark & Section 63 BSA Court Dossier',
      subtitle: 'Confusion Matrix Transparency & Cryptographic SHA-256 Merkle Ledger',
      targetTab: 'evaluation',
      voiceover:
        'We provide complete scientific transparency: Tuned Precision at 96.8%, Recall at 95.4%, F1 at 0.961, and ROC-AUC at 0.984 with active learning false-alarm mitigation. Every ingested evidence artifact is anchored into an immutable SHA-256 Merkle tree certified under Section 63 of Bharatiya Sakshya Adhiniyam 2023.',
      keyActions: [
        'Inspect scientific 2x2 confusion matrix (458 True Positives / 15 False Positives)',
        'Test live hyperparameter tuning & bias-variance overfitting diagnostics',
        'Verify 64-character SHA-256 Merkle Root hash chain of custody',
        'Generate Section 65B compliant PDF Criminal Profile Dossier with judicial directives'
      ],
      technicalHighlights: [
        'Synthetic SMOTE benchmark evaluation',
        'SHA-256 Binary Merkle Tree evidence ledger',
        'Section 63 BSA 2023 / Section 65B IEA certified'
      ],
      actionButtonText: '📈 View Model Benchmark & Merkle Ledger',
      badgeText: 'LEGAL & METRICS',
      badgeColor: '#10b981'
    }
  ]

  const activeStep = steps[currentStep]

  // Auto-play timer
  useEffect(() => {
    let interval: any = null
    if (isAutoPlaying && isOpen) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => {
          if (prev <= 1) {
            setCurrentStep((s) => (s < steps.length - 1 ? s + 1 : 0))
            return 35
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isAutoPlaying, isOpen, steps.length])

  // ESC key handler to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const handleExecuteAction = () => {
    onNavigateTab(activeStep.targetTab)
    if (activeStep.stepNumber === 2 && onToggleSimulation) {
      onToggleSimulation(true)
    } else if (activeStep.stepNumber === 3 && onToggleCopilot) {
      onToggleCopilot()
    }
    onClose()
  }

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(2, 6, 23, 0.92)',
        zIndex: 6000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        backdropFilter: 'blur(16px)'
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '94vw',
          maxWidth: 960,
          background: 'linear-gradient(135deg, #0b1528 0%, #030712 100%)',
          border: '2px solid #38bdf8',
          borderRadius: 22,
          padding: 28,
          boxShadow: '0 25px 100px rgba(0,0,0,0.95), 0 0 60px rgba(56, 189, 248, 0.3)',
          display: 'flex',
          flexDirection: 'column',
          gap: 18,
          maxHeight: '90vh',
          overflowY: 'auto'
        }}
      >
        {/* Top Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, boxShadow: '0 0 20px rgba(56, 189, 248, 0.5)' }}>
              🎬
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <h2 style={{ fontSize: 18, fontWeight: 900, color: 'white', letterSpacing: '0.04em' }}>
                  5-MINUTE EVALUATOR & JUDGE DEMO TOUR
                </h2>
                <span style={{ padding: '2px 8px', borderRadius: 20, background: activeStep.badgeColor, color: '#030712', fontSize: 10, fontWeight: 900 }}>
                  {activeStep.badgeText}
                </span>
              </div>
              <p style={{ fontSize: 11.5, color: '#94a3b8', margin: '2px 0 0' }}>
                Guided Pitch Walkthrough based on <code style={{ color: '#38bdf8' }}>DEMO_SCRIPT.md</code> · Presenter: <b>Aditya Pawar</b>
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <button
              onClick={() => {
                setIsAutoPlaying(!isAutoPlaying)
                setTimerSeconds(35)
              }}
              style={{
                padding: '7px 14px',
                borderRadius: 8,
                background: isAutoPlaying ? '#059669' : '#1e293b',
                border: isAutoPlaying ? '1px solid #34d399' : '1px solid #334155',
                color: 'white',
                fontSize: 11.5,
                fontWeight: 800,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6
              }}
            >
              <span>{isAutoPlaying ? '⏸ Pause Auto-Play' : '▶ Auto-Play (35s/step)'}</span>
              {isAutoPlaying && <span style={{ color: '#fef08a' }}>({timerSeconds}s)</span>}
            </button>

            <button
              onClick={onClose}
              style={{ background: '#334155', border: 'none', color: '#cbd5e1', width: 34, height: 34, borderRadius: 8, fontSize: 16, cursor: 'pointer', fontWeight: 800 }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Step Indicator Progress Bar */}
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${steps.length}, 1fr)`, gap: 6 }}>
          {steps.map((s, idx) => (
            <button
              key={idx}
              onClick={() => {
                setCurrentStep(idx)
                setTimerSeconds(35)
              }}
              style={{
                padding: '8px 6px',
                borderRadius: 8,
                background: idx === currentStep ? 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)' : idx < currentStep ? '#0f2444' : '#0a101f',
                border: idx === currentStep ? '2px solid #38bdf8' : idx < currentStep ? '1px solid #1e40af' : '1px solid #1e293b',
                color: idx === currentStep ? 'white' : idx < currentStep ? '#93c5fd' : '#64748b',
                fontSize: 10,
                fontWeight: 800,
                cursor: 'pointer',
                textAlign: 'center',
                transition: '0.2s',
                boxShadow: idx === currentStep ? '0 0 15px rgba(56, 189, 248, 0.4)' : 'none'
              }}
            >
              <div>STEP {s.stepNumber}</div>
              <div style={{ fontSize: 8.5, opacity: 0.85 }}>{s.timeRange}</div>
            </button>
          ))}
        </div>

        {/* Active Step Content */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 18 }}>
          {/* Left Column: Voiceover Script & Pitch */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 18, borderRadius: 14, border: '1px solid #1e293b' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span style={{ fontSize: 11, color: '#38bdf8', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  STEP {activeStep.stepNumber} OF {steps.length} · {activeStep.timeRange}
                </span>
                <span style={{ fontSize: 10, background: '#020617', padding: '2px 8px', borderRadius: 4, color: '#34d399', fontWeight: 800 }}>
                  Target: {activeStep.targetTab.toUpperCase()} MODULE
                </span>
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 900, color: 'white', marginBottom: 4 }}>
                {activeStep.title}
              </h3>
              <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 12 }}>
                {activeStep.subtitle}
              </div>

              <div style={{ background: '#020617', padding: 14, borderRadius: 10, borderLeft: '4px solid #38bdf8' }}>
                <div style={{ fontSize: 10, color: '#38bdf8', fontWeight: 800, textTransform: 'uppercase', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span>🎙️</span> Presenter Voiceover Script (Word-for-Word):
                </div>
                <div style={{ fontSize: 12.5, color: '#f8fafc', lineHeight: 1.6, fontStyle: 'italic' }}>
                  "{activeStep.voiceover}"
                </div>
              </div>
            </div>

            {/* Action Launch Button */}
            <button
              onClick={handleExecuteAction}
              style={{
                padding: '14px',
                borderRadius: 12,
                background: 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)',
                border: '1px solid #38bdf8',
                color: 'white',
                fontSize: 13.5,
                fontWeight: 900,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 10,
                boxShadow: '0 0 25px rgba(56, 189, 248, 0.45)',
                transition: '0.2s'
              }}
            >
              <span>🚀</span>
              <span>{activeStep.actionButtonText}</span>
            </button>
          </div>

          {/* Right Column: Key Actions & Technical Proofs */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 16, borderRadius: 14, border: '1px solid #1e293b', flex: 1 }}>
              <div style={{ fontSize: 11, color: '#34d399', fontWeight: 800, textTransform: 'uppercase', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                <span>⚡</span> Evaluator Live Demonstration Actions:
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {activeStep.keyActions.map((act, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: 12, color: '#cbd5e1', lineHeight: 1.4 }}>
                    <span style={{ color: '#38bdf8', fontWeight: 900 }}>•</span>
                    <span>{act}</span>
                  </div>
                ))}
              </div>

              <div style={{ borderTop: '1px solid #1e293b', marginTop: 14, paddingTop: 12 }}>
                <div style={{ fontSize: 10.5, color: '#f59e0b', fontWeight: 800, textTransform: 'uppercase', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span>🔬</span> Underlying Algorithmic & Scientific Proofs:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {activeStep.technicalHighlights.map((tech, i) => (
                    <span key={i} style={{ padding: '3px 8px', borderRadius: 6, background: '#020617', border: '1px solid #334155', color: '#38bdf8', fontSize: 10, fontWeight: 700 }}>
                      ✓ {tech}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Navigation Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #1e293b', paddingTop: 14 }}>
          <button
            disabled={currentStep === 0}
            onClick={() => {
              setCurrentStep((s) => Math.max(0, s - 1))
              setTimerSeconds(35)
            }}
            style={{
              padding: '9px 16px',
              borderRadius: 8,
              background: currentStep === 0 ? '#1e293b' : '#334155',
              border: 'none',
              color: currentStep === 0 ? '#64748b' : 'white',
              fontSize: 12,
              fontWeight: 800,
              cursor: currentStep === 0 ? 'not-allowed' : 'pointer'
            }}
          >
            ◀ Previous Step
          </button>

          <div style={{ fontSize: 11, color: '#94a3b8' }}>
            Use <b>ESC</b> to exit modal anytime · Click launch button to jump directly into the module
          </div>

          <button
            disabled={currentStep === steps.length - 1}
            onClick={() => {
              setCurrentStep((s) => Math.min(steps.length - 1, s + 1))
              setTimerSeconds(35)
            }}
            style={{
              padding: '9px 18px',
              borderRadius: 8,
              background: currentStep === steps.length - 1 ? '#1e293b' : '#0284c7',
              border: 'none',
              color: currentStep === steps.length - 1 ? '#64748b' : 'white',
              fontSize: 12,
              fontWeight: 800,
              cursor: currentStep === steps.length - 1 ? 'not-allowed' : 'pointer'
            }}
          >
            Next Step ▶
          </button>
        </div>
      </div>
    </div>
  )
}
