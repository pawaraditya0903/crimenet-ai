import json, os

# 1. Lock Master Security DB
master_sec_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\master_security.json"
with open(master_sec_path, "w", encoding="utf-8") as f:
    json.dump({"password": "Aditya@4912", "face_descriptor": [], "face_photo": ""}, f, indent=2)

# 2. Lock Backend API
backend_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py"
if os.path.exists(backend_path):
    with open(backend_path, "r", encoding="utf-8-sig") as f:
        bcode = f.read().replace("\ufeff", "")
    bcode = bcode.replace('"aditya"', '"Aditya@4912"')
    with open(backend_path, "w", encoding="utf-8") as f:
        f.write(bcode)

# 3. Lock Frontend App.tsx
frontend_path = r"c:\Users\Aditya\Downloads\SIH 2026\frontend\src\App.tsx"
if os.path.exists(frontend_path):
    with open(frontend_path, "r", encoding="utf-8-sig") as f:
        fcode = f.read().replace("\ufeff", "")
    fcode = fcode.replace("['aditya', 'Aditya', 'ADITYA', 'aditya@4912', '2026']", "['Aditya@4912']")
    fcode = fcode.replace("['aditya@4912', 'aditya@2026', '2026', 'aditya']", "['Aditya@4912']")
    fcode = fcode.replace("['aditya@4912', 'aditya@2026', 'aditya', '2026']", "['Aditya@4912']")
    with open(frontend_path, "w", encoding="utf-8") as f:
        f.write(fcode)

print("SUCCESS: System is strictly locked to Aditya@4912!")
