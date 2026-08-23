import { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import axios from 'axios'

export default function GraphExplorer() {
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef = useRef<cytoscape.Core | null>(null)
  const chatBottomRef = useRef<HTMLDivElement>(null)
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [chatInput, setChatInput] = useState('')
  const [isAiLoading, setIsAiLoading] = useState(false)
  const [chatMessages, setChatMessages] = useState<Array<{ sender: string; text: string }>>([
    { sender: 'ai', text: 'Hello Investigator! I am CrimeNet AI powered by Generative Intelligence on Aditya Pawar\'s Platform. You can ask me anything about suspect profiles, phone numbers, money laundering, or general questions.' }
  ])
  const [layoutMode, setLayoutMode] = useState('concentric')
  const [threatFilter, setThreatFilter] = useState(40)
  const [pathSource, setPathSource] = useState('n1')
  const [pathTarget, setPathTarget] = useState('n9')

  const elementsData = [
    { data: { id: 'n1', label: 'Arjun Mehta (Kingpin)', type: 'Person', risk: 95, color: '#ef4444', size: 65, role: 'Syndicate Mastermind' } },
    { data: { id: 'n2', label: 'Mohammed Rafiq', type: 'Person', risk: 88, color: '#f97316', size: 55, role: 'Hawala Operator' } },
    { data: { id: 'n3', label: 'Vikram Singh', type: 'Person', risk: 79, color: '#f59e0b', size: 50, role: 'Logistics Head' } },
    { data: { id: 'n4', label: 'Priya Desai', type: 'Person', risk: 74, color: '#eab308', size: 48, role: 'Financial Controller' } },
    { data: { id: 'n5', label: 'Mehta Enterprises Ltd', type: 'Organization', risk: 70, color: '#a855f7', size: 58, role: 'Primary Shell Corp' } },
    { data: { id: 'n6', label: '+91-9876543210', type: 'PhoneNumber', risk: 85, color: '#38bdf8', size: 46, role: 'Burner Line' } },
    { data: { id: 'n7', label: 'Goregaon Warehouse', type: 'Location', risk: 60, color: '#10b981', size: 52, role: 'Contraband Staging Hub' } },
    { data: { id: 'n8', label: 'BMW X5 (MH-01-AB)', type: 'Vehicle', risk: 68, color: '#6366f1', size: 45, role: 'Transport Asset' } },
    { data: { id: 'n9', label: 'Phoenix Trading LLC', type: 'Organization', risk: 82, color: '#ec4899', size: 54, role: 'Offshore Shell' } },
    
    { data: { id: 'e1', source: 'n1', target: 'n2', label: 'ASSOCIATE_OF' } },
    { data: { id: 'e2', source: 'n1', target: 'n5', label: 'OWNS' } },
    { data: { id: 'e3', source: 'n1', target: 'n6', label: 'USES_PHONE' } },
    { data: { id: 'e4', source: 'n3', target: 'n1', label: 'OPERATES_FOR' } },
    { data: { id: 'e5', source: 'n4', target: 'n5', label: 'MANAGES_FINANCES' } },
    { data: { id: 'e6', source: 'n3', target: 'n7', label: 'SPOTTED_AT' } },
    { data: { id: 'e7', source: 'n3', target: 'n8', label: 'DRIVES' } },
    { data: { id: 'e8', source: 'n5', target: 'n9', label: 'WIRE_TRANSFER_1.5CR' } },
    { data: { id: 'e9', source: 'n4', target: 'n9', label: 'AUTHORIZED_PAYMENT' } }
  ]

  useEffect(() => {
    if (!containerRef.current) return

    const cy = cytoscape({
      container: containerRef.current,
      elements: elementsData,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'background-color': 'data(color)',
            'width': 'data(size)',
            'height': 'data(size)',
            'color': '#ffffff',
            'font-size': '11px',
            'font-weight': 'bold',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'text-background-color': 'rgba(3, 7, 18, 0.85)',
            'text-background-opacity': 1,
            'text-background-padding': '3px',
            'border-width': 2,
            'border-color': '#38bdf8'
          }
        },
        {
          selector: 'edge',
          style: {
            'label': 'data(label)',
            'width': 2,
            'line-color': '#3b82f6',
            'target-arrow-color': '#3b82f6',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'font-size': '8.5px',
            'color': '#94a3b8',
            'text-background-color': 'rgba(15, 23, 42, 0.9)',
            'text-background-opacity': 1,
            'text-rotation': 'autorotate'
          }
        },
        {
          selector: '.highlighted',
          style: {
            'border-color': '#fbbf24',
            'border-width': 5,
            'line-color': '#fbbf24',
            'target-arrow-color': '#fbbf24',
            'width': 4
          }
        }
      ],
      layout: { name: 'concentric', minNodeSpacing: 60 }
    })

    cy.on('tap', 'node', (evt) => {
      const node = evt.target
      setSelectedNode(node.data())
    })

    cyRef.current = cy
    return () => cy.destroy()
  }, [])

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, isAiLoading])

  const applyLayout = (name: string) => {
    setLayoutMode(name)
    if (!cyRef.current) return

    let layoutConfig: any = { name, animate: true, animationDuration: 600 }
    if (name === 'concentric') {
      layoutConfig = {
        name: 'concentric',
        concentric: (node: any) => (node.data('id') === 'n1' ? 10 : node.data('risk')),
        levelWidth: () => 20
      }
    } else if (name === 'breadthfirst') {
      layoutConfig = { name: 'breadthfirst', directed: true, roots: '#n1' }
    } else if (name === 'cose') {
      layoutConfig = { name: 'cose', nodeRepulsion: 8000, idealEdgeLength: 100 }
    } else if (name === 'circle') {
      layoutConfig = { name: 'circle' }
    }

    cyRef.current.layout(layoutConfig).run()
  }

  useEffect(() => {
    if (!cyRef.current) return
    cyRef.current.batch(() => {
      cyRef.current?.nodes().forEach((n) => {
        if (n.data('risk') < threatFilter) {
          n.style('display', 'none')
        } else {
          n.style('display', 'element')
        }
      })
    })
  }, [threatFilter])

  const findPath = () => {
    if (!cyRef.current) return
    cyRef.current.elements().removeClass('highlighted')
    const aStar = cyRef.current.elements().aStar({
      root: `#${pathSource}`,
      goal: `#${pathTarget}`,
      directed: false
    })

    if (aStar.found) {
      aStar.path.addClass('highlighted')
    } else {
      alert('No direct path found between selected entities!')
    }
  }

  const speakText = (text: string) => {
    window.speechSynthesis.cancel()
    const cleanText = text.replace(/[*#`_]/g, '')
    const utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.rate = 1.05
    utterance.pitch = 0.95
    window.speechSynthesis.speak(utterance)
  }

  const handleSendChat = async () => {
    if (!chatInput.trim()) return
    const userMsg = chatInput
    setChatMessages((prev) => [...prev, { sender: 'user', text: userMsg }])
    setChatInput('')
    setIsAiLoading(true)

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/chat/message', { message: userMsg })
      setChatMessages((prev) => [...prev, { sender: 'ai', text: res.data.response }])
    } catch {
      setChatMessages((prev) => [...prev, { sender: 'ai', text: 'Error connecting to intelligence copilot.' }])
    } finally {
      setIsAiLoading(false)
    }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16, height: 'calc(100vh - 120px)' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, position: 'relative' }}>
        
        {/* HUD Controls Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.85)', padding: '10px 16px', borderRadius: 12, border: '1px solid #1e293b' }}>
          
          <div style={{ display: 'flex', gap: 6 }}>
            <span style={{ fontSize: 11, color: '#94a3b8', display: 'flex', alignItems: 'center', marginRight: 4 }}>LAYOUT:</span>
            {[
              { id: 'concentric', label: '🎯 Radial Kingpin' },
              { id: 'breadthfirst', label: '🌲 Command Tree' },
              { id: 'cose', label: '⚡ Force Physics' },
              { id: 'circle', label: '⭕ Circular' }
            ].map((l) => (
              <button
                key={l.id}
                onClick={() => applyLayout(l.id)}
                style={{
                  padding: '5px 10px',
                  borderRadius: 6,
                  background: layoutMode === l.id ? '#1d4ed8' : '#020617',
                  border: layoutMode === l.id ? '1px solid #38bdf8' : '1px solid #334155',
                  color: 'white',
                  fontSize: 11,
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                {l.label}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>Filter Threat &gt;= <b style={{ color: '#ef4444' }}>{threatFilter}</b></span>
            <input
              type="range"
              min="40"
              max="90"
              value={threatFilter}
              onChange={(e) => setThreatFilter(parseInt(e.target.value))}
              style={{ width: 85 }}
            />
          </div>

          <button
            onClick={() => cyRef.current?.fit()}
            style={{ padding: '5px 10px', borderRadius: 6, background: '#334155', color: 'white', border: 'none', fontSize: 11, fontWeight: 700, cursor: 'pointer' }}
          >
            ⛶ Center View
          </button>
        </div>

        {/* Pathfinder */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'rgba(15, 23, 42, 0.75)', padding: '8px 14px', borderRadius: 10, border: '1px solid #1e293b' }}>
          <span style={{ fontSize: 11, color: '#f59e0b', fontWeight: 800 }}>⚡ PATHFINDER:</span>
          <select value={pathSource} onChange={(e) => setPathSource(e.target.value)} style={{ padding: '4px 8px', borderRadius: 6, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11 }}>
            <option value="n1">Arjun Mehta (Kingpin)</option>
            <option value="n2">Mohammed Rafiq (Hawala)</option>
            <option value="n3">Vikram Singh (Logistics)</option>
          </select>
          <span style={{ color: '#94a3b8', fontSize: 11 }}>➔</span>
          <select value={pathTarget} onChange={(e) => setPathTarget(e.target.value)} style={{ padding: '4px 8px', borderRadius: 6, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11 }}>
            <option value="n9">Phoenix Trading LLC</option>
            <option value="n7">Goregaon Warehouse</option>
            <option value="n8">BMW X5 Fleet</option>
          </select>
          <button onClick={findPath} style={{ padding: '4px 12px', borderRadius: 6, background: '#d97706', color: 'white', border: 'none', fontSize: 11, fontWeight: 800, cursor: 'pointer' }}>
            Trace Money Trail
          </button>
        </div>

        {/* Canvas */}
        <div
          ref={containerRef}
          style={{
            flex: 1,
            background: 'radial-gradient(circle at center, #0b1329 0%, #030712 100%)',
            borderRadius: 14,
            border: '1px solid rgba(59, 130, 246, 0.3)',
            boxShadow: 'inset 0 0 40px rgba(0,0,0,0.8)'
          }}
        />

        {selectedNode && (
          <div style={{ position: 'absolute', bottom: 16, left: 16, background: 'rgba(15, 23, 42, 0.95)', padding: 14, borderRadius: 10, border: '1px solid #38bdf8', maxWidth: 320, boxShadow: '0 10px 30px rgba(0,0,0,0.8)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 800, color: 'white', fontSize: 13 }}>{selectedNode.label}</span>
              <button onClick={() => setSelectedNode(null)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: 12 }}>✕</button>
            </div>
            <div style={{ fontSize: 11, color: '#38bdf8', marginTop: 2 }}>{selectedNode.role} ({selectedNode.type})</div>
            <div style={{ fontSize: 11, color: '#ef4444', fontWeight: 800, marginTop: 4 }}>Threat Score: {selectedNode.risk} / 100</div>
          </div>
        )}
      </div>

      {/* Right AI Copilot HUD */}
      <div style={{ background: 'rgba(15, 23, 42, 0.85)', borderRadius: 14, border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ padding: '12px 16px', background: 'rgba(2, 6, 23, 0.8)', borderBottom: '1px solid #1e293b', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 16 }}>🤖</span>
            <span style={{ fontSize: 13, fontWeight: 800, color: '#38bdf8' }}>CrimeNet AI Live Copilot</span>
          </div>
          <span style={{ fontSize: 10, color: '#34d399', fontWeight: 700 }}>● VOICE ENABLED</span>
        </div>

        {/* Chat Stream */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
          {chatMessages.map((m, i) => (
            <div
              key={i}
              style={{
                alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
                background: m.sender === 'user' ? '#1d4ed8' : '#0c1324',
                color: 'white',
                padding: '10px 12px',
                borderRadius: 10,
                fontSize: 11.5,
                lineHeight: 1.5,
                maxWidth: '92%',
                border: m.sender === 'user' ? 'none' : '1px solid #334155',
                display: 'flex',
                flexDirection: 'column',
                gap: 4
              }}
            >
              <div style={{ whiteSpace: 'pre-line' }}>{m.text}</div>
              {m.sender === 'ai' && (
                <button
                  onClick={() => speakText(m.text)}
                  style={{ alignSelf: 'flex-start', background: '#1e293b', border: '1px solid #38bdf8', color: '#38bdf8', padding: '2px 8px', borderRadius: 4, fontSize: 9.5, fontWeight: 700, cursor: 'pointer', marginTop: 4 }}
                >
                  🎙️ Read Intel Aloud
                </button>
              )}
            </div>
          ))}

          {isAiLoading && (
            <div style={{ alignSelf: 'flex-start', background: '#0c1324', color: '#38bdf8', padding: '8px 12px', borderRadius: 8, fontSize: 11, border: '1px solid #334155', fontStyle: 'italic' }}>
              ⏳ Analyzing case evidence & neural intelligence...
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        {/* Chat Input */}
        <div style={{ padding: 12, borderTop: '1px solid #1e293b', display: 'flex', gap: 8, background: '#020617' }}>
          <input
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
            placeholder="Ask AI anything (e.g. 9834702432, who is Priya?)..."
            style={{ flex: 1, padding: '8px 12px', borderRadius: 8, background: '#0f172a', border: '1px solid #334155', color: 'white', fontSize: 11, outline: 'none' }}
          />
          <button
            onClick={handleSendChat}
            disabled={isAiLoading}
            style={{ padding: '8px 14px', borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 11, cursor: isAiLoading ? 'not-allowed' : 'pointer' }}
          >
            Ask
          </button>
        </div>
      </div>
    </div>
  )
}
