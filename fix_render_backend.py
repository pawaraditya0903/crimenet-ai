import json, os, math
from datetime import datetime

main_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\app\main.py"
with open(main_path, "r", encoding="utf-8-sig") as f:
    code = f.read().replace("\ufeff", "")

# Master Security Helpers with cross-platform absolute paths
helpers = """
# ── CROSS-PLATFORM PERSISTENT SECURITY DATABASE ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_SECURITY_FILE = os.path.join(BASE_DIR, "..", "master_security.json")
INTRUDER_LOGS_FILE = os.path.join(BASE_DIR, "..", "intruder_logs.json")

def get_master_data():
    if os.path.exists(MASTER_SECURITY_FILE):
        try:
            with open(MASTER_SECURITY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"password": "Aditya@4912", "face_descriptor": [], "face_photo": ""}

def save_master_data(data):
    try:
        with open(MASTER_SECURITY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error saving master data:", e)

def log_intruder(entry):
    existing = []
    if os.path.exists(INTRUDER_LOGS_FILE):
        try:
            with open(INTRUDER_LOGS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.insert(0, entry)
    try:
        with open(INTRUDER_LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing[:100], f, indent=2)
    except Exception as e:
        print("Error saving intruder log:", e)

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
    r = dot / (varA * varB)
    if r < 0:
        return 0
    return round(r * 100)
"""

if "def get_master_data():" not in code:
    # Insert right after FastAPI app creation
    code = code.replace("app = FastAPI(", helpers + "\napp = FastAPI(")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Helper functions inserted cleanly into main.py!")
