import pytest
from backend.app.ml.pipeline import IsolationForestEnsemble

def test_isolation_forest_pipeline_training_and_inference():
    model = IsolationForestEnsemble(n_estimators=100, contamination=0.05, random_state=42)
    fit_res = model.fit_synthetic_telemetry(num_samples=500)
    assert fit_res["status"] == "FITTED_SUCCESSFULLY"
    assert model.is_fitted is True

    # 1. Normal baseline input
    normal_features = [0.40, 0.10, 0.12, 0.05, 0.15]
    res_normal = model.score_sample(normal_features)
    assert res_normal["calibrated_anomaly_score"] < 0.70

    # 2. Extreme anomalous input (extreme nocturnal burst & velocity)
    anomaly_features = [4.50, 0.95, 1.80, 5.50, 2.50]
    res_anom = model.score_sample(anomaly_features)
    assert res_anom["calibrated_anomaly_score"] > 0.65
    assert res_anom["calibrated_anomaly_score"] > res_normal["calibrated_anomaly_score"]
    assert res_anom["is_anomaly"] is True

def test_isolation_forest_deterministic_reproducibility():
    model1 = IsolationForestEnsemble(n_estimators=50, random_state=42)
    model1.fit_synthetic_telemetry(num_samples=200)

    model2 = IsolationForestEnsemble(n_estimators=50, random_state=42)
    model2.fit_synthetic_telemetry(num_samples=200)

    sample = [2.0, 0.5, 0.8, 1.5, 0.9]
    score1 = model1.score_sample(sample)["calibrated_anomaly_score"]
    score2 = model2.score_sample(sample)["calibrated_anomaly_score"]
    assert score1 == score2
