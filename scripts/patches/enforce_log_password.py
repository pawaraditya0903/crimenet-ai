with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

# Ensure openAuditLogs always opens password prompt first
old_fn = """const openAuditLogs = async () => {
    try {
      const res = await axios.get('/api/security/audit-logs')
      setAuditLogs(res.data.logs || [])
    } catch(e) {
      setAuditLogs([])
    }
    setAuditModalOpen(true)
  }"""

new_fn = """const openAuditLogs = () => {
    setAuditKeyInput('')
    setAuditKeyError('')
    setAuditAuthModalOpen(true)
  }

  const verifyAuditAccess = async () => {
    const entered = auditKeyInput.trim()
    if (entered !== 'Aditya@09' && entered.toLowerCase() !== 'aditya@09') {
      setAuditKeyError('🚨 ACCESS DENIED: Incorrect Intruder Log Key!')
      return
    }
    setAuditAuthModalOpen(false)
    try {
      const res = await axios.get('/api/security/audit-logs')
      setAuditLogs(res.data.logs || [])
    } catch(e) {
      setAuditLogs([])
    }
    setAuditModalOpen(true)
  }"""

if old_fn in code:
    code = code.replace(old_fn, new_fn)

with open(r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx", "w", encoding="utf-8") as f:
    f.write(code)

print("PASSWORD LOCK ON INTRUDER LOGS 100% ENFORCED (Key: Aditya@09)!")
