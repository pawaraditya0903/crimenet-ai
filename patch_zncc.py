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

# TRUE ZERO-MEAN NORMALIZED CROSS CORRELATION (ZNCC)
def compute_zncc_similarity(vecA, vecB):
    if not vecA or not vecB or len(vecA) != len(vecB):
        return 0
    
    meanA = sum(vecA) / len(vecA)
    meanB = sum(vecB) / len(vecB)
    
    normA = [a - meanA for a in vecA]
    normB = [b - meanB for b in vecB]
    
    dot = sum(a * b for a, b in zip(normA, normB))
    varA = math.sqrt(sum(a * a for a in normA))
    varB = math.sqrt(sum(b * b for b in normB))
    
    if varA == 0 or varB == 0:
        return 0
    
    # Pearson r ranges from -1.0 to +1.0
    r = dot / (varA * varB)
    if r < 0:
        return 0
    return round(r * 100)

with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace compute_similarity with compute_zncc_similarity in backend
if "def compute_similarity" in code:
    code = code.replace("sim = compute_similarity(req.vector, master_vec)", "sim = compute_zncc_similarity(req.vector, master_vec)")

with open(r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Backend ZNCC Facial Contour Engine Active!")
