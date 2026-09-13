import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Radio,
  Landmark,
  FileText,
  Car,
  Wallet,
  Zap,
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Search,
  UploadCloud,
  Network,
  Eye
} from 'lucide-react'

interface DatasetPipelineProps {
  onNavigateToGraph?: () => void
}

export default function DatasetPipeline({ onNavigateToGraph }: DatasetPipelineProps) {
  const [activeDomain, setActiveDomain] = useState<'all' | 'cdr' | 'banking' | 'fir' | 'anpr' | 'wallet'>('all')
  const [isLoading, setIsLoading] = useState(false)
  const [pipelineResult, setPipelineResult] = useState<any>(null)
  const [summary, setSummary] = useState<any>(null)
  const [selectedLinkFilter, setSelectedLinkFilter] = useState<string>('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [csvUploadType, setCsvUploadType] = useState<string>('cdr')
  const [csvRawText, setCsvRawText] = useState<string>('')
  const [uploadMessage, setUploadMessage] = useState<string>('')

  // Fetch current summary on mount
  const fetchSummary = async () => {
    try {
      const res = await axios.get('/api/pipeline/summary')
      setSummary(res.data)
    } catch (e) {
      console.error('Failed to fetch summary:', e)
    }
  }

  useEffect(() => {
    fetchSummary()
  }, [])

  // 1-Click Load All 5 Sample Datasets
  const handleLoadAllSamples = async () => {
    setIsLoading(true)
    setUploadMessage('')
    try {
      const res = await axios.post('/api/pipeline/load-all-samples')
      setPipelineResult(res.data)
      await fetchSummary()
    } catch (err: any) {
      alert('Failed to execute pipeline: ' + (err.response?.data?.detail || err.message))
    } finally {
      setIsLoading(false)
    }
  }

  // Reset Graph to Baseline Seed
  const handleResetGraph = async () => {
    if (!confirm('Reset graph topology back to initial baseline seeds?')) return
    setIsLoading(true)
    try {
      await axios.post('/api/pipeline/reset')
      setPipelineResult(null)
      await fetchSummary()
      alert('✓ Graph successfully restored to verified baseline seed.')
    } catch (err: any) {
      alert('Reset failed: ' + err.message)
    } finally {
      setIsLoading(false)
    }
  }

  // Ingest Custom CSV
  const handleIngestCsv = async () => {
    if (!csvRawText.trim()) {
      alert('Please paste or upload CSV content.')
      return
    }
    setIsLoading(true)
    try {
      const res = await axios.post('/api/pipeline/ingest', {
        csv_content: csvRawText,
        csv_dataset_type: csvUploadType
      })
      setPipelineResult(res.data)
      setUploadMessage(`✓ Ingested CSV records for ${csvUploadType.toUpperCase()} successfully!`)
      setCsvRawText('')
      await fetchSummary()
    } catch (err: any) {
      alert('CSV ingestion error: ' + (err.response?.data?.detail || err.message))
    } finally {
      setIsLoading(false)
    }
  }

  // Load single domain sample
  const handleLoadSingleDomain = async (domain: string) => {
    setIsLoading(true)
    try {
      const sampleRes = await axios.get(`/api/pipeline/sample-data/${domain}`)
      const payload: any = {}
      if (domain === 'cdr') payload.cdr_records = sampleRes.data.records
      else if (domain === 'banking') payload.banking_records = sampleRes.data.records
      else if (domain === 'fir') payload.fir_records = sampleRes.data.records
      else if (domain === 'anpr') payload.anpr_records = sampleRes.data.records
      else if (domain === 'wallet') payload.wallet_records = sampleRes.data.records

      const res = await axios.post('/api/pipeline/ingest', payload)
      setPipelineResult(res.data)
      setUploadMessage(`✓ Loaded ${sampleRes.data.count} sample records for ${domain.toUpperCase()}`)
      await fetchSummary()
    } catch (err: any) {
      alert('Failed to load domain sample: ' + err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const links = pipelineResult?.links || []
  const filteredLinks = links.filter((l: any) => {
    const matchesCategory =
      selectedLinkFilter === 'ALL' ||
      (selectedLinkFilter === 'CROSS_DOMAIN' &&
        ['CROSS_DOMAIN_IDENTITY', 'SPATIOTEMPORAL_CO_LOCATION', 'SUSPECT_VEHICLE_CITED', 'HAWALA_ON_OFF_RAMP'].includes(l.label)) ||
      (selectedLinkFilter === 'COMMUNICATION' && l.label === 'CALLED') ||
      (selectedLinkFilter === 'FINANCIAL' && ['FUNDS_TRANSFERRED', 'WALLET_TRANSFER', 'HOLDS_ACCOUNT', 'OWNS_WALLET'].includes(l.label)) ||
      (selectedLinkFilter === 'SURVEILLANCE' && ['CAPTURED_AT_TOLL', 'SPATIOTEMPORAL_CO_LOCATION'].includes(l.label)) ||
      (selectedLinkFilter === 'LEGAL' && ['NAMED_IN_FIR', 'LODGED_FIR', 'SUSPECT_VEHICLE_CITED'].includes(l.label))

    if (!matchesCategory) return false

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const text = `${l.source} ${l.target} ${l.label} ${l.rationale || ''}`.toLowerCase()
      return text.includes(q)
    }
    return true
  })

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', background: '#030712', color: '#f8fafc', padding: '20px', overflowY: 'auto' }}>
      
      {/* ── HEADER BANNER ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 20 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: 'linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(56, 189, 248, 0.35)' }}>
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 style={{ fontSize: 20, fontWeight: 900, letterSpacing: '0.04em', margin: 0, textTransform: 'uppercase' }}>
                Multi-Source Intelligence Ingestion & Link Analysis
              </h1>
              <p style={{ margin: '3px 0 0', fontSize: 11.5, color: '#94a3b8' }}>
                Real Working Pipeline: CDR · Banking RTGS · Police FIR · Highway ANPR · Digital Wallets & Crypto
              </p>
            </div>
          </div>
        </div>

        {/* Master Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button
            onClick={handleResetGraph}
            disabled={isLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '9px 14px',
              borderRadius: 8,
              background: '#1e293b',
              border: '1px solid #475569',
              color: '#cbd5e1',
              fontSize: 12,
              fontWeight: 700,
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            <RotateCcw className="w-4 h-4 text-slate-400" />
            <span>Reset Graph Baseline</span>
          </button>

          <button
            onClick={handleLoadAllSamples}
            disabled={isLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 18px',
              borderRadius: 10,
              background: 'linear-gradient(135deg, #2563eb 0%, #0284c7 100%)',
              border: '1px solid #38bdf8',
              color: 'white',
              fontSize: 13,
              fontWeight: 900,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              boxShadow: '0 0 25px rgba(56, 189, 248, 0.4)'
            }}
          >
            <Zap className="w-4 h-4 text-amber-300" />
            <span>{isLoading ? 'Processing Pipeline...' : '✨ Load All 5 Datasets & Auto-Generate Links'}</span>
          </button>

          {onNavigateToGraph && (
            <button
              onClick={onNavigateToGraph}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '10px 16px',
                borderRadius: 10,
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid #10b981',
                color: '#34d399',
                fontSize: 12.5,
                fontWeight: 800,
                cursor: 'pointer'
              }}
            >
              <Network className="w-4 h-4" />
              <span>Explore in Graph</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* ── REAL-TIME PIPELINE METRIC CARDS ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14, marginBottom: 20 }}>
        <div style={{ padding: 14, borderRadius: 12, background: '#0b1329', border: '1px solid #1e293b' }}>
          <div style={{ fontSize: 10.5, color: '#94a3b8', fontWeight: 800 }}>DATABASE ENTITIES</div>
          <div style={{ fontSize: 24, fontWeight: 900, color: 'white', marginTop: 4 }}>
            {summary?.total_entities || 0}
          </div>
          <div style={{ fontSize: 10, color: '#38bdf8', marginTop: 2 }}>Phones, Persons, Accounts, Vehicles</div>
        </div>

        <div style={{ padding: 14, borderRadius: 12, background: '#0b1329', border: '1px solid #1e293b' }}>
          <div style={{ fontSize: 10.5, color: '#94a3b8', fontWeight: 800 }}>TOTAL ACTIVE EDGES</div>
          <div style={{ fontSize: 24, fontWeight: 900, color: '#a78bfa', marginTop: 4 }}>
            {summary?.total_relationships || 0}
          </div>
          <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>Direct & Synthesized Links</div>
        </div>

        <div style={{ padding: 14, borderRadius: 12, background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 78, 59, 0.2) 100%)', border: '1px solid #10b981' }}>
          <div style={{ fontSize: 10.5, color: '#34d399', fontWeight: 900 }}>CROSS-DOMAIN DISCOVERIES</div>
          <div style={{ fontSize: 24, fontWeight: 900, color: '#34d399', marginTop: 4 }}>
            {summary?.cross_domain_links || 0}
          </div>
          <div style={{ fontSize: 10, color: '#6ee7b7', marginTop: 2 }}>Phone KYC · Co-location · Hawala</div>
        </div>

        <div style={{ padding: 14, borderRadius: 12, background: '#0b1329', border: '1px solid #1e293b' }}>
          <div style={{ fontSize: 10.5, color: '#94a3b8', fontWeight: 800 }}>PIPELINE STATUS</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 8 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#34d399', boxShadow: '0 0 10px #34d399' }} />
            <span style={{ fontSize: 14, fontWeight: 900, color: '#34d399' }}>OPERATIONAL</span>
          </div>
          <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 4 }}>SQLite WAL + NetworkX Sync</div>
        </div>
      </div>

      {uploadMessage && (
        <div style={{ padding: '10px 16px', borderRadius: 8, background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#34d399', fontSize: 12, fontWeight: 800, marginBottom: 16 }}>
          {uploadMessage}
        </div>
      )}

      {/* ── 5 DOMAIN DATASET HUBS ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 20 }}>
        
        {/* CDR Card */}
        <div style={{ padding: 14, borderRadius: 12, background: '#0b1329', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Radio className="w-5 h-5 text-sky-400" />
                <span style={{ fontWeight: 800, fontSize: 13 }}>Telecom CDR</span>
              </div>
              <span style={{ fontSize: 9.5, padding: '2px 6px', borderRadius: 4, background: '#1e293b', color: '#38bdf8' }}>Calls & Towers</span>
            </div>
            <p style={{ fontSize: 11, color: '#94a3b8', margin: '8px 0 12px', lineHeight: 1.4 }}>
              Call logs, cell tower geographic pings, handset IMEIs, and caller-receiver pairings.
            </p>
          </div>
          <button
            onClick={() => handleLoadSingleDomain('cdr')}
            style={{ width: '100%', padding: '7px', borderRadius: 6, background: '#0284c7', border: 'none', color: 'white', fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}
          >
            Load CDR Sample
          </button>
        </div>

        {/* Banking Card */}
        <div style={{ padding: 14, borderRadius: 12, background: '#0b1329', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Landmark className="w-5 h-5 text-emerald-400" />
                <span style={{ fontWeight: 800, fontSize: 13 }}>Banking & RTGS</span>
              </div>
              <span style={{ fontSize: 9.5, padding: '2px 6px', borderRadius: 4, background: '#1e293b', color: '#34d399' }}>Wires & Ledger</span>
            </div>
            <p style={{ fontSize: 11, color: '#94a3b8', margin: '8px 0 12px', lineHeight: 1.4 }}>
              Originating/destination bank accounts, RTGS wire transfers, and linked KYC contact numbers.
            </p>
          </div>
          <button
            onClick={() => handleLoadSingleDomain('banking')}
            style={{ width: '100%', padding: '7px', borderRadius: 6, background: '#059669', border: 'none', color: 'white', fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}
          >
            Load Banking Sample
          </button>
        </div>

        {/* FIR Card */}
        <div style={{ padding: 14, borderRadius: 12, background: '#0b1329', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <FileText className="w-5 h-5 text-amber-400" />
                <span style={{ fontWeight: 800, fontSize: 13 }}>FIR Police Records</span>
              </div>
              <span style={{ fontSize: 9.5, padding: '2px 6px', borderRadius: 4, background: '#1e293b', color: '#fbbf24' }}>Legal Accused</span>
            </div>
            <p style={{ fontSize: 11, color: '#94a3b8', margin: '8px 0 12px', lineHeight: 1.4 }}>
              First Information Reports citing accused suspects, IPC legal sections, vehicles, and accounts.
            </p>
          </div>
          <button
            onClick={() => handleLoadSingleDomain('fir')}
            style={{ width: '100%', padding: '7px', borderRadius: 6, background: '#d97706', border: 'none', color: 'white', fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}
          >
            Load FIR Sample
          </button>
        </div>

        {/* ANPR Card */}
        <div style={{ padding: 14, borderRadius: 12, background: '#0b1329', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Car className="w-5 h-5 text-purple-400" />
                <span style={{ fontWeight: 800, fontSize: 13 }}>Highway ANPR</span>
              </div>
              <span style={{ fontSize: 9.5, padding: '2px 6px', borderRadius: 4, background: '#1e293b', color: '#c084fc' }}>Toll Cameras</span>
            </div>
            <p style={{ fontSize: 11, color: '#94a3b8', margin: '8px 0 12px', lineHeight: 1.4 }}>
              Toll gate license plate captures, vehicle speeds, and RTO registered vehicle owner profiles.
            </p>
          </div>
          <button
            onClick={() => handleLoadSingleDomain('anpr')}
            style={{ width: '100%', padding: '7px', borderRadius: 6, background: '#9333ea', border: 'none', color: 'white', fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}
          >
            Load ANPR Sample
          </button>
        </div>

        {/* Digital Wallet Card */}
        <div style={{ padding: 14, borderRadius: 12, background: '#0b1329', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Wallet className="w-5 h-5 text-cyan-400" />
                <span style={{ fontWeight: 800, fontSize: 13 }}>Wallets & USDT</span>
              </div>
              <span style={{ fontSize: 9.5, padding: '2px 6px', borderRadius: 4, background: '#1e293b', color: '#22d3ee' }}>UPI & TRC20</span>
            </div>
            <p style={{ fontSize: 11, color: '#94a3b8', margin: '8px 0 12px', lineHeight: 1.4 }}>
              UPI handles, digital wallet transfers, and USDT TRC-20 crypto mixer off-ramps.
            </p>
          </div>
          <button
            onClick={() => handleLoadSingleDomain('wallet')}
            style={{ width: '100%', padding: '7px', borderRadius: 6, background: '#0891b2', border: 'none', color: 'white', fontSize: 11.5, fontWeight: 700, cursor: 'pointer' }}
          >
            Load Wallet Sample
          </button>
        </div>

      </div>

      {/* ── CUSTOM CSV UPLOADER SECTION ── */}
      <div style={{ padding: 16, borderRadius: 12, background: '#0a1020', border: '1px solid #1e293b', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <UploadCloud className="w-4 h-4 text-sky-400" />
            <span style={{ fontWeight: 800, fontSize: 13, color: '#e2e8f0' }}>Custom Dataset CSV Ingestion</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>Target Domain:</span>
            <select
              value={csvUploadType}
              onChange={(e) => setCsvUploadType(e.target.value)}
              style={{ padding: '4px 8px', borderRadius: 6, background: '#020617', border: '1px solid #334155', color: '#38bdf8', fontSize: 11.5, fontWeight: 700 }}
            >
              <option value="cdr">Telecom CDR</option>
              <option value="banking">Banking Ledger</option>
              <option value="fir">FIR Police Record</option>
              <option value="anpr">Highway ANPR</option>
              <option value="wallet">Digital Wallet / USDT</option>
            </select>
          </div>
        </div>

        <textarea
          rows={3}
          value={csvRawText}
          onChange={(e) => setCsvRawText(e.target.value)}
          placeholder={`Paste ${csvUploadType.toUpperCase()} CSV records here (e.g. caller,receiver,duration_sec,timestamp,tower_name,lat,lng...)`}
          style={{ width: '100%', padding: '10px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: '#cbd5e1', fontSize: 11, fontFamily: 'monospace', resize: 'vertical' }}
        />

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 10 }}>
          <button
            onClick={handleIngestCsv}
            disabled={isLoading || !csvRawText.trim()}
            style={{
              padding: '8px 16px',
              borderRadius: 8,
              background: csvRawText.trim() ? '#0284c7' : '#1e293b',
              border: 'none',
              color: 'white',
              fontSize: 12,
              fontWeight: 800,
              cursor: csvRawText.trim() ? 'pointer' : 'not-allowed'
            }}
          >
            Parse & Ingest CSV Records
          </button>
        </div>
      </div>

      {/* ── GENERATED INTELLIGENCE LINKS TABLE ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#0a1020', borderRadius: 12, border: '1px solid #1e293b', padding: 16 }}>
        
        {/* Table Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontWeight: 900, fontSize: 14, color: 'white' }}>DISCOVERED GRAPH LINKS</span>
            <span style={{ padding: '2px 8px', borderRadius: 12, background: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8', fontSize: 11, fontWeight: 800 }}>
              {filteredLinks.length} Links
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            {/* Filter Tabs */}
            {['ALL', 'CROSS_DOMAIN', 'COMMUNICATION', 'FINANCIAL', 'SURVEILLANCE', 'LEGAL'].map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedLinkFilter(cat)}
                style={{
                  padding: '5px 10px',
                  borderRadius: 6,
                  border: 'none',
                  background: selectedLinkFilter === cat ? '#0284c7' : '#1e293b',
                  color: selectedLinkFilter === cat ? 'white' : '#94a3b8',
                  fontSize: 11,
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                {cat.replace('_', ' ')}
              </button>
            ))}

            {/* Search */}
            <div style={{ position: 'relative' }}>
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search entities or rationale..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  padding: '5px 8px 5px 28px',
                  borderRadius: 6,
                  background: '#020617',
                  border: '1px solid #334155',
                  color: 'white',
                  fontSize: 11,
                  outline: 'none'
                }}
              />
            </div>
          </div>
        </div>

        {/* Links Table */}
        <div style={{ overflowX: 'auto' }}>
          {filteredLinks.length === 0 ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#64748b', fontSize: 13 }}>
              No links currently loaded. Click <b>"Load All 5 Datasets & Auto-Generate Links"</b> above to process the multi-source intelligence pipeline.
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11.5 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e293b', color: '#94a3b8', textAlign: 'left' }}>
                  <th style={{ padding: '8px 10px' }}>SOURCE ENTITY</th>
                  <th style={{ padding: '8px 10px' }}>LINK TYPE</th>
                  <th style={{ padding: '8px 10px' }}>TARGET ENTITY</th>
                  <th style={{ padding: '8px 10px' }}>CONFIDENCE</th>
                  <th style={{ padding: '8px 10px' }}>INVESTIGATIVE RATIONALE</th>
                  <th style={{ padding: '8px 10px' }}>PROVENANCE</th>
                </tr>
              </thead>
              <tbody>
                {filteredLinks.map((link: any, idx: number) => {
                  const isCrossDomain = ['CROSS_DOMAIN_IDENTITY', 'SPATIOTEMPORAL_CO_LOCATION', 'SUSPECT_VEHICLE_CITED', 'HAWALA_ON_OFF_RAMP'].includes(link.label)
                  return (
                    <tr
                      key={link.id || idx}
                      style={{
                        borderBottom: '1px solid #141f36',
                        background: isCrossDomain ? 'rgba(16, 185, 129, 0.05)' : 'transparent',
                        transition: '0.15s'
                      }}
                    >
                      <td style={{ padding: '10px', fontWeight: 800, color: '#f1f5f9' }}>
                        {link.source}
                      </td>
                      <td style={{ padding: '10px' }}>
                        <span
                          style={{
                            padding: '3px 8px',
                            borderRadius: 4,
                            fontSize: 10,
                            fontWeight: 800,
                            background: isCrossDomain
                              ? 'rgba(16, 185, 129, 0.2)'
                              : link.type === 'COMMUNICATION'
                              ? 'rgba(56, 189, 248, 0.15)'
                              : link.type === 'FINANCIAL' || link.type === 'CRYPTO'
                              ? 'rgba(234, 179, 8, 0.15)'
                              : 'rgba(168, 85, 247, 0.15)',
                            color: isCrossDomain
                              ? '#34d399'
                              : link.type === 'COMMUNICATION'
                              ? '#38bdf8'
                              : link.type === 'FINANCIAL' || link.type === 'CRYPTO'
                              ? '#facc15'
                              : '#c084fc',
                            border: isCrossDomain ? '1px solid #10b981' : '1px solid transparent'
                          }}
                        >
                          {link.label}
                        </span>
                      </td>
                      <td style={{ padding: '10px', fontWeight: 800, color: '#f1f5f9' }}>
                        {link.target}
                      </td>
                      <td style={{ padding: '10px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <div style={{ width: 45, height: 5, borderRadius: 3, background: '#1e293b', overflow: 'hidden' }}>
                            <div
                              style={{
                                width: `${(link.confidence || 0.9) * 100}%`,
                                height: '100%',
                                background: isCrossDomain ? '#10b981' : '#38bdf8'
                              }}
                            />
                          </div>
                          <span style={{ fontSize: 10.5, fontWeight: 800, color: '#94a3b8' }}>
                            {Math.round((link.confidence || 0.9) * 100)}%
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '10px', color: '#94a3b8', maxWidth: 360, lineHeight: 1.35 }}>
                        {link.rationale}
                      </td>
                      <td style={{ padding: '10px' }}>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                          {(link.provenance || []).map((prov: string, pIdx: number) => (
                            <span
                              key={pIdx}
                              style={{
                                fontSize: 9,
                                padding: '1px 5px',
                                borderRadius: 3,
                                background: '#1e293b',
                                color: '#94a3b8',
                                fontFamily: 'monospace'
                              }}
                            >
                              {prov}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>

      </div>

    </div>
  )
}
