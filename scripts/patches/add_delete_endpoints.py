with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

delete_code = """
class DeleteLogRequest(BaseModel):
    id: Optional[str] = ""
    timestamp: Optional[str] = ""

@app.post("/api/security/delete-log")
async def delete_single_log(req: DeleteLogRequest):
    global security_audit_logs
    if os.path.exists(INTRUDER_LOGS_FILE):
        try:
            with open(INTRUDER_LOGS_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
            logs = [l for l in logs if l.get("id") != req.id and l.get("timestamp") != req.timestamp]
            with open(INTRUDER_LOGS_FILE, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2)
            security_audit_logs = logs
        except Exception as e:
            pass
    return {"success": True, "message": "Log deleted successfully"}

@app.post("/api/security/clear-all-logs")
async def clear_all_logs_endpoint():
    global security_audit_logs
    security_audit_logs = []
    try:
        with open(INTRUDER_LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
    except Exception as e:
        pass
    return {"success": True, "message": "All logs wiped"}
"""

if "/api/security/delete-log" not in code:
    code = code + "\n" + delete_code
    with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "w", encoding="utf-8") as f:
        f.write(code)

print("Backend delete endpoints installed!")
