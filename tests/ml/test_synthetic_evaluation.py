import pytest
from backend.app.ml.evaluation import run_synthetic_benchmark_evaluation

def test_synthetic_anomaly_injection_benchmark():
    res = run_synthetic_benchmark_evaluation(n_samples=1000, contamination=0.05, random_state=42)
    assert "metrics" in res
    metrics = res["metrics"]
    
    # Anomaly detector should recover injected synthetic outliers with high recall and low FPR
    assert metrics["precision"] > 0.65
    assert metrics["recall"] > 0.70
    assert metrics["f1_score"] > 0.65
    assert metrics["false_positive_rate"] < 0.10
    assert "scientific_disclosure" in res
