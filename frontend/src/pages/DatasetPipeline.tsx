import React, { useState, useEffect, useRef } from 'react'
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
  Eye,
  FileSpreadsheet,
  X,
  Check,
  FileUp,
  FileCode
} from 'lucide-react'

interface DatasetPipelineProps {
  onNavigateToGraph?: () => void
}

const DOMAIN_INFO: Record<string, { label: string; icon: any; required: string[]; optional: string[] }> = {
  cdr: {
    label: 'Telecom CDR',
    icon: Radio,
    required: ['caller', 'receiver', 'timestamp'],
    optional: ['duration_sec', 'tower_name', 'tower_id', 'imei', 'imsi', 'lat', 'lng']
  },
  banking: {
    label: 'Banking Ledger',
    icon: Landmark,
    required: ['from_account', 'to_account', 'amount', 'timestamp'],
    optional: ['from_name', 'to_name', 'bank_name', 'txn_type', 'linked_phone', 'narration']
  },
  fir: {
    label: 'FIR Police Records',
    icon: FileText,
    required: ['fir_no', 'police_station', 'accused_name'],
    optional: ['complainant', 'ipc_sections', 'suspect_phone', 'suspect_vehicle', 'suspect_account']
  },
  anpr: {
    label: 'Highway ANPR',
    icon: Car,
    required: ['plate_number', 'camera_id', 'timestamp'],
    optional: ['location_name', 'vehicle_model', 'speed_kmh', 'registered_owner', 'owner_phone', 'lat', 'lng']
  },
  wallet: {
    label: 'Digital Wallet / USDT',
    icon: Wallet,
    required: ['sender_wallet', 'receiver_wallet', 'amount', 'timestamp'],
    optional: ['sender_name', 'receiver_name', 'platform', 'sender_phone', 'receiver_phone', 'narration']
  }
}

export default function DatasetPipeline({ onNavigateToGraph }: DatasetPipelineProps) {
  const [activeDomain, setActiveDomain] = useState<'all' | 'cdr' | 'banking' | 'fir' | 'anpr' | 'wallet'>('all')
  const [isLoading, setIsLoading] = useState(false)
  const [pipelineResult, setPipelineResult] = useState<any>(null)
  const [summary, setSummary] = useState<any>(null)
  const [selectedLinkFilter, setSelectedLinkFilter] = useState<string>('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [csvUploadType, setCsvUploadType] = useState<string>('cdr')
  const [uploadMessage, setUploadMessage] = useState<string>('')

  // ── REAL CSV FILE UPLOAD LAYER STATE ──
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [processingStage, setProcessingStage] = useState<string>('')
  const [uploadError, setUploadError] = useState<{ message: string; missing_columns?: string[]; details?: string } | null>(null)
  const [uploadSuccessMetrics, setUploadSuccessMetrics] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

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
    setUploadError(null)
    setUploadSuccessMetrics(null)
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
    setUploadError(null)
    setUploadSuccessMetrics(null)
    try {
      await axios.post('/api/pipeline/reset')
      setPipelineResult(null)
      setSelectedFile(null)
      await fetchSummary()
      alert('✓ Graph successfully restored to verified baseline seed.')
    } catch (err: any) {
      alert('Reset failed: ' + err.message)
    } finally {
      setIsLoading(false)
    }
  }

  // File selection handlers
  const handleFileSelect = (file: File | null) => {
    setUploadError(null)
    setUploadSuccessMetrics(null)
    if (!file) {
      setSelectedFile(null)
      return
    }
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setUploadError({ message: `File "${file.name}" is not a valid CSV. Please select a .csv file.` })
      setSelectedFile(null)
      return
    }
    setSelectedFile(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  // Real CSV File Upload & Processing
  const handleProcessCsvFile = async () => {
    if (!selectedFile) return
    setIsLoading(true)
    setUploadError(null)
    setUploadSuccessMetrics(null)
    setProcessingStage('Uploading & Validating CSV Schema...')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('dataset_type', csvUploadType)

      setProcessingStage('Ingesting Records & Resolving Entities...')

      const res = await axios.post('/api/pipeline/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setProcessingStage('Synthesizing Cross-Domain Links...')
      setPipelineResult(res.data)
      setUploadSuccessMetrics(res.data)
      setUploadMessage(`✓ Successfully processed ${res.data.records_processed} records from ${selectedFile.name}`)
      await fetchSummary()
    } catch (err: any) {
      console.error('CSV upload error:', err)
      const errorData = err.response?.data?.detail
      if (typeof errorData === 'object' && errorData !== null) {
        setUploadError({
          message: errorData.message || 'Dataset validation failed.',
          missing_columns: errorData.missing_columns,
          details: errorData.required_columns ? `Required columns: ${errorData.required_columns.join(', ')}` : undefined
        })
      } else {
        setUploadError({
          message: errorData || err.message || 'Failed to upload and process CSV dataset.'
        })
      }
    } finally {
      setIsLoading(false)
      setProcessingStage('')
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

      {/* ── REAL CUSTOM CSV UPLOADER SECTION ── */}
      <div style={{ padding: 18, borderRadius: 14, background: '#0a1020', border: '1px solid #1e293b', marginBottom: 20 }}>
        
        {/* Section Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 34, height: 34, borderRadius: 8, background: 'rgba(56, 189, 248, 0.15)', border: '1px solid #38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FileSpreadsheet className="w-5 h-5 text-sky-400" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 14, color: 'white', letterSpacing: '0.02em' }}>
                Upload Custom Dataset (CSV Engine)
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>
                Select dataset type, choose or drop a local CSV file, and execute multi-domain entity resolution.
              </div>
            </div>
          </div>

          <div style={{ fontSize: 11, color: '#64748b', fontFamily: 'monospace' }}>
            MAX SIZE: 10MB · UTF-8 COMMA SEPARATED
          </div>
        </div>

        {/* 1. Dataset Type Selector */}
        <div style={{ marginBottom: 14 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#cbd5e1', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Step 1: Select Dataset Type
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {Object.entries(DOMAIN_INFO).map(([key, info]) => {
              const IconComponent = info.icon
              const isSelected = csvUploadType === key
              return (
                <button
                  key={key}
                  onClick={() => { setCsvUploadType(key); setUploadError(null); }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '8px 14px',
                    borderRadius: 8,
                    border: isSelected ? '1px solid #38bdf8' : '1px solid #1e293b',
                    background: isSelected ? '#1d4ed8' : '#020617',
                    color: isSelected ? 'white' : '#94a3b8',
                    fontSize: 12,
                    fontWeight: isSelected ? 800 : 600,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <IconComponent className="w-4 h-4" />
                  <span>{info.label}</span>
                </button>
              )
            })}
          </div>

          {/* Schema Required Columns Guidance */}
          <div style={{ marginTop: 10, padding: '8px 12px', borderRadius: 6, background: '#020617', border: '1px solid #1e293b', fontSize: 11, display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <span style={{ color: '#38bdf8', fontWeight: 800 }}>Schema Requirements for {DOMAIN_INFO[csvUploadType]?.label}:</span>
            <span style={{ color: '#fbbf24' }}>
              Required: <b>{DOMAIN_INFO[csvUploadType]?.required.join(', ')}</b>
            </span>
            <span style={{ color: '#64748b' }}>|</span>
            <span style={{ color: '#94a3b8' }}>
              Optional: {DOMAIN_INFO[csvUploadType]?.optional.join(', ')}
            </span>
          </div>
        </div>

        {/* 2. Drag-and-Drop & File Picker Zone */}
        <div style={{ marginBottom: 14 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#cbd5e1', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Step 2: Choose CSV File
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,text/csv"
            style={{ display: 'none' }}
            onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
          />

          {!selectedFile ? (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              style={{
                border: `2px dashed ${isDragging ? '#38bdf8' : '#334155'}`,
                background: isDragging ? 'rgba(56, 189, 248, 0.08)' : '#020617',
                borderRadius: 10,
                padding: '28px 20px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <FileUp className={`w-8 h-8 mx-auto mb-2 ${isDragging ? 'text-sky-400' : 'text-slate-500'}`} />
              <div style={{ fontSize: 13, fontWeight: 800, color: 'white' }}>
                Drag and drop your <span style={{ color: '#38bdf8' }}>{DOMAIN_INFO[csvUploadType]?.label} CSV</span> here, or click to browse
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
                Supports UTF-8 comma-separated files (.csv) up to 10MB
              </div>
            </div>
          ) : (
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '14px 18px',
                borderRadius: 10,
                background: '#020617',
                border: '1px solid #10b981'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 36, height: 36, borderRadius: 8, background: 'rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 800, color: 'white' }}>
                    {selectedFile.name}
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', display: 'flex', gap: 8, marginTop: 2 }}>
                    <span>Size: <b>{formatFileSize(selectedFile.size)}</b></span>
                    <span>•</span>
                    <span style={{ color: '#34d399', fontWeight: 700 }}>✓ CSV Verified</span>
                    <span>•</span>
                    <span>Target: <b>{DOMAIN_INFO[csvUploadType]?.label}</b></span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  style={{
                    padding: '6px 12px',
                    borderRadius: 6,
                    background: '#1e293b',
                    border: '1px solid #475569',
                    color: '#cbd5e1',
                    fontSize: 11.5,
                    fontWeight: 700,
                    cursor: isLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  Change File
                </button>
                <button
                  onClick={() => setSelectedFile(null)}
                  disabled={isLoading}
                  style={{
                    padding: '6px 10px',
                    borderRadius: 6,
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid #ef4444',
                    color: '#f87171',
                    fontSize: 11.5,
                    fontWeight: 700,
                    cursor: isLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  ✕ Remove
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 3. Action Button & Processing Lifecycle */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
          <div style={{ fontSize: 12, color: '#94a3b8' }}>
            {processingStage ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#38bdf8', fontWeight: 800 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#38bdf8', boxShadow: '0 0 10px #38bdf8' }} />
                <span>{processingStage}</span>
              </div>
            ) : selectedFile ? (
              <span style={{ color: '#34d399' }}>Ready to parse {selectedFile.name}</span>
            ) : (
              <span>Select a CSV file to process</span>
            )}
          </div>

          <button
            onClick={handleProcessCsvFile}
            disabled={isLoading || !selectedFile}
            style={{
              padding: '10px 22px',
              borderRadius: 8,
              background: isLoading ? '#334155' : selectedFile ? 'linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%)' : '#1e293b',
              border: selectedFile ? '1px solid #38bdf8' : 'none',
              color: 'white',
              fontSize: 12.5,
              fontWeight: 800,
              cursor: isLoading || !selectedFile ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              boxShadow: selectedFile && !isLoading ? '0 0 20px rgba(56, 189, 248, 0.3)' : 'none'
            }}
          >
            <UploadCloud className="w-4 h-4" />
            <span>{isLoading ? (processingStage || 'Processing Dataset...') : 'Process Dataset'}</span>
          </button>
        </div>

        {/* 4. Error Alert View */}
        {uploadError && (
          <div style={{ marginTop: 14, padding: '12px 16px', borderRadius: 8, background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#f87171', fontWeight: 800, fontSize: 13 }}>
              <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>❌ Upload Failed: {uploadError.message}</span>
            </div>
            {uploadError.missing_columns && (
              <div style={{ marginTop: 6, fontSize: 11.5, color: '#fca5a5' }}>
                Missing Required Columns: <code style={{ background: '#020617', padding: '2px 6px', borderRadius: 4, color: '#fbbf24', fontFamily: 'monospace' }}>{uploadError.missing_columns.join(', ')}</code>
              </div>
            )}
            {uploadError.details && (
              <div style={{ marginTop: 4, fontSize: 11, color: '#cbd5e1' }}>
                {uploadError.details}
              </div>
            )}
          </div>
        )}

        {/* 5. Real Metrics Success Dashboard */}
        {uploadSuccessMetrics && (
          <div style={{ marginTop: 14, padding: '16px', borderRadius: 10, background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 78, 59, 0.18) 100%)', border: '1px solid #10b981' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10, marginBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span style={{ fontSize: 13.5, fontWeight: 900, color: '#34d399' }}>
                  ✓ DATASET PROCESSED SUCCESSFULLY
                </span>
                <span style={{ fontSize: 10.5, padding: '2px 8px', borderRadius: 4, background: '#064e3b', color: '#6ee7b7', fontWeight: 800 }}>
                  DOMAIN: {uploadSuccessMetrics.dataset_type}
                </span>
              </div>

              {onNavigateToGraph && (
                <button
                  onClick={onNavigateToGraph}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '6px 12px',
                    borderRadius: 6,
                    background: '#10b981',
                    border: 'none',
                    color: 'white',
                    fontSize: 11.5,
                    fontWeight: 800,
                    cursor: 'pointer'
                  }}
                >
                  <Network className="w-3.5 h-3.5" />
                  <span>Explore in Graph</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              )}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10 }}>
              <div style={{ padding: '10px 12px', background: 'rgba(2, 6, 23, 0.6)', borderRadius: 8, border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, textTransform: 'uppercase' }}>Records Processed</div>
                <div style={{ fontSize: 18, fontWeight: 900, color: 'white', marginTop: 2 }}>{uploadSuccessMetrics.records_processed}</div>
              </div>
              <div style={{ padding: '10px 12px', background: 'rgba(2, 6, 23, 0.6)', borderRadius: 8, border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, textTransform: 'uppercase' }}>Entities Discovered</div>
                <div style={{ fontSize: 18, fontWeight: 900, color: '#38bdf8', marginTop: 2 }}>{uploadSuccessMetrics.entities_created}</div>
              </div>
              <div style={{ padding: '10px 12px', background: 'rgba(2, 6, 23, 0.6)', borderRadius: 8, border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, textTransform: 'uppercase' }}>Relationships Generated</div>
                <div style={{ fontSize: 18, fontWeight: 900, color: '#a78bfa', marginTop: 2 }}>{uploadSuccessMetrics.relationships_generated}</div>
              </div>
              <div style={{ padding: '10px 12px', background: 'rgba(2, 6, 23, 0.6)', borderRadius: 8, border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, textTransform: 'uppercase' }}>Cross-Domain Links</div>
                <div style={{ fontSize: 18, fontWeight: 900, color: '#34d399', marginTop: 2 }}>{uploadSuccessMetrics.cross_domain_links}</div>
              </div>
            </div>
          </div>
        )}

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
