from typing import List, Dict, Any
from backend.app.ml.features import FEATURE_NAMES, FEATURE_BASELINES

def generate_alert_explanation(features: List[float], entity_name: str) -> Dict[str, Any]:
    """Computes exact feature deviation from baseline distributions and generates
    transparent, human-interpretable investigative reasons.
    """
    contributing_signals = []
    feature_breakdown = []

    for i, name in enumerate(FEATURE_NAMES):
        val = features[i] if i < len(features) else 0.0
        baseline = FEATURE_BASELINES.get(name, {"mean": 0.0, "std": 1.0})
        mean_val = baseline["mean"]
        std_val = baseline["std"] or 1.0

        # Calculate z-score deviation
        z_score = round((val - mean_val) / std_val, 2)
        pct_diff = round(((val - mean_val) / max(mean_val, 0.001)) * 100, 1)

        sign = "+" if pct_diff >= 0 else ""
        dev_label = f"{sign}{pct_diff}% ({sign}{z_score}σ)"

        item = {
            "feature": name,
            "value": round(val, 3),
            "baseline_mean": mean_val,
            "baseline_std": std_val,
            "z_score": z_score,
            "deviation_label": dev_label
        }
        feature_breakdown.append(item)

        # Signal formulation for significant deviations (z-score > 1.5)
        if z_score >= 1.5:
            if name == "nocturnal_activity_ratio":
                contributing_signals.append(f"Nocturnal clustering: {round(val*100, 1)}% of events occurred between 01:00 AM - 04:30 AM ({z_score}σ above baseline).")
            elif name == "financial_velocity_score":
                contributing_signals.append(f"Elevated financial velocity: rapid transfer rate exceeding standard distribution by {pct_diff}%.")
            elif name == "cdr_burst_zscore":
                contributing_signals.append(f"Abnormal telecom burst: call frequency surge with Z-score {z_score}σ.")
            elif name == "centrality_degree_weight":
                contributing_signals.append(f"Key structural connectivity: node acts as an information conduit between multiple distinct clusters.")
            elif name == "benford_deviation_index":
                contributing_signals.append(f"Benford first-digit anomaly: transaction amounts deviate from logarithmic distributions, consistent with smurfing.")

    # Sort breakdown by absolute z-score descending
    feature_breakdown.sort(key=lambda x: abs(x["z_score"]), reverse=True)

    if not contributing_signals:
        contributing_signals.append("Baseline profile: all measured parameters conform within standard statistical variance limits.")

    explanation_summary = f"Investigative lead for '{entity_name}' triggered primarily by: " + "; ".join(contributing_signals[:3])

    return {
        "entity_name": entity_name,
        "feature_breakdown": feature_breakdown,
        "contributing_signals": contributing_signals,
        "explanation_summary": explanation_summary,
        "disclaimer": "All feature deviations represent statistical signals for human investigator review, not determinations of guilt."
    }
