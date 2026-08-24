import json, os

# 1. Update backend main.py to support full logs
backend_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py"
with open(backend_path, "r", encoding="utf-8-sig") as f:
    bcode = f.read().replace("\ufeff", "")

# Ensure log-visit stores all entries up to 500
bcode = bcode.replace("existing[:100]", "existing[:500]")
bcode = bcode.replace("logs[:100]", "logs[:500]")

with open(backend_path, "w", encoding="utf-8") as f:
    f.write(bcode)

# 2. Update frontend App.tsx to automatically log every page open
frontend_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx"
with open(frontend_path, "r", encoding="utf-8-sig") as f:
    fcode = f.read().replace("\ufeff", "")

# Add auto-log on page mount
auto_log_effect = """  // AUTO-LOG VISITOR IMMEDIATELY ON LINK OPEN
  useEffect(() => {
    const recordInitialVisit = async () => {
      try {
        const ipRes = await axios.get('https://api.ipify.org?format=json').catch(() => ({ data: { ip: 'Remote Visitor' } }))
        await axios.post('/api/security/log-visit', {
          ip: ipRes.data.ip,
          device: navigator.userAgent.substring(0, 45),
          action: '🌐 LINK_OPENED_PAGE_VISIT',
          status: 'PAGE_VIEW',
          badge: 'Remote Visitor Arrived',
          photo: ''
        })
      } catch(e) {}
    }
    recordInitialVisit()
  }, [])
"""

if "recordInitialVisit" not in fcode:
    fcode = fcode.replace(
        "  // Sync profile from server on load",
        auto_log_effect + "\n  // Sync profile from server on load"
    )

with open(frontend_path, "w", encoding="utf-8") as f:
    f.write(fcode)

print("Comprehensive visitor telemetry successfully installed!")
