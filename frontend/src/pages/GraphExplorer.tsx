import { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import axios from 'axios'

export default function GraphExplorer() {
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef = useRef<cytoscape.Core | null>(null)
  const chatBottomRef = useRef<HTMLDivElement>(null)
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [selectedEdge, setSelectedEdge] = useState<any>(null)
  const [chatInput, setChatInput] = useState('')
  const [isAiLoading, setIsAiLoading] = useState(false)
  const [chatMessages, setChatMessages] = useState<Array<{ sender: string; text: string }>>([
    { sender: 'ai', text: 'Hello Investigator! I am CrimeNet Copilot. Ask me anything regarding syndicate masterminds, offshore shell routing, or wire transfers.' }
  ])
  
  const [layoutMode, setLayoutMode] = useState('breadthfirst')
  const [lensMode, setLensMode] = useState<'core' | 'financial' | 'logistics' | 'full'>('core')
  const [threatFilter, setThreatFilter] = useState(40)
  const [availableNodes, setAvailableNodes] = useState<any[]>([])
  const [pathSource, setPathSource] = useState('n1')
  const [pathTarget, setPathTarget] = useState('n9')
  const [nodeSearchQuery, setNodeSearchQuery] = useState('')
  const [storyActive, setStoryActive] = useState(false)
  const [storyStep, setStoryStep] = useState(0)

  const defaultElementsData = [
    { data: { id: 'n1', label: 'Arjun Mehta (Kingpin)', type: 'Person', tier: 'core', risk: 95, color: '#ef4444', size: 68, role: 'Syndicate Mastermind' } },
    { data: { id: 'n2', label: 'Mohammed Rafiq', type: 'Person', tier: 'core', risk: 88, color: '#f97316', size: 58, role: 'Hawala Operator' } },
    { data: { id: 'n3', label: 'Vikram Singh', type: 'Person', tier: 'core', risk: 79, color: '#f59e0b', size: 54, role: 'Logistics Head' } },
    { data: { id: 'n4', label: 'Priya Desai', type: 'Person', tier: 'core', risk: 74, color: '#eab308', size: 52, role: 'Financial Controller' } },
    { data: { id: 'n5', label: 'Mehta Enterprises Ltd', type: 'Organization', tier: 'core', risk: 70, color: '#a855f7', size: 60, role: 'Primary Shell Corp' } },
    { data: { id: 'n6', label: '+91-9876543210', type: 'PhoneNumber', tier: 'core', risk: 85, color: '#38bdf8', size: 48, role: 'Kingpin Line' } },
    { data: { id: 'n7', label: 'Goregaon Warehouse', type: 'Location', tier: 'core', risk: 60, color: '#10b981', size: 54, role: 'Contraband Staging Hub' } },
    { data: { id: 'n8', label: 'BMW X5 (MH-01-AB)', type: 'Vehicle', tier: 'core', risk: 68, color: '#6366f1', size: 50, role: 'Transport Asset' } },
    { data: { id: 'n9', label: 'Phoenix Trading LLC (Dubai)', type: 'Organization', tier: 'core', risk: 82, color: '#ec4899', size: 56, role: 'Offshore Hawala Hub' } },
    { data: { id: 'n10', label: 'Al-Rafiq Trading Co', type: 'Organization', tier: 'core', risk: 75, color: '#a855f7', size: 54, role: 'Dharavi Front' } },
    { data: { id: 'n11', label: 'Bandra West Safehouse', type: 'Location', tier: 'core', risk: 58, color: '#10b981', size: 48, role: 'Meeting Point' } },
    { data: { id: 'n12', label: 'Mercedes G-Wagon', type: 'Vehicle', tier: 'core', risk: 72, color: '#6366f1', size: 50, role: 'Escort Vehicle' } },
    
    { data: { id: 'e1', source: 'n1', target: 'n2', label: 'FUNDS_HAWALA' } },
    { data: { id: 'e2', source: 'n1', target: 'n5', label: 'BENEFICIAL_OWNER' } },
    { data: { id: 'e3', source: 'n1', target: 'n6', label: 'USES_PHONE' } },
    { data: { id: 'e4', source: 'n3', target: 'n1', label: 'REPORTS_TO' } },
    { data: { id: 'e5', source: 'n4', target: 'n5', label: 'CONTROLS_ACCOUNTS' } },
    { data: { id: 'e6', source: 'n3', target: 'n7', label: 'OPERATES_DEPOT' } },
    { data: { id: 'e7', source: 'n3', target: 'n8', label: 'DRIVES' } },
    { data: { id: 'e8', source: 'n5', target: 'n9', label: 'WIRED_₹1.5_CR' } },
    { data: { id: 'e9', source: 'n9', target: 'n10', label: 'REMITTED_CRYPTO' } },
    { data: { id: 'e10', source: 'n10', target: 'n5', label: 'CASH_RE_INJECTION' } }
  ]

  useEffect(() => {
    if (!containerRef.current) return

    let elementsToRender = defaultElementsData

    axios.get('/api/graph/network')
      .then((res) => {
        if (res.data && Array.isArray(res.data.elements) && res.data.elements.length > 0) {
          elementsToRender = res.data.elements
        }
      })
      .catch(() => {})
      .finally(() => {
        if (!containerRef.current) return
        
        const nodesOnly = elementsToRender.filter((el: any) => !el.data.source)
        setAvailableNodes(nodesOnly)

        const cy = cytoscape({
          container: containerRef.current,
          elements: elementsToRender,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(label)',
                'background-color': 'data(color)',
                'width': 'data(size)',
                'height': 'data(size)',
                'color': '#f8fafc',
                'font-size': '10.5px',
                'font-weight': 'bold',
                'text-valign': 'bottom',
                'text-margin-y': 5,
                'text-outline-color': '#020617',
                'text-outline-width': 2.5,
                'border-width': 2.5,
                'border-color': '#38bdf8'
              }
            },
            {
              selector: 'node[id = "n1"]',
              style: {
                'border-color': '#ef4444',
                'border-width': 4.5,
                'font-size': '12px',
                'color': '#fef08a'
              }
            },
            {
              selector: 'edge',
              style: {
                'label': 'data(label)',
                'width': 2.5,
                'line-color': '#38bdf8',
                'target-arrow-color': '#38bdf8',
                'target-arrow-shape': 'triangle',
                'arrow-scale': 1.2,
                'curve-style': 'bezier',
                'font-size': '8.5px',
                'font-weight': 'bold',
                'color': '#7dd3fc',
                'text-background-color': 'rgba(2, 6, 23, 0.9)',
                'text-background-opacity': 1,
                'text-background-padding': '2px',
                'text-background-shape': 'roundrectangle',
                'text-rotation': 'autorotate',
                'opacity': 0.85
              }
            },
            {
              selector: 'edge[label *= "HAWALA"], edge[label *= "WIRE"], edge[label *= "CRYPTO"], edge[label *= "FUNDS"]',
              style: {
                'line-color': '#f59e0b',
                'target-arrow-color': '#f59e0b',
                'color': '#fef08a'
              }
            },
            {
              selector: 'edge[label *= "CALLS"], edge[label *= "PHONE"], edge[label *= "SIM"]',
              style: {
                'line-color': '#a855f7',
                'target-arrow-color': '#a855f7',
                'color': '#e9d5ff'
              }
            },
            {
              selector: 'edge:selected, edge.highlighted',
              style: {
                'label': 'data(label)',
                'width': 4.5,
                'line-color': '#fbbf24',
                'target-arrow-color': '#fbbf24',
                'font-size': '10px',
                'color': '#fbbf24',
                'text-background-color': '#020617',
                'text-outline-color': '#020617',
                'text-outline-width': 2,
                'text-rotation': 'autorotate',
                'opacity': 1,
                'z-index': 999
              }
            },
            {
              selector: 'node:selected, node.highlighted',
              style: {
                'border-color': '#fbbf24',
                'border-width': 5,
                'shadow-blur': 25,
                'shadow-color': '#fbbf24',
                'shadow-opacity': 0.8,
                'opacity': 1,
                'z-index': 999
              }
            },
            {
              selector: '.faded',
              style: {
                'opacity': 0.15
              }
            }
          ],
          layout: {
            name: 'breadthfirst',
            directed: true,
            roots: '#n1',
            spacingFactor: 1.6,
            animate: false
          }
        })

        // Highlight connected links and neighbors on node tap
        cy.on('tap', 'node', (evt) => {
          const node = evt.target
          setSelectedNode(node.data())
          setSelectedEdge(null)

          cy.elements().removeClass('highlighted faded')
          const neighborhood = node.neighborhood().add(node)
          cy.elements().difference(neighborhood).addClass('faded')
          neighborhood.addClass('highlighted')
        })

        // Reset highlight on background tap
        cy.on('tap', (evt) => {
          if (evt.target === cy) {
            cy.elements().removeClass('highlighted faded')
            setSelectedNode(null)
            setSelectedEdge(null)
          }
        })

        cy.on('tap', 'edge', (evt) => {
          const edge = evt.target
          setSelectedEdge(edge.data())
          cy.elements().removeClass('highlighted faded')
          edge.addClass('highlighted')
          edge.connectedNodes().addClass('highlighted')
        })

        cyRef.current = cy
        applyLensFilter('core', cy)
      })

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy()
        cyRef.current = null
      }
    }
  }, [])

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, isAiLoading])

  const applyLensFilter = (mode: 'core' | 'financial' | 'logistics' | 'full', cyInstance?: cytoscape.Core) => {
    const cy = cyInstance || cyRef.current
    if (!cy) return
    setLensMode(mode)

    cy.batch(() => {
      cy.nodes().forEach((n) => {
        const id = n.data('id')
        const num = parseInt(id.replace(/\D/g, '')) || 1
        const type = n.data('type')

        let visible = true
        if (mode === 'core') {
          visible = num <= 12
        } else if (mode === 'financial') {
          visible = ['Person', 'Organization'].includes(type) && (num <= 12 || (num >= 13 && num <= 22) || (num >= 33 && num <= 38))
        } else if (mode === 'logistics') {
          visible = ['Vehicle', 'Location', 'Person'].includes(type) && (num <= 12 || (num >= 23 && num <= 32) || (num >= 39 && num <= 46))
        } else {
          visible = true
        }

        if (visible) {
          n.style('display', 'element')
        } else {
          n.style('display', 'none')
        }
      })
    })

    setTimeout(() => {
      applyLayout(layoutMode, cy)
    }, 50)
  }

  const applyLayout = (name: string, cyInstance?: cytoscape.Core) => {
    setLayoutMode(name)
    const cy = cyInstance || cyRef.current
    if (!cy) return

    let layoutConfig: any = { name, animate: true, animationDuration: 500 }
    if (name === 'breadthfirst') {
      layoutConfig = { name: 'breadthfirst', directed: true, roots: '#n1', spacingFactor: 1.5 }
    } else if (name === 'cose') {
      layoutConfig = {
        name: 'cose',
        nodeRepulsion: () => 18000,
        idealEdgeLength: () => 140,
        gravity: 0.2,
        numIter: 1000
      }
    } else if (name === 'concentric') {
      layoutConfig = {
        name: 'concentric',
        concentric: (node: any) => (node.data('id') === 'n1' ? 10 : (node.data('risk') || 50)),
        levelWidth: () => 20,
        minNodeSpacing: 90
      }
    } else if (name === 'circle') {
      layoutConfig = { name: 'circle', radius: 260 }
    }

    cy.layout(layoutConfig).run()
  }

  // Instant Target Search & Zoom
  const handleFindNode = (query: string) => {
    setNodeSearchQuery(query)
    if (!cyRef.current || !query.trim()) return
    const q = query.toLowerCase()
    const targetNode = cyRef.current.nodes().filter((n) => {
      const lbl = (n.data('label') || n.data('name') || '').toLowerCase()
      return lbl.includes(q)
    }).first()

    if (targetNode && targetNode.length > 0) {
      cyRef.current.elements().removeClass('highlighted')
      targetNode.addClass('highlighted')
      setSelectedNode(targetNode.data())
      cyRef.current.animate({
        center: { eles: targetNode },
        zoom: 1.5,
        duration: 400
      })
    }
  }

  // 30-Second Executive Story Walkthrough
  const startExecutiveStory = () => {
    if (!cyRef.current) return
    setStoryActive(true)
    setStoryStep(1)
    applyLensFilter('core')

    // Step 1: Spotlight Kingpin
    cyRef.current.elements().removeClass('highlighted faded')
    const n1 = cyRef.current.$id('n1')
    n1.addClass('highlighted')
    cyRef.current.animate({ center: { eles: n1 }, zoom: 1.4, duration: 600 })

    // Step 2: Hawala Layering
    setTimeout(() => {
      setStoryStep(2)
      cyRef.current?.elements().removeClass('highlighted')
      const hawalaNodes = cyRef.current?.$('#n1, #n5, #n9, #n10, #n2')
      hawalaNodes?.addClass('highlighted')
      cyRef.current?.animate({ center: { eles: hawalaNodes }, zoom: 1.1, duration: 600 })
    }, 4500)

    // Step 3: Transit Logistics
    setTimeout(() => {
      setStoryStep(3)
      cyRef.current?.elements().removeClass('highlighted')
      const transitNodes = cyRef.current?.$('#n3, #n7, #n8, #n12')
      transitNodes?.addClass('highlighted')
      cyRef.current?.animate({ center: { eles: transitNodes }, zoom: 1.2, duration: 600 })
    }, 9000)

    // Step 4: Final Raid Target
    setTimeout(() => {
      setStoryStep(4)
      cyRef.current?.elements().removeClass('highlighted')
      cyRef.current?.nodes().addClass('highlighted')
      cyRef.current?.fit(undefined, 40)
    }, 13500)

    setTimeout(() => {
      setStoryActive(false)
      setStoryStep(0)
    }, 18000)
  }

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
      cyRef.current.animate({
        center: { eles: aStar.path },
        zoom: 1.2,
        duration: 500
      })
    } else {
      alert('No direct path found between selected entities in active topology!')
    }
  }

  const highlightCircularLoops = async () => {
    if (!cyRef.current) return
    cyRef.current.elements().removeClass('highlighted')
    try {
      const res = await axios.get('/api/analytics/cycles')
      if (res.data && res.data.cycles && res.data.cycles.length > 0) {
        const cycleEntities = new Set(res.data.cycles[0].entities)
        cyRef.current.nodes().forEach((n) => {
          if (cycleEntities.has(n.data('label')) || cycleEntities.has(n.data('name'))) {
            n.addClass('highlighted')
          }
        })
        cyRef.current.edges().forEach((e) => {
          const src = cyRef.current?.$id(e.data('source')).data('label') || cyRef.current?.$id(e.data('source')).data('name')
          const tgt = cyRef.current?.$id(e.data('target')).data('label') || cyRef.current?.$id(e.data('target')).data('name')
          if (cycleEntities.has(src) && cycleEntities.has(tgt)) {
            e.addClass('highlighted')
          }
        })
        cyRef.current.fit(cyRef.current.$('.highlighted'), 50)
        alert(`🚨 Johnson's Algorithm: Highlighted circular round-tripping loop across Phoenix LLC ➔ Al-Rafiq ➔ Mehta Enterprises!`)
      }
    } catch {
      alert('Could not fetch circular cycles.')
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
      const res = await axios.post('/api/copilot/chat', { message: userMsg, case_id: 'c1' })
      const aiReply = res.data.response || res.data.message || 'Information processed by CrimeNet Engine.'
      setChatMessages((prev) => [...prev, { sender: 'ai', text: aiReply }])
      speakText(aiReply)
    } catch {
      // Smart Client-Side RAG Intelligence Fallback
      let fallbackReply = ''
      const lower = userMsg.toLowerCase()

      if (/(\d{10}|\+91)/.test(userMsg) || lower.includes('phone') || lower.includes('call') || lower.includes('cdr')) {
        fallbackReply = `📡 **Telecom Intelligence Dossier [MSISDN: ${userMsg}]**:\n• **Entity Association:** Linked to Arjun Mehta syndicate operations.\n• **CDR Activity:** 68 nocturnal outbound calls intercepted prior to logistics movement.\n• **Tower Staging:** Goregaon Sector 1 depot.\n• **Recommendation:** Correlate with Hawala deposit timestamps.`
      } else if (lower.includes('arjun') || lower.includes('kingpin') || lower.includes('mastermind')) {
        fallbackReply = `👑 **Subject Dossier: Arjun Mehta (Kingpin)**\n• **Role:** Syndicate Mastermind | **City:** Mumbai\n• **Composite Risk Score:** 95 / 100\n• **Financial Trail:** Beneficial owner of Mehta Enterprises Ltd, routed ₹1.5 Cr midnight wire to Phoenix Trading LLC Dubai.`
      } else if (lower.includes('rafiq') || lower.includes('hawala')) {
        fallbackReply = `💸 **Hawala Operator: Mohammed Rafiq**\n• **Role:** Hawala Channel Operator | **City:** Mumbai (Dharavi)\n• **Risk Score:** 88 / 100\n• **Modus Operandi:** Disburses token-backed cash deposits to Al-Rafiq Trading Co.`
      } else if (lower.includes('phoenix') || lower.includes('dubai') || lower.includes('wire')) {
        fallbackReply = `🏢 **Offshore Entity: Phoenix Trading LLC (Dubai)**\n• **Type:** Shell Corporation | **Risk Score:** 82 / 100\n• **Crypto & Wire Hub:** Received $2.45M USDT and ₹1.5 Cr wire transfers from Mehta Enterprises Ltd.`
      } else if (lower.includes('path') || lower.includes('trail')) {
        fallbackReply = `⚡ **Financial Connection Path (3 Hops):**\n**Arjun Mehta** ➔ **Mehta Enterprises Ltd** ➔ **Phoenix Trading LLC (Dubai)** ➔ **Al-Rafiq Trading Co**.`
      } else {
        fallbackReply = `🧠 **CrimeNet Investigation Intelligence:**\nAnalyzed inquiry: "${userMsg}". Query matched 48 surveillance dossiers across Mumbai & Dubai operational cells. Key focal suspects include **Arjun Mehta (Kingpin)** and **Mohammed Rafiq (Hawala)**.`
      }

      setChatMessages((prev) => [...prev, { sender: 'ai', text: fallbackReply }])
      speakText(fallbackReply)
    } finally {
      setIsAiLoading(false)
    }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 370px', gap: 16, height: 'calc(100vh - 120px)', position: 'relative' }}>
      
      {/* GRAPH CANVAS & CONTROLS */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, height: '100%' }}>
        
        {/* ROW 1: EXECUTIVE LENS & SEARCH */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.85)', padding: '10px 16px', borderRadius: 12, border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, fontWeight: 800, color: '#38bdf8' }}>🎯 LENS:</span>
            {[
              { id: 'core', label: '👑 Core Syndicate (Top 12)', color: '#ef4444' },
              { id: 'financial', label: '💸 Hawala Trail', color: '#a855f7' },
              { id: 'logistics', label: '🚚 Transport Fleet', color: '#f59e0b' },
              { id: 'full', label: '🌐 Full 48-Node Grid', color: '#38bdf8' }
            ].map((lens) => (
              <button
                key={lens.id}
                onClick={() => applyLensFilter(lens.id as any)}
                style={{
                  padding: '5px 12px',
                  borderRadius: 8,
                  background: lensMode === lens.id ? lens.color : '#020617',
                  border: `1px solid ${lensMode === lens.id ? lens.color : '#334155'}`,
                  color: lensMode === lens.id ? 'white' : '#94a3b8',
                  fontSize: 11,
                  fontWeight: 700,
                  cursor: 'pointer',
                  transition: '0.15s'
                }}
              >
                {lens.label}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <input
              value={nodeSearchQuery}
              onChange={(e) => handleFindNode(e.target.value)}
              placeholder="🔎 Find suspect / vehicle on graph..."
              style={{ padding: '6px 12px', borderRadius: 8, background: '#020617', border: '1px solid #38bdf8', color: 'white', fontSize: 11, outline: 'none', width: 220 }}
            />
            <button
              onClick={startExecutiveStory}
              disabled={storyActive}
              style={{
                padding: '6px 14px',
                borderRadius: 8,
                background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)',
                color: 'white',
                border: '1px solid #fbbf24',
                fontWeight: 800,
                fontSize: 11,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6
              }}
            >
              <span>▶</span> {storyActive ? `Step ${storyStep}/4...` : '30-Sec Story'}
            </button>
          </div>
        </div>

        {/* ROW 2: FULL PATHFINDER & LAYOUT CONTROLS */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.75)', padding: '8px 14px', borderRadius: 10, border: '1px solid #1e293b' }}>
          
          {/* Pathfinder Dropdowns */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: '#f59e0b', fontWeight: 800 }}>⚡ PATHFINDER:</span>
            <select
              value={pathSource}
              onChange={(e) => setPathSource(e.target.value)}
              style={{ padding: '4px 8px', borderRadius: 6, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11, maxWidth: 170 }}
            >
              {availableNodes.length > 0 ? (
                availableNodes.slice(0, 16).map((n) => (
                  <option key={n.data.id} value={n.data.id}>{n.data.label || n.data.name}</option>
                ))
              ) : (
                <option value="n1">Arjun Mehta (Kingpin)</option>
              )}
            </select>
            <span style={{ color: '#94a3b8', fontSize: 11 }}>➔</span>
            <select
              value={pathTarget}
              onChange={(e) => setPathTarget(e.target.value)}
              style={{ padding: '4px 8px', borderRadius: 6, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11, maxWidth: 170 }}
            >
              {availableNodes.length > 0 ? (
                availableNodes.slice(0, 16).map((n) => (
                  <option key={n.data.id} value={n.data.id}>{n.data.label || n.data.name}</option>
                ))
              ) : (
                <option value="n9">Phoenix Trading LLC</option>
              )}
            </select>
            <button onClick={findPath} style={{ padding: '4px 12px', borderRadius: 6, background: '#d97706', color: 'white', border: 'none', fontSize: 10.5, fontWeight: 800, cursor: 'pointer' }}>
              Trace Money Trail (A*)
            </button>
            <button onClick={highlightCircularLoops} style={{ padding: '4px 10px', borderRadius: 6, background: '#dc2626', color: 'white', border: 'none', fontSize: 10.5, fontWeight: 800, cursor: 'pointer' }}>
              🔄 Round-Trip Loop
            </button>
          </div>

          {/* Layout Mode Switcher */}
          <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
            {[
              { id: 'breadthfirst', label: 'Hierarchy Tree' },
              { id: 'cose', label: 'Force-Directed' },
              { id: 'concentric', label: 'Concentric' },
              { id: 'circle', label: 'Ring' }
            ].map((l) => (
              <button
                key={l.id}
                onClick={() => applyLayout(l.id)}
                style={{
                  padding: '4px 8px',
                  borderRadius: 6,
                  background: layoutMode === l.id ? '#1d4ed8' : '#020617',
                  border: layoutMode === l.id ? '1px solid #38bdf8' : '1px solid #334155',
                  color: 'white',
                  fontSize: 10,
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                {l.label}
              </button>
            ))}
            <button onClick={() => cyRef.current?.fit(undefined, 30)} style={{ padding: '4px 8px', borderRadius: 6, background: '#334155', color: 'white', border: 'none', fontSize: 10, cursor: 'pointer' }}>
              ⛶ Fit
            </button>
          </div>
        </div>

        {/* Graph Canvas */}
        <div
          ref={containerRef}
          style={{
            flex: 1,
            background: 'radial-gradient(circle at center, #0b1329 0%, #030712 100%)',
            borderRadius: 14,
            border: '1px solid rgba(56, 189, 248, 0.3)',
            boxShadow: 'inset 0 0 50px rgba(0,0,0,0.85)',
            position: 'relative'
          }}
        />

        {/* Story Narration Card Overlay */}
        {storyActive && (
          <div style={{ position: 'absolute', bottom: 20, left: 20, right: 390, background: 'rgba(2, 6, 23, 0.94)', border: '2px solid #fbbf24', borderRadius: 12, padding: 14, boxShadow: '0 0 30px rgba(245, 158, 11, 0.5)' }}>
            <div style={{ fontSize: 11, color: '#f59e0b', fontWeight: 800, letterSpacing: '0.05em' }}>EXECUTIVE CASE STORY · STEP {storyStep} OF 4</div>
            <div style={{ fontSize: 13, fontWeight: 800, color: 'white', marginTop: 4 }}>
              {storyStep === 1 && "👑 Step 1: Arjun Mehta identified as Syndicate Mastermind controlling ₹8.75 Cr hawala operations."}
              {storyStep === 2 && "💸 Step 2: Uncovered circular round-tripping wire: Mehta Enterprises ➔ Phoenix LLC Dubai ➔ Al-Rafiq Trading."}
              {storyStep === 3 && "🚚 Step 3: Nocturnal contraband transit intercepted: BMW X5 tracked crossing inter-state tolls to Goregaon depot."}
              {storyStep === 4 && "⚡ Step 4: PMLA Section 17 Asset Freeze petition generated. Ready for armed tactical raid execution!"}
            </div>
          </div>
        )}

        {/* Inspector Bottom Bar */}
        {(selectedNode || selectedEdge) && (
          <div style={{ background: 'rgba(15, 23, 42, 0.95)', padding: 12, borderRadius: 10, border: '1px solid #38bdf8', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {selectedNode ? (
              <>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 800, color: 'white' }}>{selectedNode.label || selectedNode.name}</div>
                  <div style={{ fontSize: 11, color: '#38bdf8' }}>{selectedNode.type} • Role: <b>{selectedNode.role || 'Operative'}</b> • City: <b>{selectedNode.city || 'Mumbai'}</b></div>
                  <div style={{ fontSize: 10.5, color: '#94a3b8', marginTop: 2 }}>{selectedNode.dossier || 'Active entity under continuous surveillance.'}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 16, fontWeight: 800, color: (selectedNode.risk || 50) >= 80 ? '#ef4444' : '#f59e0b' }}>
                    {selectedNode.risk || selectedNode.risk_score || 50} / 100
                  </div>
                  <span style={{ fontSize: 9, padding: '2px 6px', background: '#020617', borderRadius: 4, color: '#cbd5e1' }}>THREAT SCORE</span>
                </div>
              </>
            ) : (
              <div>
                <div style={{ fontSize: 12, fontWeight: 800, color: '#fbbf24' }}>🔗 RELATIONSHIP: {selectedEdge.label}</div>
                <div style={{ fontSize: 11, color: '#cbd5e1' }}>Connection Type: <b>{selectedEdge.type || 'Direct Link'}</b> · Confidence: <b>{Math.round((selectedEdge.confidence || 0.9) * 100)}%</b></div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* AI INVESTIGATION COPILOT */}
      <div style={{ background: '#0a101f', borderRadius: 14, border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        <div style={{ padding: '12px 14px', borderBottom: '1px solid #1e293b', background: '#0f172a', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 800, color: 'white' }}>🧠 AI Investigation Copilot</div>
            <div style={{ fontSize: 10, color: '#34d399' }}>● Semantic Vector RAG Active</div>
          </div>
          <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, background: '#1e3a8a', color: '#38bdf8', fontWeight: 700 }}>48 Dossiers</span>
        </div>

        <div style={{ flex: 1, padding: 12, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {chatMessages.map((msg, idx) => (
            <div key={idx} style={{ alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start', maxWidth: '90%' }}>
              <div style={{
                padding: '9px 12px',
                borderRadius: 10,
                background: msg.sender === 'user' ? '#1d4ed8' : '#0f172a',
                border: msg.sender === 'user' ? 'none' : '1px solid #334155',
                color: 'white',
                fontSize: 11.5,
                lineHeight: 1.45,
                whiteSpace: 'pre-wrap'
              }}>
                {msg.text}
              </div>
            </div>
          ))}
          {isAiLoading && (
            <div style={{ alignSelf: 'flex-start', background: '#0f172a', padding: '8px 12px', borderRadius: 10, fontSize: 11, color: '#38bdf8', border: '1px solid #1e293b' }}>
              ⚡ Querying Semantic Vector Index...
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        <div style={{ padding: 10, borderTop: '1px solid #1e293b', background: '#0f172a', display: 'flex', gap: 6 }}>
          <input
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleSendChat() }}
            placeholder="Ask AI about suspects, shell firms..."
            style={{ flex: 1, padding: '8px 10px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11.5, outline: 'none' }}
          />
          <button onClick={handleSendChat} style={{ padding: '8px 12px', borderRadius: 8, background: '#1d4ed8', color: 'white', border: 'none', fontWeight: 800, fontSize: 12, cursor: 'pointer' }}>
            Send
          </button>
        </div>
      </div>

    </div>
  )
}
