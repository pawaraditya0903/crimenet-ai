with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

code = code.replace(
    """  const handleDeleteSingleLog = async (logItem: any, e: React.MouseEvent) => {
    e.stopPropagation()
    if (soundEnabled) playCyberSound('click')
    try {
      await axios.post('/api/security/delete-log', {
        id: logItem.id || '',
        timestamp: logItem.timestamp || ''
      })
    } catch(e) {}
    setAuditLogs((prev) => prev.filter((item) => item.timestamp !== logItem.timestamp))
  }""",
    """  const handleDeleteSingleLog = async (logItem: any, e: React.MouseEvent) => {
    e.stopPropagation()
    if (soundEnabled) playCyberSound('click')
    try {
      await axios.post('/api/security/delete-log', {
        id: logItem.id || '',
        timestamp: logItem.timestamp || ''
      })
    } catch(e) {}
    setAuditLogs((prev) => prev.filter((item) => item.timestamp !== logItem.timestamp && item.id !== logItem.id))
  }"""
)

with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("Frontend delete handler updated!")
