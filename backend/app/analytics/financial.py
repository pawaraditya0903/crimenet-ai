import math
from typing import List, Dict, Any

def detect_smurfing(
    transactions: List[Dict[str, Any]],
    threshold_limit: float = 50000.0,
    proximity_margin: float = 0.15
) -> Dict[str, Any]:
    """Detects structured micro-transaction smurfing designed to evade mandatory reporting thresholds."""
    lower_bound = threshold_limit * (1.0 - proximity_margin)
    upper_bound = threshold_limit * 0.999

    smurf_candidates = []
    total_smurfed_volume = 0.0
    account_groups: Dict[str, List[Dict[str, Any]]] = {}

    for tx in transactions:
        amt = float(tx.get("amount", 0.0))
        account = tx.get("account", "UNKNOWN_ACCOUNT")
        if account not in account_groups:
            account_groups[account] = []
        account_groups[account].append(tx)

        if lower_bound <= amt <= upper_bound:
            smurf_candidates.append(tx)
            total_smurfed_volume += amt

    # Calculate Shannon entropy of the account fan-out distribution
    total_tx_count = len(transactions) or 1
    entropy = 0.0
    cluster_breakdown = []

    for account, txs in account_groups.items():
        p = len(txs) / total_tx_count
        if p > 0:
            entropy -= p * math.log2(p)
        cluster_breakdown.append({
            "account": account,
            "transaction_count": len(txs),
            "total_volume": sum(float(t.get("amount", 0.0)) for t in txs)
        })

    cluster_breakdown.sort(key=lambda x: x["transaction_count"], reverse=True)

    return {
        "status": "ANALYSIS_COMPLETE",
        "total_transactions_evaluated": total_tx_count,
        "structured_smurf_transactions_count": len(smurf_candidates),
        "total_smurfed_volume": round(total_smurfed_volume, 2),
        "shannon_entropy_score": round(entropy, 3),
        "structuring_detected": len(smurf_candidates) >= 5,
        "top_originators": cluster_breakdown[:5],
        "investigative_note": (
            f"Detected {len(smurf_candidates)} transactions clustered just below statutory ₹{int(threshold_limit):,} "
            f"threshold (range: ₹{int(lower_bound):,} - ₹{int(upper_bound):,}). Consistent with smurfing patterns."
        )
    }

def calculate_composite_financial_risk(
    amount_anomaly_score: float,
    counterparty_risk: float,
    frequency_velocity: float,
    graph_layering_risk: float
) -> Dict[str, Any]:
    """Transparent composite risk calculation:
    Composite = 0.35 * Amount + 0.25 * Counterparty + 0.20 * Velocity + 0.20 * Graph
    """
    composite = (
        0.35 * min(1.0, max(0.0, amount_anomaly_score)) +
        0.25 * min(1.0, max(0.0, counterparty_risk)) +
        0.20 * min(1.0, max(0.0, frequency_velocity)) +
        0.20 * min(1.0, max(0.0, graph_layering_risk))
    )
    scaled_score = round(composite * 100.0, 1)

    return {
        "composite_risk_score": scaled_score,
        "contributing_components": {
            "amount_anomaly_contribution": round(0.35 * amount_anomaly_score * 100, 1),
            "counterparty_risk_contribution": round(0.25 * counterparty_risk * 100, 1),
            "velocity_contribution": round(0.20 * frequency_velocity * 100, 1),
            "graph_layering_contribution": round(0.20 * graph_layering_risk * 100, 1)
        },
        "formula": "Composite = 0.35*Amount + 0.25*Counterparty + 0.20*Velocity + 0.20*Graph",
        "investigative_classification": "HIGH_PRIORITY_REVIEW" if scaled_score >= 75.0 else ("MODERATE_SUSPICION" if scaled_score >= 50.0 else "LOW_INVESTIGATIVE_PRIORITY")
    }
