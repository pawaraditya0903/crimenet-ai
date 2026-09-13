from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from backend.app.pipeline.ingestion import (
    MultiSourcePipeline,
    SAMPLE_CDR_DATA,
    SAMPLE_BANKING_DATA,
    SAMPLE_FIR_DATA,
    SAMPLE_ANPR_DATA,
    SAMPLE_WALLET_DATA
)
from backend.app.models.database import get_db
from backend.app.models.tables import DEFAULT_ENTITIES, DEFAULT_RELATIONSHIPS

router = APIRouter(prefix="/api/pipeline", tags=["Data Ingestion & Entity Resolution Pipeline"])

class IngestBatchRequest(BaseModel):
    dataset_type: Optional[str] = "custom"
    cdr_records: Optional[List[Dict[str, Any]]] = None
    banking_records: Optional[List[Dict[str, Any]]] = None
    fir_records: Optional[List[Dict[str, Any]]] = None
    anpr_records: Optional[List[Dict[str, Any]]] = None
    wallet_records: Optional[List[Dict[str, Any]]] = None
    csv_content: Optional[str] = None
    csv_dataset_type: Optional[str] = None

@router.get("/sample-data/{dataset_type}")
async def get_sample_data(dataset_type: str):
    """Returns synthetic demonstration records for a requested domain."""
    d_type = dataset_type.lower().strip()
    if d_type == "cdr":
        return {"dataset_type": "CDR", "records": SAMPLE_CDR_DATA, "count": len(SAMPLE_CDR_DATA)}
    elif d_type == "banking":
        return {"dataset_type": "BANKING", "records": SAMPLE_BANKING_DATA, "count": len(SAMPLE_BANKING_DATA)}
    elif d_type == "fir":
        return {"dataset_type": "FIR", "records": SAMPLE_FIR_DATA, "count": len(SAMPLE_FIR_DATA)}
    elif d_type == "anpr":
        return {"dataset_type": "ANPR", "records": SAMPLE_ANPR_DATA, "count": len(SAMPLE_ANPR_DATA)}
    elif d_type == "wallet":
        return {"dataset_type": "WALLET", "records": SAMPLE_WALLET_DATA, "count": len(SAMPLE_WALLET_DATA)}
    elif d_type == "all":
        return {
            "dataset_type": "ALL",
            "samples": {
                "cdr": SAMPLE_CDR_DATA,
                "banking": SAMPLE_BANKING_DATA,
                "fir": SAMPLE_FIR_DATA,
                "anpr": SAMPLE_ANPR_DATA,
                "wallet": SAMPLE_WALLET_DATA
            }
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unknown dataset type '{dataset_type}'. Supported: cdr, banking, fir, anpr, wallet, all")

@router.get("/summary")
async def get_pipeline_summary():
    """Returns current counts of entities, relationships, and cross-domain links in the graph database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM graph_entities")
        total_entities = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM graph_relationships")
        total_relationships = cursor.fetchone()["count"]

        cursor.execute("SELECT type, COUNT(*) as count FROM graph_entities GROUP BY type")
        entity_types = {row["type"]: row["count"] for row in cursor.fetchall()}

        cursor.execute("SELECT label, COUNT(*) as count FROM graph_relationships GROUP BY label")
        relationship_types = {row["label"]: row["count"] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) as count FROM graph_relationships WHERE label IN ('CROSS_DOMAIN_IDENTITY', 'SPATIOTEMPORAL_CO_LOCATION', 'SUSPECT_VEHICLE_CITED', 'HAWALA_ON_OFF_RAMP')")
        cross_domain_links = cursor.fetchone()["count"]

    return {
        "status": "HEALTHY",
        "total_entities": total_entities,
        "total_relationships": total_relationships,
        "cross_domain_links": cross_domain_links,
        "entity_breakdown": entity_types,
        "relationship_breakdown": relationship_types
    }

@router.post("/load-all-samples")
async def load_all_sample_datasets():
    """Loads all 5 synthetic benchmark datasets (CDR, Banking, FIR, ANPR, Wallet),
    executes multi-source entity resolution, discovers cross-domain links,
    and updates the database graph topology.
    """
    result = MultiSourcePipeline.process_and_link(
        cdr_records=SAMPLE_CDR_DATA,
        banking_records=SAMPLE_BANKING_DATA,
        fir_records=SAMPLE_FIR_DATA,
        anpr_records=SAMPLE_ANPR_DATA,
        wallet_records=SAMPLE_WALLET_DATA,
        persist_to_db=True
    )
    return result

@router.post("/ingest")
async def ingest_dataset_batch(req: IngestBatchRequest):
    """Ingests records or CSV content from one or more datasets and executes entity resolution."""
    cdr = req.cdr_records or []
    banking = req.banking_records or []
    fir = req.fir_records or []
    anpr = req.anpr_records or []
    wallet = req.wallet_records or []

    # Handle CSV content if provided
    if req.csv_content and req.csv_dataset_type:
        parsed_records = MultiSourcePipeline.parse_csv_content(req.csv_content)
        t = req.csv_dataset_type.lower().strip()
        if t == "cdr":
            cdr.extend(parsed_records)
        elif t == "banking":
            banking.extend(parsed_records)
        elif t == "fir":
            fir.extend(parsed_records)
        elif t == "anpr":
            anpr.extend(parsed_records)
        elif t == "wallet":
            wallet.extend(parsed_records)

    result = MultiSourcePipeline.process_and_link(
        cdr_records=cdr,
        banking_records=banking,
        fir_records=fir,
        anpr_records=anpr,
        wallet_records=wallet,
        persist_to_db=True
    )
    return result

@router.post("/reset")
async def reset_graph_to_seed():
    """Resets the graph database back to verified initial demonstration baseline."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM graph_relationships")
        cursor.execute("DELETE FROM graph_entities")

        for e in DEFAULT_ENTITIES:
            cursor.execute(
                "INSERT INTO graph_entities (id, name, type, tier, category, risk_score, city, phone, dossier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (e["id"], e["name"], e["type"], e["tier"], e["category"], e["risk_score"], e["city"], e["phone"], e["dossier"])
            )
        for r in DEFAULT_RELATIONSHIPS:
            cursor.execute(
                "INSERT INTO graph_relationships (id, source, target, label, type, confidence, weight) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (r["id"], r["source"], r["target"], r["label"], r["type"], r["confidence"], r["weight"])
            )

    return {"status": "GRAPH_RESET_SUCCESS", "message": "Graph restored to initial verified topology."}
