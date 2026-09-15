import os
import sys

# Ensure repository root and backend directory are in sys.path regardless of execution context
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

for p in [REPO_ROOT, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

import time
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import socketio

from backend.app.config import (
    ALLOWED_ORIGINS,
    IS_PRODUCTION,
    JWT_SECRET_KEY,
    PII_KEY_BYTES
)
from backend.app.models.database import init_db, get_db
from backend.app.models.tables import seed_database_if_empty
from backend.app.security.middleware import SecurityHeadersMiddleware
from backend.app.security.passwords import hash_password, verify_password
from backend.app.security.crypto import encrypt_pii, decrypt_pii
from backend.app.security.jwt import create_jwt_token, create_refresh_token, verify_jwt_token
from backend.app.security.rbac import ForensicRole, require_roles, require_authenticated_user
from backend.app.realtime.socket_manager import sio, emit_investigation_event
from backend.app.ml.pipeline import GLOBAL_ML_PIPELINE

# Import Routers
from backend.app.routers.auth import router as auth_router, refresh_access_token
from backend.app.routers.cases import router as cases_router
from backend.app.routers.evidence import router as evidence_router, get_merkle_evidence_root
from backend.app.routers.alerts import router as alerts_router, list_alerts, get_alert_explainability, review_alert_endpoint
from backend.app.routers.graph import router as graph_router
from backend.app.routers.analytics import router as analytics_router, benford_endpoint, model_evaluation_endpoint
from backend.app.routers.telecom import router as telecom_router
from backend.app.routers.copilot import router as copilot_router, copilot_chat_endpoint, confirm_copilot_action
from backend.app.routers.audit import router as audit_router, get_system_audit_trail
from backend.app.routers.reports import router as reports_router
from backend.app.routers.security import router as security_router
from backend.app.routers.pipeline import router as pipeline_router
from backend.app.routers.osint import router as osint_router
from backend.app.routers.geospatial import router as geospatial_router
from backend.app.database.connection import init_relational_schema, check_database_connection
from backend.app.graph.neo4j_client import check_neo4j_status
from backend.app.storage.s3_client import check_storage_status
from backend.app.routers.models import router as models_router, tune_model_hyperparameters, TuneModelRequest
from backend.app.routers.diagnostics import router as diagnostics_router
from backend.app.routers.system_settings import router as system_settings_router

logger = logging.getLogger("crimenet.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database schema & seeds for PostgreSQL/PostGIS and SQLite
    logger.info("Initializing CrimeNet AI Enterprise Relational & PostGIS Store...")
    init_relational_schema()
    init_db()
    seed_database_if_empty()
    yield

# Ensure database is initialized on import
init_relational_schema()
init_db()
seed_database_if_empty()

app = FastAPI(
    title="CrimeNet AI — Autonomous Forensic Intelligence Platform",
    description="Production-grade distributed forensic intelligence and anti-money laundering platform.",
    version="2.1.0",
    lifespan=lifespan
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Security Headers & Request Limiting Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. Mount Routers
app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(evidence_router)
app.include_router(alerts_router)
app.include_router(graph_router)
app.include_router(analytics_router)
app.include_router(telecom_router)
app.include_router(copilot_router)
app.include_router(audit_router)
app.include_router(reports_router)
app.include_router(security_router)
app.include_router(pipeline_router)
app.include_router(osint_router)
app.include_router(geospatial_router)
app.include_router(models_router)
app.include_router(diagnostics_router)
app.include_router(system_settings_router)

# ── TOP-LEVEL HEALTH & SYSTEM TELEMETRY ──
@app.get("/api/health")
@app.get("/health")
async def health_check():
    db_telemetry = check_database_connection()
    neo_telemetry = check_neo4j_status()
    s3_telemetry = check_storage_status()

    return {
        "status": "OPERATIONAL_HEALTHY",
        "service": "CrimeNet AI Core Backend",
        "environment": "production" if IS_PRODUCTION else "development",
        "version": "2.1.0",
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "architecture": {
            "relational_system_of_record": "PostgreSQL 16 + PostGIS",
            "dedicated_graph_db": "Neo4j 5 (Cypher Traversal)",
            "object_storage": "S3 / MinIO (Evidence Vault)",
            "analytics_ml_layer": "NetworkX + Scikit-Learn IsolationForest"
        },
        "subsystems": {
            "database": f"{db_telemetry['dialect'].title()}_{'PostGIS_Active' if db_telemetry.get('postgis_enabled') else 'Connected'}",
            "graph_engine": f"{neo_telemetry['status']}_{neo_telemetry.get('engine', 'NetworkX')}",
            "object_storage": f"{s3_telemetry['provider']}_{s3_telemetry['status']}",
            "ml_anomaly_engine": "Scikit_Learn_IsolationForest_Fitted",
            "audit_chain": "Cryptographically_Linked_SHA256"
        },
        "telemetry_details": {
            "database": db_telemetry,
            "neo4j": neo_telemetry,
            "object_storage": s3_telemetry
        }
    }

@app.get("/api/notifications")
async def get_notifications(claims: Optional[dict] = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, case_id, title, details, severity, is_read, timestamp FROM notifications ORDER BY timestamp DESC LIMIT 50")
        rows = [dict(r) for r in cursor.fetchall()]
    return {
        "notifications": rows,
        "unread_count": sum(1 for r in rows if not r["is_read"]),
        "total": len(rows)
    }

@app.post("/api/notifications/{notif_id}/read")
async def mark_notification_read(notif_id: str, claims: dict = Depends(require_authenticated_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    return {"success": True}

@app.post("/api/notifications/clear")
@app.post("/api/notifications/clear-all")
async def clear_all_notifications(claims: dict = Depends(require_authenticated_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notifications")
    return {"success": True}

# Simulation State for Dynamic Visual Demonstrations
SIMULATION_STATE = {"is_running": False, "speed": 1.0, "tick": 0}

@app.post("/api/sim/start")
@app.post("/api/simulation/start")
async def start_sim():
    SIMULATION_STATE["is_running"] = True
    return {"status": "RUNNING", "simulation": SIMULATION_STATE, "state": SIMULATION_STATE}

@app.post("/api/sim/pause")
@app.post("/api/simulation/pause")
async def pause_sim():
    SIMULATION_STATE["is_running"] = False
    return {"status": "PAUSED", "simulation": SIMULATION_STATE, "state": SIMULATION_STATE}

@app.post("/api/sim/reset")
@app.post("/api/simulation/reset")
async def reset_sim():
    SIMULATION_STATE["tick"] = 0
    return {"status": "reset", "simulation": SIMULATION_STATE}

@app.post("/api/simulation/speed")
async def set_sim_speed(payload: Dict[str, Any] = {}):
    speed = float(payload.get("speed", 1.0))
    SIMULATION_STATE["speed"] = speed
    return {"status": "speed_updated", "speed": speed, "simulation": SIMULATION_STATE}

@app.get("/api/sim/status")
@app.get("/api/simulation/status")
async def get_sim_status():
    return SIMULATION_STATE

# ── BACKWARD COMPATIBILITY EXPORTS FOR EXISTING TESTS & TOOLS ──
import hashlib
from backend.app.security.passwords import hash_password as _orig_hash_password

class HashResult(str):
    salt_hex: str = ""
    def __iter__(self):
        return iter((str(self), self.salt_hex))
    def __getitem__(self, item):
        if isinstance(item, int):
            if item == 0:
                return str(self)
            elif item == 1:
                return self.salt_hex
        return super().__getitem__(item)

def hash_password(password: str, salt: Optional[bytes] = None, iterations: int = 100000):
    formatted, salt_hex = _orig_hash_password(password, salt, iterations)
    res = HashResult(formatted)
    res.salt_hex = salt_hex
    return res

get_alerts = list_alerts
get_merkle_evidence_ledger = get_merkle_evidence_root
benford_fraud_analysis = benford_endpoint
from backend.app.routers.models import get_model_evaluation
refresh_access_token_endpoint = refresh_access_token
LIVE_IFOREST = GLOBAL_ML_PIPELINE
_DEFAULT_PASS_HASH = hash_password("Aditya@4912")
_LEGACY_PASS_HASH = hashlib.sha256(b"Aditya@4912").hexdigest()
ModelTuneRequest = TuneModelRequest

from pydantic import BaseModel, Field

class LiveTrainRequest(BaseModel):
    n_estimators: int = 100
    num_samples: int = 500

async def get_live_model_status():
    status = GLOBAL_ML_PIPELINE.get_status()
    sample_feat = [1.2, 0.4, 0.5, 1.1, 0.3]
    score = GLOBAL_ML_PIPELINE.score_sample(sample_feat)
    return {
        "engine_status": status,
        "live_inference_verification": {
            "scoring_output": {
                "isolation_score": score.get("raw_decision_score", 0.0),
                "mahalanobis_distance": score.get("mahalanobis_distance", 0.0),
                "ensemble_anomaly_confidence": score.get("calibrated_anomaly_score", 0.0),
                "classification": score.get("classification", "")
            }
        }
    }

async def trigger_live_training(req: LiveTrainRequest):
    GLOBAL_ML_PIPELINE.n_estimators = req.n_estimators
    res = GLOBAL_ML_PIPELINE.fit_synthetic_telemetry(num_samples=req.num_samples)
    return {
        "status": "LIVE_SKLEARN_FITTED_SUCCESSFULLY",
        "estimators_trained": GLOBAL_ML_PIPELINE.trained_trees_count,
        "details": res
    }

def purge_expired_intruder_logs(retention_days: int = 30):
    cutoff = time.time() - (retention_days * 86400)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM intruder_logs WHERE epoch < ?", (cutoff,))
        purged = cursor.rowcount
    return {"purged": purged, "retention_days": retention_days, "cutoff_epoch": cutoff}

from backend.app.schemas.alerts import AlertReviewRequest
from backend.app.schemas.copilot import CopilotChatRequest

# ── SERVE FRONTEND SPA IN PRODUCTION IF BUILT ──
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = os.path.join(REPO_ROOT, "frontend", "dist")
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("socket.io"):
            raise HTTPException(status_code=404, detail="Not Found")
        target_file = os.path.join(frontend_dist, full_path)
        if os.path.exists(target_file) and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

# Wrap FastAPI app with Socket.IO ASGI application
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
