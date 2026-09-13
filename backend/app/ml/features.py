from typing import List, Dict, Any

FEATURE_NAMES = [
    "financial_velocity_score",
    "nocturnal_activity_ratio",
    "centrality_degree_weight",
    "cdr_burst_zscore",
    "benford_deviation_index"
]

# Standard baseline distributions for synthetic baseline normal traffic
FEATURE_BASELINES = {
    "financial_velocity_score": {"mean": 0.45, "std": 0.25},
    "nocturnal_activity_ratio": {"mean": 0.12, "std": 0.08},
    "centrality_degree_weight": {"mean": 0.15, "std": 0.10},
    "cdr_burst_zscore": {"mean": 0.10, "std": 0.75},
    "benford_deviation_index": {"mean": 0.18, "std": 0.12}
}

def extract_features_from_entity(entity: Dict[str, Any], graph_degree: float = 0.1, pr_val: float = 0.05) -> List[float]:
    """Extracts a 5-dimensional numerical telemetry feature vector from an investigative entity."""
    risk = float(entity.get("risk_score", 50.0)) / 100.0
    
    # Financial velocity (proportional to threat score and transaction activity)
    fin_velocity = round(risk * 2.8, 3)
    
    # Nocturnal ratio (0.0 - 1.0)
    nocturnal = round(min(0.95, risk * 0.90), 3)
    
    # Centrality weight (composite of PageRank and degree)
    centrality_wt = round(pr_val * 5.0 + graph_degree * 0.5, 3)
    
    # Telecom call burst Z-score
    burst_z = round(risk * 3.5, 2)
    
    # Benford first-digit deviation index
    benford_dev = round(1.45 if risk > 0.75 else 0.22, 3)
    
    return [fin_velocity, nocturnal, centrality_wt, burst_z, benford_dev]
