import csv
import io
from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File, Form, Depends
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
from backend.app.security.rbac import require_authenticated_user, require_roles, ForensicRole

router = APIRouter(prefix="/api/pipeline", tags=["Data Ingestion & Entity Resolution Pipeline"])

REQUIRED_COLUMNS_BY_DOMAIN: Dict[str, List[str]] = {
    "cdr": ["caller", "receiver", "timestamp"],
    "banking": ["from_account", "to_account", "amount", "timestamp"],
    "fir": ["fir_no", "police_station", "accused_name"],
    "anpr": ["plate_number", "camera_id", "timestamp"],
    "wallet": ["sender_wallet", "receiver_wallet", "amount", "timestamp"]
}


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
async def load_all_sample_datasets(claims: dict = Depends(require_authenticated_user)):
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
async def ingest_dataset_batch(req: IngestBatchRequest, claims: dict = Depends(require_authenticated_user)):
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

@router.post("/upload-csv")
async def upload_csv_dataset(
    file: UploadFile = File(...),
    dataset_type: str = Form(...),
    claims: dict = Depends(require_authenticated_user)
):
    """Uploads an investigator's CSV file for a specific intelligence domain,
    validates headers against domain schema, normalizes identifiers,
    and executes cross-domain entity resolution and graph linking.
    """
    dtype = dataset_type.lower().strip()
    if dtype not in REQUIRED_COLUMNS_BY_DOMAIN:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Unsupported dataset type '{dataset_type}'.",
                "supported_types": list(REQUIRED_COLUMNS_BY_DOMAIN.keys()),
                "dataset_type": dataset_type
            }
        )

    # 1. File extension validation
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Invalid file format: '{filename}'. Only CSV files (.csv) are accepted.",
                "dataset_type": dtype
            }
        )

    # 2. Safe in-memory reading with size limit (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Uploaded CSV file is completely empty. Please select a valid dataset file.",
                "dataset_type": dtype
            }
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"File exceeds maximum permissible upload size limit of 10MB.",
                "dataset_type": dtype
            }
        )

    # 3. UTF-8 decoding
    text_content = ""
    for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            text_content = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if not text_content:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unable to decode CSV file. Please ensure it is saved as UTF-8 encoded text.",
                "dataset_type": dtype
            }
        )

    # 4. Parse CSV headers & records
    try:
        reader = csv.DictReader(io.StringIO(text_content.strip()))
        if not reader.fieldnames:
            raise ValueError("CSV header row missing")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Malformed CSV file structure: {str(e)}",
                "dataset_type": dtype
            }
        )

    # 5. Validate required columns
    normalized_headers = {col.strip().lower(): col for col in reader.fieldnames if col}
    required_cols = REQUIRED_COLUMNS_BY_DOMAIN[dtype]
    missing_cols = [req for req in required_cols if req not in normalized_headers]

    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Invalid {dtype.upper()} dataset: missing required columns.",
                "missing_columns": missing_cols,
                "required_columns": required_cols,
                "found_columns": list(normalized_headers.keys()),
                "dataset_type": dtype
            }
        )

    # 6. Normalize rows into standardized dictionary records
    records: List[Dict[str, Any]] = []
    for row in reader:
        norm_row = {
            k.strip().lower(): v.strip() if isinstance(v, str) else v
            for k, v in row.items()
            if k
        }
        # Ignore completely empty rows
        if any(v for v in norm_row.values() if v is not None and str(v).strip() != ""):
            records.append(norm_row)

    if not records:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"The uploaded CSV file contains headers but has no data rows.",
                "dataset_type": dtype
            }
        )

    # 7. Execute MultiSourcePipeline entity resolution and link generation
    result = MultiSourcePipeline.process_and_link(
        cdr_records=records if dtype == "cdr" else None,
        banking_records=records if dtype == "banking" else None,
        fir_records=records if dtype == "fir" else None,
        anpr_records=records if dtype == "anpr" else None,
        wallet_records=records if dtype == "wallet" else None,
        persist_to_db=True
    )

    return {
        "status": "DATASET_UPLOAD_SUCCESS",
        "message": f"Dataset '{dtype.upper()}' ({len(records)} records) processed and correlated successfully.",
        "dataset_type": dtype.upper(),
        "records_processed": len(records),
        "entities_created": len(result.get("entities", [])),
        "relationships_generated": len(result.get("relationships", [])),
        "cross_domain_links": len(result.get("cross_domain_links", [])),
        "warnings": result.get("warnings", []),
        "links": result.get("links", [])
    }


@router.post("/reset")
async def reset_graph_to_seed(claims: dict = Depends(require_roles([ForensicRole.SUPERVISORY_OFFICER]))):
    """Resets the graph database back to verified initial demonstration baseline. Restricted to Supervisory Officers."""
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
