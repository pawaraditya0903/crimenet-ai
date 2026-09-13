from fastapi import APIRouter
from backend.app.graph.engine import build_network_graph
from backend.app.graph.cycles import detect_financial_cycles
from backend.app.analytics.financial import detect_smurfing
from backend.app.analytics.benford import run_benford_analysis
from backend.app.ml.pipeline import GLOBAL_ML_PIPELINE
from backend.app.ml.evaluation import run_synthetic_benchmark_evaluation
from backend.app.models.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["Advanced Analytics"])

@router.get("/anomalies")
async def anomalies():
    """Returns anomalies detected across multi-sensor telemetry."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, case_id, entity_name, anomaly_type, anomaly_score, severity, status, plain_english_explanation FROM alerts")
        rows = [dict(r) for r in cursor.fetchall()]

    return {
        "summary": {"total": len(rows), "critical": sum(1 for r in rows if r["severity"] == "critical")},
        "anomalies": rows,
        "active_sklearn_engine": GLOBAL_ML_PIPELINE.get_status()
    }

@router.get("/cycles")
async def cycles_endpoint():
    """Detects circular financial layering cycles using Johnson's simple cycles algorithm."""
    G, _, _ = build_network_graph()
    return detect_financial_cycles(G)

@router.get("/smurfing")
async def smurfing_endpoint():
    """Evaluates sub-50k structured smurfing transactions designed to evade reporting thresholds."""
    sample_smurf_txs = [
        {"account": "Rohan Gupta (Mule Lead)", "amount": 49500},
        {"account": "Rohan Gupta (Mule Lead)", "amount": 48200},
        {"account": "Rohan Gupta (Mule Lead)", "amount": 49100},
        {"account": "Anita Roy (Accountant)", "amount": 47500},
        {"account": "Anita Roy (Accountant)", "amount": 48900},
        {"account": "Sameer Sheikh (Courier)", "amount": 46800},
        {"account": "Sameer Sheikh (Courier)", "amount": 49200},
        {"account": "Indus Export LLP", "amount": 49800},
        {"account": "Indus Export LLP", "amount": 48500},
        {"account": "Indus Export LLP", "amount": 49000},
    ] * 5
    return detect_smurfing(sample_smurf_txs, threshold_limit=50000.0)

@router.get("/benford")
async def benford_endpoint():
    """Applies Benford's Law First-Digit Analysis to financial transaction amounts."""
    # Build sample transactions with synthetic smurfing clustering on digits 4 and 9
    amounts = [49500, 48200, 47000, 49900, 48800, 95000, 92000, 98000, 94500] * 10
    amounts.extend([1250, 18500, 14200, 23000, 31000, 150000, 240000, 110000] * 5)
    return run_benford_analysis(amounts)

@router.get("/model-evaluation")
async def model_evaluation_endpoint():
    """Returns empirical benchmark metrics and confusion matrix evaluated on synthetic ground truth."""
    return run_synthetic_benchmark_evaluation(n_samples=2000, contamination=0.05)
