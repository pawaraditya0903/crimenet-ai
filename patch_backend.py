import json, os, math
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

MASTER_SECURITY_FILE = r"c:\Users\Aditya\Downloads\SIH 2026\backend\master_security.json"
INTRUDER_LOGS_FILE = r"c:\Users\Aditya\Downloads\SIH 2026\backend\intruder_logs.json"

def get_master_data():
    if os.path.exists(MASTER_SECURITY_FILE):
        try:
            with open(MASTER_SECURITY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"password": "Aditya@4912", "face_descriptor": [], "face_photo": ""}

def save_master_data(data):
    with open(MASTER_SECURITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def log_intruder(entry):
    existing = []
    if os.path.exists(INTRUDER_LOGS_FILE):
        try:
            with open(INTRUDER_LOGS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except:
            existing = []
    existing.insert(0, entry)
    with open(INTRUDER_LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing[:100], f, indent=2)

def compute_similarity(vecA, vecB):
    if not vecA or not vecB or len(vecA) != len(vecB):
        return 0
    dot = sum(a * b for a, b in zip(vecA, vecB))
    normA = math.sqrt(sum(a * a for a in vecA))
    normB = math.sqrt(sum(b * b for b in vecB))
    if normA == 0 or normB == 0:
        return 0
    sim = dot / (normA * normB)
    return max(0, min(100, round(sim * 100)))

with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace or append security controller
if "class FaceVerifyRequest" not in code:
    endpoints = """
class FaceVerifyRequest(BaseModel):
    vector: List[int]
    photo: Optional[str] = ""
    ip: Optional[str] = "Unknown"
    device: Optional[str] = "Unknown"

class RegisterMasterFaceRequest(BaseModel):
    key: str
    vector: List[int]
    photo: Optional[str] = ""

class ChangePasswordRequest(BaseModel):
    key: str
    new_password: str

@app.post("/api/security/verify-face")
async def verify_face_endpoint(req: FaceVerifyRequest):
    master = get_master_data()
    master_vec = master.get("face_descriptor", [])
    
    if not master_vec:
        log_entry = {
            "id": str(int(datetime.now().timestamp() * 1000)),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": req.ip,
            "device": req.device,
            "action": "FACE_REJECTED_NO_MASTER_FACE",
            "status": "BLOCKED_INTRUDER",
            "badge": "Stranger Attempt",
            "photo": req.photo
        }
        log_intruder(log_entry)
        return {"authorized": False, "similarity": 0, "message": "No master face registered on server yet."}

    sim = compute_similarity(req.vector, master_vec)
    
    if sim >= 80:
        log_entry = {
            "id": str(int(datetime.now().timestamp() * 1000)),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": req.ip,
            "device": req.device,
            "action": "FACEID_MATCH_SUCCESS",
            "status": "AUTHORIZED",
            "badge": "Aditya Pawar (Chief Architect)",
            "photo": req.photo
        }
        log_intruder(log_entry)
        return {"authorized": True, "similarity": sim, "message": "IDENTITY CONFIRMED: ADITYA PAWAR"}
    else:
        log_entry = {
            "id": str(int(datetime.now().timestamp() * 1000)),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": req.ip,
            "device": req.device,
            "action": f"INTRUDER_FACE_MISMATCH_{sim}%",
            "status": "BLOCKED_INTRUDER",
            "badge": "Unauthorized Stranger",
            "photo": req.photo
        }
        log_intruder(log_entry)
        return {"authorized": False, "similarity": sim, "message": f"INTRUDER DETECTED ({sim}% match). Live photo & IP logged!"}

@app.post("/api/security/register-master-face")
async def register_master_face(req: RegisterMasterFaceRequest):
    master = get_master_data()
    if req.key.strip() != "Aditya@4912" and req.key.strip() != master.get("password"):
        return {"success": False, "message": "Invalid Master Key!"}
    master["face_descriptor"] = req.vector
    master["face_photo"] = req.photo
    save_master_data(master)
    return {"success": True, "message": "Aditya Pawar Face Profile Saved on Server!"}

@app.post("/api/security/change-password")
async def change_password_endpoint(req: ChangePasswordRequest):
    master = get_master_data()
    if req.key.strip() != "Aditya@4912" and req.key.strip() != master.get("password"):
        return {"success": False, "message": "Invalid Master Key!"}
    master["password"] = req.new_password.strip()
    save_master_data(master)
    return {"success": True, "message": "Master Password Successfully Updated!"}

@app.get("/api/security/master-profile")
async def get_master_profile():
    master = get_master_data()
    return {"has_face": len(master.get("face_descriptor", [])) > 0, "photo": master.get("face_photo", "")}
"""
    code = code + "\n" + endpoints
    with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "w", encoding="utf-8") as f:
        f.write(code)

print("Backend API ready!")
