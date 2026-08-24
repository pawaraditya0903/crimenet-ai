import json, os

# 1. Update backend storage capacity to 1,000 logs
backend_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py"
with open(backend_path, "r", encoding="utf-8-sig") as f:
    bcode = f.read().replace("\ufeff", "")

bcode = bcode.replace("existing[:500]", "existing[:1000]")
bcode = bcode.replace("logs[:500]", "logs[:1000]")
bcode = bcode.replace("existing[:100]", "existing[:1000]")
bcode = bcode.replace("logs[:100]", "logs[:1000]")

with open(backend_path, "w", encoding="utf-8") as f:
    f.write(bcode)

# 2. Update frontend to include Live Search & Log Count
frontend_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx"
with open(frontend_path, "r", encoding="utf-8-sig") as f:
    fcode = f.read().replace("\ufeff", "")

# Add logSearch state if not present
if "logSearchQuery" not in fcode:
    fcode = fcode.replace(
        "const [logFilter, setLogFilter] = useState<'ALL' | 'BLOCKED' | 'AUTHORIZED'>('ALL')",
        "const [logFilter, setLogFilter] = useState<'ALL' | 'BLOCKED' | 'AUTHORIZED'>('ALL')\n  const [logSearchQuery, setLogSearchQuery] = useState('')"
    )

    # Update filteredLogs to support text search
    fcode = fcode.replace(
        """  const filteredLogs = auditLogs.filter((l: any) => {
    if (logFilter === 'BLOCKED') return l.status.includes('BLOCKED')
    if (logFilter === 'AUTHORIZED') return l.status.includes('AUTHORIZED')
    return true
  })""",
        """  const filteredLogs = auditLogs.filter((l: any) => {
    const matchesFilter = logFilter === 'ALL' || (logFilter === 'BLOCKED' && l.status.includes('BLOCKED')) || (logFilter === 'AUTHORIZED' && l.status.includes('AUTHORIZED'))
    const q = logSearchQuery.toLowerCase().trim()
    if (!q) return matchesFilter
    const text = `${l.ip} ${l.device} ${l.action} ${l.timestamp} ${l.status} ${l.badge || ''}`.toLowerCase()
    return matchesFilter && text.includes(q)
  })"""
    )

    # Add search bar & count header into the Modal UI
    old_header_controls = """                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  {(['ALL', 'BLOCKED', 'AUTHORIZED'] as const).map((f) => ("""

    new_header_controls = """                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 8, flexWrap: 'wrap' }}>
                  <input
                    type="text"
                    placeholder="🔍 Search IP, Device, Timestamp..."
                    value={logSearchQuery}
                    onChange={(e) => setLogSearchQuery(e.target.value)}
                    style={{ padding: '5px 12px', borderRadius: 6, background: '#020617', border: '1px solid #334155', color: 'white', fontSize: 11, outline: 'none', width: 220 }}
                  />
                  <div style={{ fontSize: 11, color: '#38bdf8', fontWeight: 800 }}>
                    Showing {filteredLogs.length} of {auditLogs.length} Total Logs
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  {(['ALL', 'BLOCKED', 'AUTHORIZED'] as const).map((f) => ("""

    fcode = fcode.replace(old_header_controls, new_header_controls)

with open(frontend_path, "w", encoding="utf-8") as f:
    f.write(fcode)

print("1,000+ Logs Capacity with Live Search Bar Installed!")
