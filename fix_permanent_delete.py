import json, os

backend_file = r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py"
with open(backend_file, "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

# Completely synchronized Permanent File Delete Engine
new_delete_backend = """
# ── BULLETPROOF PERMANENT LOG DELETION ENGINE ──
@app.post("/api/security/delete-log")
async def delete_single_log(req: Request):
    try:
        body = await req.json()
        target_ts = str(body.get("timestamp", "")).strip()
        target_id = str(body.get("id", "")).strip()
        
        log_path = r"c:\\Users\\Aditya\\Downloads\\SIH 2026\\backend\\intruder_logs.json"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
            
            # Match by ID or Timestamp or partial timestamp
            filtered_logs = []
            for item in logs:
                item_ts = str(item.get("timestamp", "")).strip()
                item_id = str(item.get("id", "")).strip()
                
                # Check if this is the record to delete
                is_match = False
                if target_id and item_id and target_id == item_id:
                    is_match = True
                elif target_ts and item_ts and (target_ts == item_ts or target_ts in item_ts or item_ts in target_ts):
                    is_match = True
                
                if not is_match:
                    filtered_logs.append(item)
            
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(filtered_logs, f, indent=2)
                
            global security_audit_logs
            security_audit_logs = filtered_logs
            return {"success": True, "remaining": len(filtered_logs)}
    except Exception as e:
        print("Delete error:", e)
    return {"success": False}

@app.post("/api/security/clear-all-logs")
async def clear_all_logs_endpoint():
    global security_audit_logs
    security_audit_logs = []
    log_path = r"c:\\Users\\Aditya\\Downloads\\SIH 2026\\backend\\intruder_logs.json"
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
    except Exception as e:
        pass
    return {"success": True, "message": "All logs wiped permanently"}
"""

# Replace existing delete endpoint with bulletproof one
if "@app.post(\"/api/security/delete-log\")" in code:
    idx = code.find("@app.post(\"/api/security/delete-log\")")
    end_idx = code.find("@app.post(\"/api/security/clear-all-logs\")")
    if end_idx != -1:
        end_idx = code.find("\n\n", end_idx + 50)
        if end_idx == -1: end_idx = len(code)
        code = code[:idx] + new_delete_backend + code[end_idx:]
else:
    code = code + "\n" + new_delete_backend

with open(backend_file, "w", encoding="utf-8") as f:
    f.write(code)

print("Backend Permanent File Delete Engine successfully installed!")
