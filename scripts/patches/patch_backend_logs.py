import json, os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Persistent intruder log path
LOG_FILE = r"c:\Users\Aditya\Downloads\SIH 2026\backend\intruder_logs.json"

def load_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_log_entry(entry):
    logs = load_logs()
    logs.insert(0, entry)
    # keep last 100 entries
    logs = logs[:100]
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Ensure persistent log saving in backend
if "intruder_logs.json" not in code:
    code = code.replace(
        "security_audit_logs.insert(0, entry)",
        """security_audit_logs.insert(0, entry)
    try:
        import json, os
        log_path = r"c:\\Users\\Aditya\\Downloads\\SIH 2026\\backend\\intruder_logs.json"
        existing = []
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        existing.insert(0, entry)
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(existing[:100], f, indent=2)
    except Exception as e:
        print('Error saving intruder log:', e)"""
    )
    with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "w", encoding="utf-8") as f:
        f.write(code)

print("Backend persistent intruder database patched!")
