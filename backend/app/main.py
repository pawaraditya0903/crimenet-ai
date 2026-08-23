import json, os, math
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import socketio, json, io, urllib.request, urllib.error, urllib.parse, datetime, ssl, random
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rc

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

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

app = FastAPI(title="CrimeNet AI - Aditya Pawar Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

SYSTEM_PROMPT = "You are CrimeNet AI, an autonomous intelligence and criminal investigation copilot on Aditya Pawar's platform. You are sharp, knowledgeable, and helpful. You answer general questions naturally and provide deep forensic breakdowns for suspects, telecom numbers, and money laundering cases."

# ── MULTI-TIER LIVE GENERATIVE AI ENGINE ──
def ask_ai_intelligence(user_msg: str) -> str:
    # 1. Try Live Cloud LLM (OpenAI / LLaMA Gateway)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        url = "https://text.pollinations.ai/"
        payload = json.dumps({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            "model": "openai"
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

        with urllib.request.urlopen(req, timeout=6, context=ctx) as res:
            reply = res.read().decode("utf-8").strip()
            if reply and len(reply) > 5:
                return reply
    except Exception:
        pass

    # 2. Local Conversational & Forensic Knowledge Brain
    q = user_msg.lower().strip()
    digits = "".join(c for c in q if c.isdigit())

    # Phone Number Analysis
    if len(digits) >= 8:
        prefix = digits[:4]
        circle = "Maharashtra & Goa Circle" if prefix in ["9834","9822","9850","9823","9860","9881","9890","9762","9763","9764","9765"] else "Western Telecom Circle"
        seed = sum(int(d) for d in digits)
        risk = 72 + (seed % 26)
        return (
            f"📱 **TELECOM CDR & SUBSCRIBER DOSSIER: `{digits}`**\n\n"
            f"• **Telecom Circle:** {circle} (India)\n"
            f"• **Carrier Gateway:** Jio / Vodafone-Idea Network\n"
            f"• **Calculated Threat Level:** **{risk:.1f} / 100** [{'CRITICAL' if risk >= 85 else 'HIGH RISK'}]\n"
            f"• **Linked Dual-SIM IMEI:** `35{seed}892019482{seed%9}9`\n"
            f"• **30-Day Call Volume:** {280 + seed*3} Outbound / {190 + seed*2} Inbound\n"
            f"• **Nocturnal Call Ratio:** {(30 + (seed % 18)):.1f}% (Peak: 01:30 AM – 04:15 AM)\n"
            f"• **Active Cell Tower:** Sector Hub ID #{40400 + (seed % 50)} (19.1663° N, 72.8526° E)\n\n"
            f"📋 **Investigative Directives:**\n"
            f"1. Section 5(2) Indian Telegraph Act lawful metadata interception warrant.\n"
            f"2. Cross-reference IMEI across National CEIR Stolen/Blocked Registry.\n"
            f"3. Geofence surveillance on target tower hub."
        )

    if "priya" in q or "desai" in q:
        return (
            "👤 **SUSPECT DOSSIER: Priya Desai**\n\n"
            "• **Role:** Financial Controller & Chief Accountant\n"
            "• **Threat Score:** **74.2 / 100** [HIGH RISK]\n"
            "• **Affiliation:** Manages shell accounts for **Mehta Enterprises Ltd**\n"
            "• **Flagged Red Flag:** Authorized the ₹1.50 Cr nocturnal transfer at 02:00 AM to Phoenix Trading LLC.\n"
            "• **Action Plan:** Issue Section 91 CrPC summons for banking ledgers."
        )

    if "arjun" in q or "kingpin" in q or "bhai" in q:
        return (
            "🚨 **PRIME KINGPIN: Arjun Mehta (alias: 'Bhai')**\n\n"
            "• **Role:** Syndicate Head & Mastermind\n"
            "• **Threat Score:** **94.5 / 100** [CRITICAL THREAT]\n"
            "• **PageRank Authority:** 0.0847 (Rank #1 in entire network)\n"
            "• **Betweenness Centrality:** 0.312 (Key bridge across all cells)\n"
            "• **Controlled Shell Orgs:** Mehta Enterprises Ltd & Phoenix Trading LLC\n"
            "• **Primary Burner:** `+91-9876543210` (68-call pre-raid burst)\n"
            "• **Action Plan:** Execute 24/7 non-bailable surveillance and freeze all linked accounts under PMLA Section 17."
        )

    if "vikram" in q or "singh" in q:
        return (
            "🚚 **SUSPECT DOSSIER: Vikram Singh**\n\n"
            "• **Role:** Logistics, Transport & Warehouse Coordinator\n"
            "• **Threat Score:** **79.4 / 100** [HIGH RISK]\n"
            "• **Primary Hotspot:** **Goregaon Industrial Warehouse (Plot 47B)**\n"
            "• **Fleet Monitored:** BMW X5 (MH-01-AB-5678) & transport trucks\n"
            "• **Action Plan:** Deploy tactical surveillance unit at Goregaon Warehouse."
        )

    if "rafiq" in q or "mohammed" in q:
        return (
            "💼 **SUSPECT DOSSIER: Mohammed Rafiq**\n\n"
            "• **Role:** Primary Hawala Channel Operator (Cluster 1)\n"
            "• **Threat Score:** **88.0 / 100** [CRITICAL RISK]\n"
            "• **Front Business:** Al-Rafiq Trading Co (Dharavi hub)\n"
            "• **Modus Operandi:** Layering cash remittances and token handovers connecting Mumbai to Dubai."
        )

    if any(w in q for w in ["how are you", "how r u", "how do you do"]):
        return "I am functioning at 100% capacity! 🚀\n\nAs CrimeNet AI on Aditya Pawar's platform, I am actively monitoring 48 network nodes, 112 relationships, and real-time transaction anomalies. How can I assist your investigation today?"

    if any(w in q for w in ["who are you", "what is your name", "who made you", "who created you"]):
        return "I am **CrimeNet AI**, an autonomous criminal intelligence analysis system architected and built by **Aditya Pawar**.\n\nI specialize in graph link analysis, PageRank kingpin discovery, forensic telecom audits, and real-time investigative reasoning."

    if any(w in q for w in ["hi", "hello", "hey", "namaste"]):
        return "Hello Investigator! 👋\n\nI am CrimeNet AI, your intelligence copilot on Aditya Pawar's Platform.\n\nYou can ask me:\n• Search any suspect (e.g. *Who is Priya Desai?*, *Tell me about Vikram Singh*)\n• Investigate any phone number (e.g. `9834702432`)\n• Kingpins & PageRank rankings\n• Money laundering anomalies & case directives\n\nWhat would you like to explore?"

    if any(w in q for w in ["joke", "funny"]):
        return "Why did the forensic analyst break up with the spreadsheet? 😄\n\nBecause it had too many unresolved relations and zero chemistry!"

    # Universal intelligent response
    return (
        f"I have processed your query regarding: **'{user_msg}'**.\n\n"
        f"• **Platform Analysis:** Monitored across Aditya Pawar's intelligence graph.\n"
        f"• **Key Targets in System:** Arjun Mehta (Kingpin), Mohammed Rafiq (Hawala), Vikram Singh (Logistics), Priya Desai (Finance).\n"
        f"• **Active Alerts:** ₹1.5 Cr midnight shell transfer to Phoenix Trading LLC & 68-call telecom burst on `+91-9876543210`.\n\n"
        f"Feel free to ask for specific suspect profiles, case management directives, or type any phone number (like `9834702432`)!"
    )

# ── 48 FULL ENTITIES DATASET ──
ALL_ENTITIES = [
    {"id":"n1","name":"Arjun Mehta (Kingpin)","type":"Person","risk_score":95.0,"city":"Mumbai","role":"Syndicate Mastermind","phone":"+91-9876543210"},
    {"id":"n2","name":"Mohammed Rafiq","type":"Person","risk_score":88.0,"city":"Mumbai","role":"Hawala Channel Operator","phone":"+91-9654321098"},
    {"id":"n3","name":"Vikram Singh","type":"Person","risk_score":79.4,"city":"Mumbai","role":"Logistics & Transport Head","phone":"+91-9845678901"},
    {"id":"n4","name":"Priya Desai","type":"Person","risk_score":74.2,"city":"Mumbai","role":"Financial Controller","phone":"+91-9765432109"},
    {"id":"n5","name":"Mehta Enterprises Ltd","type":"Organization","risk_score":70.0,"city":"Mumbai","role":"Primary Shell Corporation"},
    {"id":"n6","name":"+91-9876543210","type":"PhoneNumber","risk_score":85.0,"city":"Mumbai","role":"Primary Burner Line"},
    {"id":"n7","name":"Goregaon Industrial Warehouse","type":"Location","risk_score":60.0,"city":"Mumbai","role":"Contraband Staging Hub"},
    {"id":"n8","name":"BMW X5 (MH-01-AB-5678)","type":"Vehicle","risk_score":68.0,"city":"Mumbai","role":"Syndicate Transport Vehicle"},
    {"id":"n9","name":"Phoenix Trading LLC","type":"Organization","risk_score":82.0,"city":"Dubai","role":"Offshore Hawala Layering Hub"},
    {"id":"n10","name":"Rohan Gupta","type":"Person","risk_score":65.0,"city":"Delhi","role":"Mule Account Provider"},
    {"id":"n11","name":"Al-Rafiq Trading Co","type":"Organization","risk_score":75.0,"city":"Mumbai","role":"Dharavi Cash Stash Hub"},
    {"id":"n12","name":"Suresh Patil","type":"Person","risk_score":71.0,"city":"Pune","role":"Customs Clearance Proxy"},
    {"id":"n13","name":"+91-9822019283","type":"PhoneNumber","risk_score":62.0,"city":"Pune","role":"Secondary SIM Link"},
    {"id":"n14","name":"Bandra West Safehouse","type":"Location","risk_score":58.0,"city":"Mumbai","role":"Meeting Staging Point"},
    {"id":"n15","name":"Apex Logistics Corp","type":"Organization","risk_score":64.0,"city":"Surat","role":"Container Trucking Shell"},
    {"id":"n16","name":"Truck MH-04-E-9912","type":"Vehicle","risk_score":55.0,"city":"Thane","role":"Cargo Transport Unit"},
]
for i in range(17, 49):
    types = ["Person", "PhoneNumber", "Organization", "Location", "Vehicle"]
    t = types[i % len(types)]
    ALL_ENTITIES.append({
        "id": f"n{i}",
        "name": f"Sub-Node #{i} ({t})",
        "type": t,
        "risk_score": round(45.0 + (i * 1.1) % 40, 1),
        "city": ["Mumbai", "Delhi", "Pune", "Dubai", "Surat"][i % 5],
        "role": f"Affiliated {t} operative in Layer {(i % 3) + 1}"
    })

# ── 112 RELATIONSHIPS DATASET ──
ALL_RELATIONSHIPS = [
    {"id":"e1","source":"Arjun Mehta (Kingpin)","target":"Mohammed Rafiq","label":"ASSOCIATE_OF","type":"Financial Hawala","confidence":0.95},
    {"id":"e2","source":"Arjun Mehta (Kingpin)","target":"Mehta Enterprises Ltd","label":"OWNS","type":"Corporate Ownership","confidence":0.99},
    {"id":"e3","source":"Arjun Mehta (Kingpin)","target":"+91-9876543210","label":"USES_PHONE","type":"Telecom Identity","confidence":0.98},
    {"id":"e4","source":"Vikram Singh","target":"Arjun Mehta (Kingpin)","label":"OPERATES_FOR","type":"Command Chain","confidence":0.92},
    {"id":"e5","source":"Priya Desai","target":"Mehta Enterprises Ltd","label":"MANAGES_FINANCES","type":"Account Control","confidence":0.94},
    {"id":"e6","source":"Vikram Singh","target":"Goregaon Industrial Warehouse","label":"SPOTTED_AT","type":"Geospatial Sighting","confidence":0.89},
    {"id":"e7","source":"Vikram Singh","target":"BMW X5 (MH-01-AB-5678)","label":"DRIVES","type":"Asset Usage","confidence":0.91},
    {"id":"e8","source":"Mehta Enterprises Ltd","target":"Phoenix Trading LLC","label":"TRANSACTED_WITH","type":"₹1.5 Cr Wire Transfer","confidence":0.96},
    {"id":"e9","source":"Mohammed Rafiq","target":"Al-Rafiq Trading Co","label":"CONTROLS","type":"Front Operation","confidence":0.95},
    {"id":"e10","source":"Priya Desai","target":"Phoenix Trading LLC","label":"AUTHORISED_PAYMENT","type":"Midnight Shell Structuring","confidence":0.94},
]
rel_types = ["ASSOCIATE_OF", "TRANSACTED_WITH", "CALLED", "COORDINATES_WITH", "LOCATED_NEAR", "USES_VEHICLE"]
for j in range(11, 113):
    src = ALL_ENTITIES[j % len(ALL_ENTITIES)]["name"]
    tgt = ALL_ENTITIES[(j * 3 + 1) % len(ALL_ENTITIES)]["name"]
    ALL_RELATIONSHIPS.append({
        "id": f"e{j}",
        "source": src,
        "target": tgt,
        "label": rel_types[j % len(rel_types)],
        "type": f"Layer {(j%3)+1} Interaction",
        "confidence": round(0.70 + (j % 28) * 0.01, 2)
    })

SUSPECTS = [
    {"id":"1","name":"Arjun Mehta (Kingpin)","risk_score":94.5,"pagerank":0.0847,"betweenness":0.312,"community":1,"degree":0.42,"role":"Syndicate Mastermind","phone":"+91-9876543210","location":"Juhu / Goregaon"},
    {"id":"2","name":"Mohammed Rafiq","risk_score":88.0,"pagerank":0.0712,"betweenness":0.285,"community":1,"degree":0.38,"role":"Hawala Channel Operator","phone":"+91-9654321098","location":"Dharavi"},
    {"id":"3","name":"Vikram Singh","risk_score":79.4,"pagerank":0.0594,"betweenness":0.198,"community":2,"degree":0.29,"role":"Logistics & Transport Head","phone":"+91-9845678901","location":"Goregaon Industrial Area"},
    {"id":"4","name":"Priya Desai","risk_score":74.2,"pagerank":0.0511,"betweenness":0.165,"community":2,"degree":0.25,"role":"Financial Controller","phone":"+91-9765432109","location":"Bandra West"},
    {"id":"5","name":"Mehta Enterprises Ltd","risk_score":70.0,"pagerank":0.0482,"betweenness":0.142,"community":1,"degree":0.22,"role":"Primary Shell Corporation","location":"Nariman Point"},
]

ANOMALIES = [
    {"id":"a1","severity":"critical","entity_name":"Arjun Mehta","entity_type":"Person","anomaly_type":"LARGE_FINANCIAL_SPIKE","details":"₹1.50 Crore midnight transfer at 02:00 AM to Phoenix Trading LLC (Isolation Forest Score: 0.96)","anomaly_score":0.96,"timestamp":"2024-03-13 02:00:14"},
    {"id":"a2","severity":"critical","entity_name":"+91-9876543210","entity_type":"PhoneNumber","anomaly_type":"CDR_BURST_ACTIVITY","details":"68 outbound calls in 180 minutes prior to raid event (Z-Score: 4.8 Sigma above baseline)","anomaly_score":0.92,"timestamp":"2024-03-13 21:30:00"},
    {"id":"a3","severity":"high","entity_name":"Mehta Enterprises Ltd","entity_type":"Organization","anomaly_type":"CIRCULAR_TRANSACTIONS","details":"Round-tripping ₹8.75 Cr across 3 shell corporate accounts within 24 hours (Modularity Score: 0.84)","anomaly_score":0.84,"timestamp":"2024-03-12 18:45:22"},
    {"id":"a4","severity":"high","entity_name":"BMW X5 (MH-01-AB-5678)","entity_type":"Vehicle","anomaly_type":"ANPR_TOLL_DEVIATION","details":"Crossed 4 inter-state toll plazas between 01:00 AM - 04:00 AM with transponder disabled","anomaly_score":0.78,"timestamp":"2024-03-11 03:22:10"},
]

INVESTIGATORS = [
    {"id":"inv-1","name":"Aditya Pawar","email":"aditya@crimenet.ai","badge":"INV-2026-AP01","role":"Lead System Architect & Chief Investigator","clearance":"Top Secret / Level 5","skills":["Network Link Analysis","Graph ML Architecture","PMLA Financial Forensics","Tactical Command"]},
    {"id":"inv-2","name":"Rahul Sharma","email":"rahul@crimenet.ai","badge":"INV-2026-RS02","role":"Senior Cyber Intelligence Analyst","clearance":"Secret / Level 4","skills":["Telecom CDR Triangulation","IMEI/IMSI Tracking","OSINT Scraping","CEIR Registry Audit"]},
    {"id":"inv-3","name":"Sneha Kulkarni","email":"sneha@crimenet.ai","badge":"INV-2026-SK03","role":"Forensic Financial Auditor","clearance":"Secret / Level 4","skills":["Shell Company Layering","Banking Swift/RTGS Audit","Hawala Token Decryption","Benami Asset Tracing"]},
    {"id":"inv-4","name":"Vikramaditya Rao","email":"vikram@crimenet.ai","badge":"INV-2026-VR04","role":"Tactical Field Operations Commander","clearance":"Top Secret / Level 5","skills":["Armed Raid Coordination","ANPR Vehicle Tracking","Surveillance Geofencing","Informant Handling"]},
]

@app.get("/health")
async def health():
    return {"status":"online","ai_engine":"full_generative_active","platform":"Aditya Pawar Intelligence Platform"}

@app.get("/api/graph/network")
async def get_network():
    return {
        "elements": [
            {"data": {"id": "n1", "label": "Arjun Mehta (Kingpin)", "type": "Person", "risk_score": 95, "community": 1}},
            {"data": {"id": "n2", "label": "Mohammed Rafiq", "type": "Person", "risk_score": 88, "community": 1}},
            {"data": {"id": "n3", "label": "Vikram Singh", "type": "Person", "risk_score": 79, "community": 2}},
            {"data": {"id": "n4", "label": "Priya Desai", "type": "Person", "risk_score": 74, "community": 2}},
            {"data": {"id": "n5", "label": "Mehta Enterprises", "type": "Organization", "risk_score": 70, "community": 1}},
            {"data": {"id": "n6", "label": "+91-9876543210", "type": "PhoneNumber", "risk_score": 85, "community": 1}},
            {"data": {"id": "n7", "label": "Goregaon Warehouse", "type": "Location", "risk_score": 60, "community": 2}},
            {"data": {"id": "e1", "source": "n1", "target": "n2", "label": "ASSOCIATE_OF"}},
            {"data": {"id": "e2", "source": "n1", "target": "n5", "label": "OWNS"}},
            {"data": {"id": "e3", "source": "n1", "target": "n6", "label": "USES_PHONE"}},
            {"data": {"id": "e4", "source": "n3", "target": "n1", "label": "OPERATES_FOR"}},
            {"data": {"id": "e5", "source": "n4", "target": "n5", "label": "MANAGES_FINANCES"}},
            {"data": {"id": "e6", "source": "n3", "target": "n7", "label": "SPOTTED_AT"}},
        ]
    }

@app.get("/api/analytics/top-influencers")
async def influencers():
    return {"influencers": SUSPECTS}

@app.get("/api/analytics/anomalies")
async def anomalies():
    return {"summary":{"total":len(ANOMALIES),"critical":2,"high":2},"anomalies": ANOMALIES}

@app.get("/api/analytics/communities")
async def communities():
    return {
        "communities":[
            {"community_id":1,"name":"Hawala & Money Laundering Syndicate","color":"#ef4444","size":3,"members":[{"id":"1","name":"Arjun Mehta","risk_score":94.5},{"id":"2","name":"Mohammed Rafiq","risk_score":88.0},{"id":"5","name":"Mehta Enterprises Ltd","risk_score":70.0}]},
            {"community_id":2,"name":"Logistics & Contraband Distribution Cell","color":"#f97316","size":2,"members":[{"id":"3","name":"Vikram Singh","risk_score":79.4},{"id":"4","name":"Priya Desai","risk_score":74.2}]},
        ]
    }

@app.get("/api/analytics/network-stats")
async def stats():
    return {
        "total_nodes": len(ALL_ENTITIES),
        "total_edges": len(ALL_RELATIONSHIPS),
        "density": 0.0496,
        "weakly_connected_components": 3,
        "average_degree": 4.66,
        "max_degree": 14,
        "average_clustering": 0.428,
        "diameter": 5
    }

@app.get("/api/entities/all")
async def get_all_entities():
    return {"entities": ALL_ENTITIES, "total": len(ALL_ENTITIES)}

@app.get("/api/relationships/all")
async def get_all_relationships():
    return {"relationships": ALL_RELATIONSHIPS, "total": len(ALL_RELATIONSHIPS)}

# ── LIVE CHAT ENDPOINT ──
@app.post("/api/chat/message")
async def chat(data: dict):
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return {"response": "Please enter a message or suspect query.", "cypher_query": ""}
    
    reply = ask_ai_intelligence(user_msg)
    return {"response": reply, "cypher_query": "MATCH (n) RETURN n LIMIT 50"}

# ── 4 SPECIALIZED PDF GENERATORS ──
@app.post("/api/reports/generate")
async def generate_pdf(data: dict):
    template = data.get("template", "full").lower()
    entity_type = data.get("entity_type", "Person")
    target_id = str(data.get("entity_id", "Aditya Pawar")).strip()
    now_str = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S IST")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    if template == "full":
        story.append(Paragraph("CONFIDENTIAL // COMPREHENSIVE CRIMINAL PROFILE DOSSIER", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=15, textColor=rc.HexColor('#0f172a'))))
        story.append(Paragraph(f"CrimeNet AI Forensic Engine · Platform Owner: <b>Aditya Pawar</b> · Generated: {now_str}", ParagraphStyle('Sub', fontName='Helvetica', fontSize=9, textColor=rc.HexColor('#64748b'))))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=rc.HexColor('#1d4ed8'), spaceAfter=14))
        story.append(Table([
            ["TARGET SUBJECT", target_id],
            ["KNOWN ALIASES", "Bhai, AJ, MD-01"],
            ["CLASSIFICATION", entity_type.upper()],
            ["THREAT ASSESSMENT", "CRITICAL SYNDICATE MASTERMIND (94.5 / 100)"],
            ["ACTIVE JURISDICTION", "Special Crime Branch / Enforcement Directorate"],
        ], colWidths=[180, 340], style=TableStyle([
            ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#f1f5f9')),
            ('BACKGROUND', (1,0), (1,-1), rc.HexColor('#ffffff')),
            ('TEXTCOLOR', (0,0), (-1,-1), rc.HexColor('#0f172a')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('GRID', (0,0), (-1,-1), 1, rc.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ])))
        story.append(Spacer(1, 14))
        story.append(Paragraph("JUDICIAL DIRECTIVES & WARRANT RECOMMENDATIONS", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=11, textColor=rc.HexColor('#1d4ed8'))))
        story.append(Spacer(1, 6))
        story.append(Paragraph("1. Issue 24/7 non-bailable surveillance order under Section 5(2) Indian Telegraph Act.", ParagraphStyle('B', fontName='Helvetica', fontSize=9, leading=13)))
        story.append(Paragraph("2. Freeze all accounts linked to Mehta Enterprises Ltd under PMLA Section 17.", ParagraphStyle('B', fontName='Helvetica', fontSize=9, leading=13)))

    elif template == "network":
        story.append(Paragraph("TOPOLOGY AUDIT // GRAPH CENTRALITY & MODULARITY REPORT", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=15, textColor=rc.HexColor('#0f172a'))))
        story.append(Paragraph(f"Graph Analytics Engine · Platform Owner: <b>Aditya Pawar</b> · Generated: {now_str}", ParagraphStyle('Sub', fontName='Helvetica', fontSize=9, textColor=rc.HexColor('#64748b'))))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=rc.HexColor('#2563eb'), spaceAfter=14))
        story.append(Table([
            ["EVALUATED NODE", target_id],
            ["GLOBAL PAGERANK", "0.0847 (RANK #1 / TOP 1%)"],
            ["BETWEENNESS CENTRALITY", "0.312 (CRITICAL BRIDGE BROKER)"],
            ["COMMUNITY CLUSTER", "Cluster 1 (Hawala & Laundering Cell)"],
            ["MODULARITY COEFFICIENT", "Q = 0.684 (High Subgraph Cohesion)"],
        ], colWidths=[180, 340], style=TableStyle([
            ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#eff6ff')),
            ('BACKGROUND', (1,0), (1,-1), rc.HexColor('#ffffff')),
            ('TEXTCOLOR', (0,0), (-1,-1), rc.HexColor('#0f172a')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('GRID', (0,0), (-1,-1), 1, rc.HexColor('#bfdbfe')),
            ('PADDING', (0,0), (-1,-1), 5),
        ])))

    elif template == "risk":
        story.append(Paragraph("THREAT ASSESSMENT // ISOLATION FOREST ANOMALY REPORT", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=15, textColor=rc.HexColor('#991b1b'))))
        story.append(Paragraph(f"Unsupervised ML Anomaly Engine · Platform Owner: <b>Aditya Pawar</b> · Generated: {now_str}", ParagraphStyle('Sub', fontName='Helvetica', fontSize=9, textColor=rc.HexColor('#64748b'))))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=rc.HexColor('#dc2626'), spaceAfter=14))
        story.append(Table([
            ["TARGET UNDER SCAN", target_id],
            ["AGGREGATE RISK INDEX", "CRITICAL RISK LEVEL (94.5 / 100)"],
            ["ISOLATION FOREST SCORE", "0.96 (CRITICAL OUTLIER SPIKE)"],
            ["TELECOM BURST Z-SCORE", "4.8 Sigma Deviation (Pre-Raid Alert)"],
            ["CIRCULAR FRAUD DETECTED", "₹8.75 Crore Round-Tripping Flow"],
        ], colWidths=[180, 340], style=TableStyle([
            ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#fef2f2')),
            ('BACKGROUND', (1,0), (1,-1), rc.HexColor('#ffffff')),
            ('TEXTCOLOR', (0,0), (-1,-1), rc.HexColor('#991b1b')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('GRID', (0,0), (-1,-1), 1, rc.HexColor('#fca5a5')),
            ('PADDING', (0,0), (-1,-1), 5),
        ])))

    else:
        story.append(Paragraph("TELECOM FORENSICS // CDR & SUBSCRIBER TIMELINE REPORT", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=15, textColor=rc.HexColor('#0f172a'))))
        story.append(Paragraph(f"Cellular & IMSI Forensics · Platform Owner: <b>Aditya Pawar</b> · Generated: {now_str}", ParagraphStyle('Sub', fontName='Helvetica', fontSize=9, textColor=rc.HexColor('#64748b'))))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=rc.HexColor('#d97706'), spaceAfter=14))
        story.append(Table([
            ["TARGET MSISDN / PHONE", target_id],
            ["PRIMARY IMEI LINKED", "354892019482019 (Dual SIM Device)"],
            ["TELECOM CIRCLE", "Maharashtra & Goa Circle (India)"],
            ["NOCTURNAL CALL RATIO", "42.8% (Peak Calling: 01:30 AM - 04:15 AM)"],
            ["PRIMARY CELL TOWER HUB", "Tower ID #404-45-1920 (19.1663° N, 72.8526° E)"],
        ], colWidths=[180, 340], style=TableStyle([
            ('BACKGROUND', (0,0), (0,-1), rc.HexColor('#fffbeb')),
            ('BACKGROUND', (1,0), (1,-1), rc.HexColor('#ffffff')),
            ('TEXTCOLOR', (0,0), (-1,-1), rc.HexColor('#92400e')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('GRID', (0,0), (-1,-1), 1, rc.HexColor('#fde68a')),
            ('PADDING', (0,0), (-1,-1), 5),
        ])))

    doc.build(story)
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=CrimeNet_{template.upper()}_{target_id.replace(' ','_')}.pdf"}
    )

@app.get("/api/investigators")
async def list_investigators():
    return {"investigators": INVESTIGATORS, "total": len(INVESTIGATORS)}

@app.post("/api/investigators")
async def add_investigator(data: dict):
    new_inv = {
        "id": f"inv-{len(INVESTIGATORS) + 1}",
        "name": data.get("name", "New Investigator"),
        "email": data.get("email", "investigator@crimenet.ai"),
        "badge": data.get("badge", f"INV-2026-0{len(INVESTIGATORS)+1}"),
        "role": data.get("role", "Field Intelligence Officer"),
        "clearance": data.get("clearance", "Secret / Level 4"),
        "skills": data.get("skills", ["Field Investigation", "Surveillance"])
    }
    INVESTIGATORS.append(new_inv)
    return {"status": "success", "investigator": new_inv}

@app.delete("/api/investigators/{inv_id}")
async def delete_investigator(inv_id: str):
    global INVESTIGATORS
    INVESTIGATORS = [i for i in INVESTIGATORS if i["id"] != inv_id]
    return {"status": "deleted", "id": inv_id}

@app.get("/api/alerts")
async def get_alerts():
    return {"alerts": ANOMALIES, "stats": {"total": len(ANOMALIES), "critical": 2, "high": 2, "unacknowledged": 2}}

@app.post("/api/alerts/{alert_id}/acknowledge")
async def ack_alert(alert_id: str):
    return {"status": "acknowledged", "id": alert_id}

@app.get("/api/cases")
async def get_cases():
    return {"cases": [
        {"id":"c1","title":"Operation Blue Thunder","description":"Cross-border narcotics & hawala ring","status":"investigating","priority":"critical","suspects":["Arjun Mehta","Mohammed Rafiq","Vikram Singh"],"created_at":"2024-03-01"},
        {"id":"c2","title":"Mehta Enterprises Layering Audit","description":"Offshore shell corporate money structuring","status":"open","priority":"high","suspects":["Priya Desai","Arjun Mehta"],"created_at":"2024-03-05"},
    ]}

@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    return {"id":case_id,"title":"Operation Blue Thunder","description":"Cross-border hawala syndicate","status":"investigating","priority":"critical","comments":[{"id":"cm1","content":"Raid executed at Goregaon. 3 operatives detained.","created_at":"2024-03-13 23:00:00"}],"created_at":"2024-03-01"}

@app.post("/api/cases")
async def create_case(data: dict):
    return {"id":f"c-{random.randint(100,999)}","title":data.get("title","New Case"),"status":"open","priority":data.get("priority","high"),"comments":[],"created_at":"2024-03-14"}

@app.post("/api/cases/{case_id}/comments")
async def add_comment(case_id: str, data: dict):
    return {"id":f"cm-{random.randint(100,999)}","content":data.get("content",""),"created_at":"2024-03-14 01:00:00"}

@app.get("/api/auth/users")
async def list_users():
    return [
        {"id":"u1","username":"admin","full_name":"Aditya Pawar","email":"aditya@crimenet.ai","role":"Lead Investigator","is_active":True},
        {"id":"u2","username":"analyst1","full_name":"Rahul Sharma","email":"rahul@crimenet.ai","role":"Intelligence Analyst","is_active":True},
    ]

socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# ── INTRUSION & VISITOR AUDIT LOG STORAGE ──
ACCESS_LOGS = []

@app.post("/api/security/log-visit")
async def log_visit(data: dict):
    log_entry = {
        "id": f"log-{len(ACCESS_LOGS) + 1}",
        "timestamp": datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S IST"),
        "ip": data.get("ip", "Remote User"),
        "device": data.get("device", "Mobile / Browser Device"),
        "action": data.get("action", "PAGE_VISIT"),
        "status": data.get("status", "UNAUTHORIZED"),
        "badge": data.get("badge", "Anonymous Visitor"),
        "photo": data.get("photo", "")
    }
    ACCESS_LOGS.insert(0, log_entry)
    return {"status": "logged", "total_logs": len(ACCESS_LOGS)}

@app.get("/api/security/audit-logs")
async def get_audit_logs():
    return {"logs": ACCESS_LOGS, "total": len(ACCESS_LOGS)}


# ── SERVER-SIDE BIOMETRIC & SECURITY CONTROLLER ──
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
    
    # If no face enrolled yet on server, strictly deny
    if not master_vec:
        log_entry = {
            "id": str(int(datetime.now().timestamp() * 1000)),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": req.ip,
            "device": req.device,
            "action": "FACE_REJECTED_NO_MASTER_ENROLLED",
            "status": "BLOCKED_INTRUDER",
            "badge": "Stranger Scan",
            "photo": req.photo
        }
        log_intruder(log_entry)
        return {"authorized": False, "similarity": 0, "message": "No Master Face Registered Yet! Login via Passcode Aditya@4912 to register."}

    sim = compute_similarity(req.vector, master_vec)
    
    # Strict 82% threshold against Aditya's face
    if sim >= 82:
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
        # Stranger detected! Log photo and block!
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
    return {"success": True, "message": "Aditya Pawar Master Face Profile Successfully Saved on Server!"}

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


class DeleteLogRequest(BaseModel):
    id: Optional[str] = ""
    timestamp: Optional[str] = ""


# ── BULLETPROOF PERMANENT LOG DELETION ENGINE ──
@app.post("/api/security/delete-log")
async def delete_single_log(req: Request):
    try:
        body = await req.json()
        target_ts = str(body.get("timestamp", "")).strip()
        target_id = str(body.get("id", "")).strip()
        
        log_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\intruder_logs.json"
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
    log_path = r"c:\Users\Aditya\Downloads\SIH 2026\backend\intruder_logs.json"
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
    except Exception as e:
        pass
    return {"success": True, "message": "All logs wiped permanently"}


# ── SERVE FRONTEND SPA IN PRODUCTION ──
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
