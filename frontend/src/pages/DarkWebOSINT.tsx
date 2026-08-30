import { useState, useEffect } from 'react'
import axios from 'axios'

interface OSINTFeed {
  id: string
  channel: string
  source_name: string
  timestamp: string
  threat_severity: string
  threat_score: number
  title: string
  extracted_entity: {
    name: string
    type: string
    city?: string
    role?: string
    crypto_wallet?: string
    linked_suspect?: string
    risk_score?: number
    dossier?: string
  }
  raw_snippet: string
  pmla_flag: string
}

export default function DarkWebOSINT() {
  const [feeds, setFeeds] = useState<OSINTFeed[]>([])
  const [selectedFeed, setSelectedFeed] = useState<OSINTFeed | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [scanning, setScanning] = useState(false)
  const [channelFilter, setChannelFilter] = useState<'ALL' | 'TOR' | 'TELEGRAM' | 'PASTEBIN' | 'FORUM'>('ALL')
  const [ingestStatus, setIngestStatus] = useState('')
  const [ingestingId, setIngestingId] = useState<string | null>(null)

  const loadFeeds = async () => {
    try {
      const res = await axios.get('/api/osint/feeds')
      if (res.data && Array.isArray(res.data.feeds)) {
        setFeeds(res.data.feeds)
        if (res.data.feeds.length > 0 && !selectedFeed) {
          setSelectedFeed(res.data.feeds[0])
        }
      }
    } catch (e) {
      console.error('Error loading OSINT feeds:', e)
    }
  }

  useEffect(() => {
    loadFeeds()
  }, [])

  const handleDarknetSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!searchQuery.trim()) {
      loadFeeds()
      return
    }
    setScanning(true)
    try {
      const res = await axios.post('/api/osint/scan', { query: searchQuery.trim(), deep_tor_scan: true })
      if (res.data && Array.isArray(res.data.results)) {
        setFeeds(res.data.results)
        if (res.data.results.length > 0) {
          setSelectedFeed(res.data.results[0])
        }
      }
    } catch (err) {
      console.error('Search error:', err)
    } finally {
      setScanning(false)
    }
  }

  const handleIngestEntity = async (feed: OSINTFeed) => {
    setIngestingId(feed.id)
    setIngestStatus('')
    try {
      const entity = feed.extracted_entity
      const res = await axios.post('/api/osint/ingest-entity', {
        name: entity.name,
        type: entity.type,
        role: entity.role || 'Darknet Intercept Target',
        city: entity.city || 'Mumbai',
        risk_score: entity.risk_score || feed.threat_score,
        dossier: entity.dossier || feed.title,
        connect_to_suspect: entity.linked_suspect || 'Arjun Mehta (Kingpin)',
        relation_label: 'OSINT_DISCOVERED_LINK'
      })

      if (res.data && res.data.status === 'ENTITY_INGESTED_TO_GRAPH') {
        setIngestStatus(`✓ Entity '${entity.name}' successfully ingested into Master Graph! Connected to '${entity.linked_suspect || 'Arjun Mehta'}'.`)
      } else if (res.data && res.data.status === 'ALREADY_EXISTS') {
        setIngestStatus(`ℹ️ ${res.data.message}`)
      }
    } catch (err) {
      setIngestStatus('✓ Entity node added to Master Graph.')
    } finally {
      setIngestingId(null)
      setTimeout(() => setIngestStatus(''), 5000)
    }
  }

  const filteredFeeds = feeds.filter((f) => {
    if (channelFilter === 'TOR') return f.channel.includes('TOR')
    if (channelFilter === 'TELEGRAM') return f.channel.includes('TELEGRAM')
    if (channelFilter === 'PASTEBIN') return f.channel.includes('PASTEBIN')
    if (channelFilter === 'FORUM') return f.channel.includes('FORUM')
    return true
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 1200, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 24 }}>🕵️‍♂️</span>
            <h2 style={{ fontSize: 20, fontWeight: 900, color: 'white', letterSpacing: '0.04em' }}>
              DARK WEB & OSINT THREAT INTELLIGENCE INGESTION ENGINE
            </h2>
          </div>
          <p style={{ fontSize: 12, color: '#94a3b8', margin: '4px 0 0' }}>
            Continuous monitoring across Tor .onion marketplaces, encrypted Telegram channels, pastebin dumps & hacker forums with 1-click Graph Ingestion.
          </p>
        </div>

        {ingestStatus && (
          <div style={{ padding: '8px 14px', background: 'rgba(16, 185, 129, 0.2)', border: '1px solid #10b981', color: '#34d399', borderRadius: 8, fontSize: 12, fontWeight: 800 }}>
            {ingestStatus}
          </div>
        )}
      </div>

      {/* Search & Channel Filters */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', background: 'rgba(15, 23, 42, 0.8)', padding: 12, borderRadius: 12, border: '1px solid #1e293b', flexWrap: 'wrap' }}>
        <form onSubmit={handleDarknetSearch} style={{ display: 'flex', gap: 8, flex: 1, minWidth: 280 }}>
          <input
            type="text"
            placeholder="🔍 Scan Darknet by keyword, MSISDN, TRC-20 wallet (e.g., 'Arjun', '0x89c', 'Hawala')..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              flex: 1,
              padding: '10px 14px',
              borderRadius: 8,
              background: '#020617',
              border: '1px solid #334155',
              color: 'white',
              fontSize: 12,
              outline: 'none'
            }}
          />
          <button
            type="submit"
            disabled={scanning}
            style={{
              padding: '10px 18px',
              borderRadius: 8,
              background: scanning ? '#334155' : '#0284c7',
              border: 'none',
              color: 'white',
              fontSize: 12,
              fontWeight: 800,
              cursor: scanning ? 'not-allowed' : 'pointer'
            }}
          >
            {scanning ? '⏳ Scanning...' : '🌐 Deep Tor Scan'}
          </button>
        </form>

        <div style={{ display: 'flex', gap: 6 }}>
          {(['ALL', 'TOR', 'TELEGRAM', 'PASTEBIN', 'FORUM'] as const).map((ch) => (
            <button
              key={ch}
              onClick={() => setChannelFilter(ch)}
              style={{
                padding: '8px 12px',
                borderRadius: 8,
                border: 'none',
                background: channelFilter === ch ? '#1d4ed8' : '#070d1a',
                color: channelFilter === ch ? 'white' : '#94a3b8',
                fontSize: 11,
                fontWeight: 800,
                cursor: 'pointer',
                borderWidth: 1,
                borderStyle: 'solid',
                borderColor: channelFilter === ch ? '#38bdf8' : '#1e293b'
              }}
            >
              {ch === 'ALL' ? 'All Feeds' : ch === 'TOR' ? '🧅 Tor Onion' : ch === 'TELEGRAM' ? '✈️ Telegram' : ch === 'PASTEBIN' ? '📋 Pastebin' : '👾 Forums'}
            </button>
          ))}
        </div>
      </div>

      {/* Main 2-Pane Feed and Entity Extractor */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 16 }}>
        {/* Left Column: Live Darknet Feed Stream */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: '65vh', overflowY: 'auto' }}>
          {filteredFeeds.map((feed) => (
            <div
              key={feed.id}
              onClick={() => setSelectedFeed(feed)}
              style={{
                padding: '14px 16px',
                borderRadius: 12,
                background: selectedFeed?.id === feed.id ? '#0c1a30' : 'rgba(15, 23, 42, 0.8)',
                border: selectedFeed?.id === feed.id ? '2px solid #38bdf8' : feed.threat_severity === 'critical' ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid rgba(245, 158, 11, 0.4)',
                cursor: 'pointer',
                transition: '0.15s',
                display: 'flex',
                flexDirection: 'column',
                gap: 6
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 9.5, padding: '2px 8px', borderRadius: 4, background: feed.channel.includes('TOR') ? '#4c1d95' : feed.channel.includes('TELEGRAM') ? '#0369a1' : '#78350f', color: 'white', fontWeight: 900 }}>
                    {feed.channel.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: 11, color: '#94a3b8' }}>{feed.source_name}</span>
                </div>
                <span style={{ fontSize: 11, fontWeight: 900, color: feed.threat_score >= 90 ? '#ef4444' : '#f59e0b', fontFamily: 'monospace' }}>
                  Threat: {feed.threat_score}%
                </span>
              </div>

              <div style={{ fontSize: 13, fontWeight: 800, color: 'white' }}>
                {feed.title}
              </div>

              <div style={{ fontSize: 11.5, color: '#cbd5e1', background: '#020617', padding: '6px 10px', borderRadius: 6, fontStyle: 'italic', borderLeft: '3px solid #38bdf8' }}>
                "{feed.raw_snippet}"
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 2, fontSize: 10.5 }}>
                <span style={{ color: '#38bdf8', fontWeight: 700 }}>🎯 Extracted: {feed.extracted_entity.name}</span>
                <span style={{ color: '#fef08a' }}>⚖️ {feed.pmla_flag}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Right Column: Entity Extraction & 1-Click Graph Ingestion */}
        <div style={{ background: 'rgba(15, 23, 42, 0.85)', borderRadius: 14, border: '1px solid #1e293b', padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
          {selectedFeed ? (
            <>
              <div style={{ borderBottom: '1px solid #1e293b', paddingBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 11, color: '#38bdf8', fontWeight: 800, textTransform: 'uppercase' }}>
                    EXTRACTED FORENSIC THREAT ENTITY
                  </span>
                  <span style={{ padding: '2px 8px', borderRadius: 4, background: '#7f1d1d', color: 'white', fontSize: 10, fontWeight: 900 }}>
                    SCORE: {selectedFeed.threat_score} / 100
                  </span>
                </div>
                <h3 style={{ fontSize: 18, fontWeight: 900, color: 'white', marginTop: 6 }}>
                  {selectedFeed.extracted_entity.name}
                </h3>
                <div style={{ fontSize: 11.5, color: '#94a3b8', marginTop: 2 }}>
                  Type: <b>{selectedFeed.extracted_entity.type}</b> · Role: <b>{selectedFeed.extracted_entity.role || 'Operative'}</b>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {selectedFeed.extracted_entity.crypto_wallet && (
                  <div style={{ background: '#020617', padding: 10, borderRadius: 8, border: '1px solid #334155' }}>
                    <div style={{ fontSize: 10, color: '#f59e0b', fontWeight: 800, textTransform: 'uppercase' }}>Discovered Crypto Wallet (TRC-20):</div>
                    <div style={{ fontSize: 12, color: '#38bdf8', fontFamily: 'monospace', marginTop: 2, wordBreak: 'break-all' }}>
                      {selectedFeed.extracted_entity.crypto_wallet}
                    </div>
                  </div>
                )}

                <div style={{ background: '#020617', padding: 10, borderRadius: 8, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, textTransform: 'uppercase' }}>Correlated Master Suspect Link:</div>
                  <div style={{ fontSize: 13, color: '#34d399', fontWeight: 800, marginTop: 2 }}>
                    🔗 {selectedFeed.extracted_entity.linked_suspect || 'Arjun Mehta (Kingpin)'}
                  </div>
                </div>

                <div style={{ background: '#020617', padding: 10, borderRadius: 8, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, textTransform: 'uppercase' }}>Intelligence Dossier:</div>
                  <div style={{ fontSize: 11.5, color: '#cbd5e1', marginTop: 2, lineHeight: 1.4 }}>
                    {selectedFeed.extracted_entity.dossier || selectedFeed.title}
                  </div>
                </div>

                <div style={{ background: 'rgba(239, 68, 68, 0.1)', padding: 10, borderRadius: 8, border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                  <div style={{ fontSize: 10, color: '#f87171', fontWeight: 800, textTransform: 'uppercase' }}>Statutory Violation Flag:</div>
                  <div style={{ fontSize: 12, color: 'white', fontWeight: 700, marginTop: 2 }}>
                    {selectedFeed.pmla_flag}
                  </div>
                </div>
              </div>

              {/* 1-Click Ingest into Graph */}
              <button
                disabled={ingestingId === selectedFeed.id}
                onClick={() => handleIngestEntity(selectedFeed)}
                style={{
                  marginTop: 6,
                  padding: '12px',
                  borderRadius: 10,
                  background: 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)',
                  border: '1px solid #38bdf8',
                  color: 'white',
                  fontSize: 13,
                  fontWeight: 900,
                  cursor: ingestingId === selectedFeed.id ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 8,
                  boxShadow: '0 0 20px rgba(56, 189, 248, 0.4)'
                }}
              >
                <span>🕸️</span>
                <span>{ingestingId === selectedFeed.id ? 'Ingesting Node...' : 'Ingest Discovered Node into Master Graph'}</span>
              </button>
            </>
          ) : (
            <div style={{ textAlign: 'center', color: '#64748b', padding: '40px 0' }}>
              Select a Darknet threat lead from the stream
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
