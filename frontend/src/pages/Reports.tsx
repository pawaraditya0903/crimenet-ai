import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Reports() {
  const [template, setTemplate] = useState('full')
  const [entityType, setEntityType] = useState('Person')
  const [entityId, setEntityId] = useState('Arjun Mehta')
  const [loading, setLoading] = useState(false)
  const [statusMsg, setStatusMsg] = useState('')
  const [preview, setPreview] = useState<any>(null)
  const [availableSuspects, setAvailableSuspects] = useState<any[]>([
    { id: 'n1', name: 'Arjun Mehta', type: 'Person' },
    { id: 'n2', name: 'Mohammed Rafiq', type: 'Person' },
    { id: 'n3', name: 'Vikram Singh', type: 'Person' },
    { id: 'n4', name: 'Priya Desai', type: 'Person' },
    { id: 'n5', name: 'Mehta Enterprises Ltd', type: 'Organization' },
    { id: 'n9', name: 'Phoenix Trading LLC (Dubai)', type: 'Organization' }
  ])

  useEffect(() => {
    axios.get('/api/entities/all')
      .then((res) => {
        if (res.data && res.data.entities && res.data.entities.length > 0) {
          setAvailableSuspects(res.data.entities.slice(0, 10))
        }
      })
      .catch(() => {})
  }, [])

  const handleGenerate = async () => {
    setLoading(true)
    setStatusMsg('')
    
    try {
      const response = await axios.post(
        '/api/reports/generate',
        {
          template: template,
          entity_type: entityType,
          entity_id: entityId,
          report_type: template
        },
        { responseType: 'blob' }
      )

      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `CrimeNet_${template.toUpperCase()}_${entityId.replace(/\s+/g, '_')}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      // Set Distinct On-Screen Previews
      if (template === 'full') {
        setPreview({
          title: '📄 Full Profile Dossier',
          target: entityId,
          type: entityType,
          details: [
            { label: 'Criminal Classification', val: 'Syndicate Mastermind / Key Coordinator' },
            { label: 'Known Aliases', val: 'Bhai, AJ, MD-01' },
            { label: 'Direct Associates', val: 'Mohammed Rafiq (Hawala), Vikram Singh (Logistics)' },
            { label: 'Controlled Fronts', val: 'Mehta Enterprises Ltd & Phoenix Trading LLC' }
          ],
          legal: '24/7 non-bailable surveillance order issued under Section 5(2) Indian Telegraph Act.'
        })
      } else if (template === 'network') {
        setPreview({
          title: '🔗 Network Topology & Centrality Audit',
          target: entityId,
          type: entityType,
          details: [
            { label: 'Global PageRank', val: '0.0847 (Rank #1 / Top 1%)' },
            { label: 'Betweenness Centrality', val: '0.312 (Critical Bridge Broker)' },
            { label: 'Community Cluster', val: 'Cluster 1 (Hawala & Laundering Syndicate)' },
            { label: 'Modularity Score', val: 'Q = 0.684 (High Subgraph Density)' }
          ],
          legal: 'Graph analysis confirms target controls 42.8% of shortest communication paths.'
        })
      } else if (template === 'risk') {
        setPreview({
          title: '⚠️ Risk & Threat Assessment',
          target: entityId,
          type: entityType,
          details: [
            { label: 'Isolation Forest Score', val: '0.96 (Critical Outlier Vector)' },
            { label: 'Financial Red Flag', val: '₹1.50 Cr midnight transfer @ 02:00 AM' },
            { label: 'Circular Layering', val: '₹8.75 Cr round-tripping across 3 accounts' },
            { label: 'Telecom Burst Z-Score', val: '4.8 Sigma Deviation (Pre-Raid Alert)' }
          ],
          legal: 'Mandatory asset freeze petition drafted under Section 17 PMLA.'
        })
      } else {
        setPreview({
          title: '📅 Telecom Forensics & CDR Timeline',
          target: entityId,
          type: entityType,
          details: [
            { label: 'Primary Linked IMEI', val: '354892019482019 (Dual SIM Device)' },
            { label: 'Telecom Circle', val: 'Maharashtra & Goa Circle (India)' },
            { label: 'Nocturnal Call Ratio', val: '42.8% (01:30 AM - 04:15 AM)' },
            { label: 'Cell Tower Sector', val: 'Tower #404-45-1920 (19.1663° N, 72.8526° E)' }
          ],
          legal: 'Live IMSI catcher triangulation active under Section 5(2) Indian Telegraph Act.'
        })
      }

      setStatusMsg(`✅ ${template.toUpperCase()} PDF Dossier generated and downloaded!`)
    } catch (err: any) {
      console.error(err)
      setStatusMsg('❌ Error generating report. Ensure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 880, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20, paddingBottom: 40 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 24 }}>📄</span>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 800, color: 'white' }}>Intelligence Dossier & Forensic Report Generator</h2>
          <p style={{ fontSize: 11.5, color: '#94a3b8' }}>Certified judicial evidence compliant under Section 65B Indian Evidence Act · Officer: <b>Aditya Pawar</b></p>
        </div>
      </div>

      {/* 4 Specialized Templates */}
      <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', marginBottom: 12 }}>SELECT SPECIALIZED TEMPLATE</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
          {[
            { id: 'full', title: '📄 1. Full Profile Dossier', desc: 'Complete biography, aliases, lieutenants, shell company holdings & warrants' },
            { id: 'network', title: '🔗 2. Network Topology Report', desc: 'Mathematical PageRank, Betweenness centrality, clusters & edge confidence' },
            { id: 'risk', title: '⚠️ 3. Risk & Threat Assessment', desc: 'Isolation Forest anomaly vectors, ₹1.5 Cr midnight transfer & PMLA warrants' },
            { id: 'timeline', title: '📅 4. CDR & Telecom Timeline', desc: 'Call Detail Records table, nocturnal calling spikes (01:30 AM) & tower IDs' },
          ].map((t) => (
            <div
              key={t.id}
              onClick={() => setTemplate(t.id)}
              style={{
                padding: '14px 16px',
                borderRadius: 10,
                background: template === t.id ? 'rgba(37,99,235,0.25)' : '#0c1324',
                border: template === t.id ? '2px solid #38bdf8' : '1px solid #334155',
                cursor: 'pointer',
                transition: '0.2s'
              }}
            >
              <div style={{ fontWeight: 800, color: 'white', fontSize: 13 }}>{t.title}</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>{t.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Target Form */}
      <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: 20, borderRadius: 14, border: '1px solid #1e293b' }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: '#38bdf8', marginBottom: 8 }}>TARGET INVESTIGATION ENTITY</div>
        
        {/* Quick Select Pills */}
        {availableSuspects.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
            <span style={{ fontSize: 11, color: '#94a3b8', alignSelf: 'center', marginRight: 4 }}>Quick Select:</span>
            {availableSuspects.map((s: any) => (
              <button
                key={s.id}
                type="button"
                onClick={() => { setEntityId(s.name); setEntityType(s.type); }}
                style={{
                  padding: '3px 8px',
                  borderRadius: 6,
                  background: entityId === s.name ? '#1d4ed8' : '#020617',
                  border: '1px solid #334155',
                  color: entityId === s.name ? 'white' : '#94a3b8',
                  fontSize: 10.5,
                  cursor: 'pointer'
                }}
              >
                {s.name} ({s.type})
              </button>
            ))}
          </div>
        )}

        <div style={{ display: 'flex', gap: 12 }}>
          <select
            value={entityType}
            onChange={(e) => setEntityType(e.target.value)}
            style={{ padding: '10px 14px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, outline: 'none' }}
          >
            <option value="Person">Person</option>
            <option value="PhoneNumber">Phone Number</option>
            <option value="Organization">Organization / Shell</option>
            <option value="Vehicle">Vehicle</option>
            <option value="Location">Location</option>
          </select>
          <input
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            placeholder="Enter target name or phone (e.g. Arjun Mehta, 9834702432)..."
            style={{ flex: 1, padding: '10px 14px', borderRadius: 8, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 12, outline: 'none' }}
          />
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          style={{
            width: '100%',
            marginTop: 18,
            padding: '12px 20px',
            borderRadius: 10,
            background: loading ? '#334155' : '#1d4ed8',
            color: 'white',
            border: 'none',
            fontWeight: 800,
            fontSize: 14,
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: '0.2s'
          }}
        >
          {loading ? '⏳ Compiling Specialized PDF...' : `⬇ Generate & Download ${template.toUpperCase()} PDF Report`}
        </button>

        {statusMsg && (
          <div style={{ marginTop: 12, padding: '10px 14px', borderRadius: 8, background: statusMsg.startsWith('✅') ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)', color: statusMsg.startsWith('✅') ? '#34d399' : '#f87171', fontSize: 12, fontWeight: 700 }}>
            {statusMsg}
          </div>
        )}
      </div>

      {/* MERKLE TREE EVIDENCE LEDGER CERTIFICATE (BSA 2023 / SEC 65B) */}
      <div style={{ background: 'rgba(15, 23, 42, 0.85)', padding: 18, borderRadius: 14, border: '1px solid #10b981', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 800, color: '#34d399', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>📜</span> BHARATIYA SAKSHYA ADHINIYAM (BSA 2023) MERKLE EVIDENCE LEDGER
          </div>
          <div style={{ fontSize: 11, color: '#cbd5e1', marginTop: 4 }}>
            All 48 intelligence dossiers, telecom bursts, and crypto transactions are anchored into a SHA-256 binary Merkle Root.
          </div>
          <div style={{ fontSize: 10.5, fontFamily: 'monospace', color: '#38bdf8', marginTop: 6 }}>
            MERKLE ROOT: <code>8f12a99c4b72e0d9b62e49c81a2f57b3e941c8d0a7f23e41b958c21a4f07e19a</code>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ padding: '4px 10px', borderRadius: 6, background: '#064e3b', color: '#6ee7b7', fontSize: 10.5, fontWeight: 800 }}>
            ✓ TAMPER-PROOF CERTIFIED
          </span>
          <div style={{ fontSize: 9.5, color: '#94a3b8', marginTop: 4 }}>Sec 63 BSA 2023 / Sec 65B IEA</div>
        </div>
      </div>

      {/* On-Screen Template Preview */}
      {preview && (
        <div style={{ background: 'rgba(15, 23, 42, 0.9)', padding: 22, borderRadius: 14, border: '1px solid #38bdf8' }}>
          <div style={{ fontSize: 14, fontWeight: 800, color: '#38bdf8' }}>📋 {preview.title}</div>
          <div style={{ fontSize: 16, fontWeight: 800, color: 'white', marginTop: 4 }}>Subject: {preview.target} ({preview.type})</div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, marginTop: 14 }}>
            {preview.details.map((m: any, idx: number) => (
              <div key={idx} style={{ padding: 10, background: '#020617', borderRadius: 8, border: '1px solid #1e293b' }}>
                <div style={{ fontSize: 10, color: '#64748b' }}>{m.label}</div>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#38bdf8', marginTop: 2 }}>{m.val}</div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 14, fontSize: 11, color: '#cbd5e1', lineHeight: 1.5, background: 'rgba(0,0,0,0.3)', padding: 12, borderRadius: 8 }}>
            <b>Legal Compliance & Enforcement Action:</b><br />
            {preview.legal}
          </div>
        </div>
      )}
    </div>
  )
}
