import pytest
from backend.app.ml.explainability import generate_alert_explanation

def test_feature_attribution_and_signal_generation():
    # Anomaly features: extreme nocturnal ratio (0.92 vs baseline 0.12) and burst (4.8 vs baseline 0.10)
    features = [0.45, 0.92, 0.15, 4.80, 0.18]
    xai = generate_alert_explanation(features, "Target Subject X")
    
    assert xai["entity_name"] == "Target Subject X"
    assert len(xai["feature_breakdown"]) == 5
    assert len(xai["contributing_signals"]) >= 2
    
    # Check that highest z-score feature is nocturnal ratio or burst
    top_feature = xai["feature_breakdown"][0]["feature"]
    assert top_feature in ["nocturnal_activity_ratio", "cdr_burst_zscore"]
    assert "disclaimer" in xai
