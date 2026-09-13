import json, os

# 1. Ensure master_security.json exists
master_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\master_security.json"
if not os.path.exists(master_path):
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump({"password": "Aditya@4912", "face_descriptor": [], "face_photo": ""}, f, indent=2)

# 2. Fix backend delete API
backend_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py"
with open(backend_path, "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

# Robust timestamp-based delete
code = code.replace(
    """logs = [l for l in logs if l.get("id") != req.id and l.get("timestamp") != req.timestamp]""",
    """logs = [l for l in logs if l.get("timestamp") != req.timestamp]"""
)

with open(backend_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Backend delete engine successfully updated!")
