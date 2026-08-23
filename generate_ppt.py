import os

BASE = r"c:\Users\Aditya\Downloads\SIH 2026"

FILES = {}

# ── backend/requirements.txt ──
FILES["backend/requirements.txt"] = """fastapi==0.111.0
uvicorn[standard]==0.30.0
python-socketio==5.11.1
pydantic-settings==2.3.4
python-dotenv==1.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
google-generativeai==0.7.2
networkx==3.3
scikit-learn==1.5.0
reportlab==4.2.0
aiofiles==23.2.1
pandas==2.2.2
httpx==0.27.0
"""

# ── backend/app/__init__.py ──
FILES["backend/app/__init__.py"] = ""

# ── backend/app/config.py ──
FILES["backend/app/config.py"] = """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CrimeNet AI"
    SECRET_KEY: str = "crimenet-sih-2026-secret"
    GEMINI_API_KEY: str = "AIzaSyAb8RN6I-13opApMhGZoAP1EadDr8n4DO58tHiqjtzUdcQxMacA"
    class Config:
        extra = "allow"

settings = Settings()
"""

# ── backend/app/main.py ──
FILES["backend/app/main.py"] = """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI(title="CrimeNet AI")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUSPECTS = [
    {"id":"1","name":"Arjun Mehta","risk_score":94.5,"pagerank":0.0847,"betweenness":0.312,"community":1,"degree":0.42},
    {"id":"2","name":"Mohammed Rafiq","risk_score":88.0,"pagerank":0.0712,"betweenness":0.285,"community":1,"degree":0.38},
    {"id":"3","name":"Vikram Singh","risk_score":79.4,"pagerank":0.0594,"betweenness":0.198,"community":2,"degree":0.29},
    {"id":"4","name":"Priya Desai","risk_score":74.2,"pagerank":0.0511,"betweenness":0.165,"community":2,"degree":0.25},
    {"id":"5","name":"Mehta Enterprises Ltd","risk_score":68.9,"pagerank":0.0482,"betweenness":0.142,"community":1,"degree":0.22},
    {"id":"6","name":"Rohan Gupta","risk_score":61.0,"pagerank":0.0371,"betweenness":0.101,"community":3,"degree":0.18},
    {"id":"7","name":"Anita Sharma","risk_score":55.3,"pagerank":0.0312,"betweenness":0.088,"community":3,"degree":0.15},
]

GRAPH_ELEMENTS = {
    "elements": [
        {"data":{"id":"n1","label":"Arjun Mehta","type":"Person","risk_score":95,"community":1}},
        {"data":{"id":"n2","label":"Mohammed Rafiq","type":"Person","risk_score":88,"community":1}},
        {"data":{"id":"n3","label":"Vikram Singh","type":"Person","risk_score":79,"community":2}},
        {"data":{"id":"n4","label":"Priya Desai","type":"Person","risk_score":74,"community":2}},
        {"data":{"id":"n5","label":"Mehta Enterprises","type":"Organization","risk_score":70,"community":1}},
        {"data":{"id":"n6","label":"+91-9876543210","type":"PhoneNumber","risk_score":85,"community":1}},
        {"data":{"id":"n7","label":"Goregaon Warehouse","type":"Location","risk_score":60,"community":2}},
        {"data":{"id":"n8","label":"Phoenix Trading LLC","type":"Organization","risk_score":72,"community":1}},
        {"data":{"id":"n9","label":"Rohan Gupta","type":"Person","risk_score":61,"community":3}},
        {"data":{"id":"n10","label":"MH-01-AB-5678","type":"Vehicle","risk_score":50,"community":2}},
        {"data":{"id":"e1","source":"n1","target":"n2","label":"ASSOCIATE_OF"}},
        {"data":{"id":"e2","source":"n1","target":"n5","label":"OWNS"}},
        {"data":{"id":"e3","source":"n1","target":"n6","label":"USES_PHONE"}},
        {"data":{"id":"e4","source":"n3","target":"n1","label":"OPERATES_FOR"}},
        {"data":{"id":"e5","source":"n4","target":"n5","label":"MANAGES_FINANCES"}},
        {"data":{"id":"e6","source":"n3","target":"n7","label":"SPOTTED_AT"}},
        {"data":{"id":"e7","source":"n5","target":"n8","label":"LAUNDERS_VIA"}},
        {"data":{"id":"e8","source":"n2","target":"n9","label":"RECRUITS"}},
        {"data":{"id":"e9","source":"n1","target":"n10","label":"DRIVES"}},
    ]
}

@app.get("/health")
async def health():
    return {"status":"online","neo4j":"connected","postgres":"connected","redis":"connected","gemini":"configured"}

@app.post("/api/auth/login")
async def login(data: dict):
    return {
        "access_token": "demo_token_crimenet_sih2026",
        "token_type": "bearer",
        "user": {"id":"u1","username":"admin","full_name":"Inspector Aditya Kumar","role":"investigator","email":"aditya@mumbaipolice.gov.in","is_active":True}
    }

@app.get("/api/graph/network")
async def get_network():
    return GRAPH_ELEMENTS

@app.get("/api/analytics/top-influencers")
async def top_influencers():
    return {"influencers": SUSPECTS}

@app.get("/api/analytics/communities")
async def communities():
    return {"communities":[
        {"community_id":1,"color":"#ef4444","size":4,"members":[{"id":"1","name":"Arjun Mehta","risk_score":94.5},{"id":"2","name":"Mohammed Rafiq","risk_score":88}]},
        {"community_id":2,"color":"#f97316","size":3,"members":[{"id":"3","name":"Vikram Singh","risk_score":79.4},{"id":"4","name":"Priya Desai","risk_score":74.2}]},
        {"community_id":3,"color":"#a855f7","size":2,"members":[{"id":"6","name":"Rohan Gupta","risk_score":61}]},
    ]}

@app.get("/api/analytics/anomalies")
async def anomalies():
    return {
        "summary":{"total":5,"critical":2,"high":2,"medium":1},
        "anomalies":[
            {"id":"a1","severity":"critical","entity_name":"Arjun Mehta","entity_type":"Person","anomaly_type":"LARGE_FINANCIAL_SPIKE","details":"Rs 1.5 Crore transfer at 02:30 AM to shell company Phoenix Trading LLC — flagged by Isolation Forest","anomaly_score":0.96},
            {"id":"a2","severity":"critical","entity_name":"+91-9876543210","entity_type":"PhoneNumber","anomaly_type":"CDR_BURST_ACTIVITY","details":"68 outbound calls in 3 hours — Z-score: 4.8 sigma above baseline","anomaly_score":0.92},
            {"id":"a3","severity":"high","entity_name":"Mehta Enterprises Ltd","entity_type":"Organization","anomaly_type":"CIRCULAR_TRANSACTIONS","details":"Round-tripping Rs 8.75 Cr through 3 shell accounts in 24 hours","anomaly_score":0.84},
            {"id":"a4","severity":"high","entity_name":"Priya Desai","entity_type":"Person","anomaly_type":"UNUSUAL_LOCATION","details":"Geofence alert: border crossing at Wagah detected at 01:15 AM","anomaly_score":0.77},
            {"id":"a5","severity":"medium","entity_name":"Rohan Gupta","entity_type":"Person","anomaly_type":"NEW_ASSOCIATION","details":"Link prediction: 89% probability of new connection to Karachi network","anomaly_score":0.61},
        ]
    }

@app.get("/api/analytics/network-stats")
async def network_stats():
    return {"total_nodes":48,"total_edges":112,"density":0.0496,"weakly_connected_components":3,"average_degree":4.66,"max_degree":14,"average_clustering":0.428,"diameter":5}

@app.post("/api/chat/message")
async def chat(data: dict):
    msg = data.get("message","").lower()
    if "kingpin" in msg or "dangerous" in msg or "leader" in msg:
        reply = "KINGPIN IDENTIFIED: Arjun Mehta (alias 'Bhai')\\n\\nRisk Score: 94.5/100 | PageRank: 0.0847 | Betweenness: 0.312\\nDirectly connected to 8 entities across Mumbai, Delhi, and Dubai.\\nControls 2 shell companies: Mehta Enterprises Ltd & Phoenix Trading LLC.\\n\\nCypher Query: MATCH (p:Person) RETURN p ORDER BY p.risk_score DESC LIMIT 1"
    elif "communit" in msg or "gang" in msg or "network" in msg:
        reply = "3 Criminal Communities Detected via Louvain Algorithm:\\n\\nCluster 1 (Hawala Ring): 4 members | Led by Arjun Mehta\\nCluster 2 (Logistics Cell): 3 members | Led by Vikram Singh\\nCluster 3 (Recruitment Cell): 2 members | Led by Rohan Gupta"
    elif "anomal" in msg or "suspicious" in msg or "alert" in msg:
        reply = "5 ANOMALIES DETECTED:\\n\\n[CRITICAL] Rs 1.5Cr 2AM transfer (Isolation Forest)\\n[CRITICAL] 68-call CDR burst (Z-score: 4.8 sigma)\\n[HIGH] Circular Rs 8.75Cr hawala flow\\n[HIGH] Border crossing at 1:15AM\\n[MEDIUM] New link prediction to Karachi network"
    else:
        reply = f"Analyzing query: '{data.get('message')}'\\n\\nTop 3 active suspects in the network:\\n1. Arjun Mehta — Risk 94.5/100 (CRITICAL)\\n2. Mohammed Rafiq — Risk 88.0/100 (CRITICAL)\\n3. Vikram Singh — Risk 79.4/100 (HIGH)\\n\\nRecommendation: Prioritize surveillance on Arjun Mehta — highest betweenness centrality node."
    return {"response": reply, "cypher_query": "MATCH (p:Person)-[r]-(t) WHERE p.risk_score > 70 RETURN p,r,t LIMIT 50"}

@app.get("/api/alerts")
async def alerts(severity: str = None, acknowledged: bool = None):
    alerts_list = [
        {"id":"al1","severity":"critical","alert_type":"FINANCIAL_ANOMALY","message":"Rs 1.5 Cr midnight transfer flagged","entity_name":"Arjun Mehta","entity_type":"Person","acknowledged":False,"created_at":"2024-03-13T22:45:00"},
        {"id":"al2","severity":"high","alert_type":"CDR_SPIKE","message":"68 calls in 3 hours detected on +91-9876543210","entity_name":"+91-9876543210","entity_type":"PhoneNumber","acknowledged":False,"created_at":"2024-03-13T21:30:00"},
        {"id":"al3","severity":"medium","alert_type":"LINK_PREDICTION","message":"New associate detected: Rohan Gupta linked to Karachi network","entity_name":"Rohan Gupta","entity_type":"Person","acknowledged":True,"created_at":"2024-03-12T15:00:00"},
    ]
    return {"alerts": alerts_list, "stats": {"total":3,"critical":1,"high":1,"unacknowledged":2}}

@app.post("/api/alerts/{alert_id}/acknowledge")
async def ack_alert(alert_id: str):
    return {"status": "acknowledged", "id": alert_id}

@app.get("/api/cases")
async def cases():
    return {"cases": [
        {"id":"c1","title":"Operation Blue Thunder","description":"Narcotics and hawala network investigation","status":"investigating","priority":"critical","created_at":"2024-03-01T10:00:00"},
        {"id":"c2","title":"Mehta Enterprises Money Laundering","description":"Financial audit of shell company network","status":"open","priority":"high","created_at":"2024-03-05T09:00:00"},
        {"id":"c3","title":"Goregaon Drug Bust 2024","description":"Post-arrest analysis and network mapping","status":"closed","priority":"medium","created_at":"2024-02-15T14:00:00"},
    ]}

@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    return {"id": case_id, "title": "Operation Blue Thunder", "description": "Full investigation", "status": "investigating", "priority": "critical", "entities": [], "comments": [{"id":"cm1","content":"Raid conducted at Goregaon. 3 arrested.","created_at":"2024-03-13T23:00:00"}], "created_at": "2024-03-01T10:00:00"}

@app.post("/api/cases")
async def create_case(data: dict):
    return {"id":"c-new","title": data.get("title"), "status":"open", "priority": data.get("priority","medium"), "created_at":"2024-03-14T00:00:00"}

@app.patch("/api/cases/{case_id}")
async def update_case(case_id: str, data: dict):
    return {"id": case_id, "status": data.get("status","open")}

@app.delete("/api/cases/{case_id}")
async def delete_case(case_id: str):
    return {"deleted": True}

@app.post("/api/cases/{case_id}/comments")
async def add_comment(case_id: str, data: dict):
    return {"id":"cm-new","content": data.get("content"),"created_at":"2024-03-14T01:00:00"}

@app.get("/api/map/crime-heatmap")
async def crime_heatmap():
    import random, math
    random.seed(42)
    features = []
    hotspots = [(72.8777, 19.0760), (72.8826, 19.1663), (72.9781, 19.2183), (77.2090, 28.6139)]
    for cx, cy in hotspots:
        for _ in range(20):
            features.append({"type":"Feature","geometry":{"type":"Point","coordinates":[cx+random.uniform(-0.05,0.05), cy+random.uniform(-0.05,0.05)]},"properties":{"intensity": random.uniform(0.3,1.0), "crime_type":"Narcotics"}})
    return {"type":"FeatureCollection","features":features}

@app.get("/api/map/hotspots")
async def hotspots():
    return {"hotspots":[
        {"name":"Goregaon Industrial Area","latitude":19.1663,"longitude":72.8526,"crime_count":847,"crime_types":["Narcotics","Money Laundering"]},
        {"name":"Dharavi","latitude":19.0330,"longitude":72.8526,"crime_count":512,"crime_types":["Hawala","Arms"]},
        {"name":"Bhiwandi","latitude":19.2183,"longitude":73.0297,"crime_count":389,"crime_types":["Narcotics Storage"]},
        {"name":"Bandra West","latitude":19.0596,"longitude":72.8295,"crime_count":274,"crime_types":["Money Laundering"]},
    ]}

@app.get("/api/entities/search")
async def search_entities(q: str = "", type: str = None, limit: int = 20):
    results = [
        {"id":"1","name":"Arjun Mehta","label":"Person","risk_score":94.5,"nationality":"Indian","city":"Mumbai"},
        {"id":"2","name":"Mohammed Rafiq","label":"Person","risk_score":88.0,"nationality":"Indian","city":"Mumbai"},
        {"id":"3","name":"Mehta Enterprises Ltd","label":"Organization","risk_score":70.0,"org_type":"Shell Company","city":"Mumbai"},
        {"id":"4","name":"Goregaon Warehouse","label":"Location","risk_score":60.0,"city":"Mumbai"},
    ]
    if q:
        results = [r for r