import numpy as np
from typing import Dict, Any
from sklearn.ensemble import IsolationForest

def run_synthetic_benchmark_evaluation(
    n_samples: int = 2000,
    contamination: float = 0.05,
    random_state: int = 42
) -> Dict[str, Any]:
    """Evaluates Isolation Forest performance on a controlled synthetic benchmark
    where ground-truth anomaly labels are mathematically known.
    """
    rng = np.random.RandomState(random_state)
    n_anomalies = int(n_samples * contamination)
    n_normal = n_samples - n_anomalies

    # 1. Generate Normal Background Data (Label = 0)
    norm_fin = rng.exponential(scale=0.45, size=(n_normal, 1))
    norm_noct = rng.beta(a=1.5, b=8.0, size=(n_normal, 1))
    norm_cent = rng.gamma(shape=1.2, scale=0.15, size=(n_normal, 1))
    norm_burst = rng.normal(loc=0.0, scale=0.75, size=(n_normal, 1))
    norm_benford = rng.exponential(scale=0.18, size=(n_normal, 1))
    X_norm = np.hstack([norm_fin, norm_noct, norm_cent, norm_burst, norm_benford])
    y_norm = np.zeros(n_normal, dtype=int)

    # 2. Generate Injected Anomalies (Label = 1)
    anom_fin = rng.uniform(low=2.5, high=5.0, size=(n_anomalies, 1))
    anom_noct = rng.uniform(low=0.70, high=0.98, size=(n_anomalies, 1))
    anom_cent = rng.uniform(low=0.60, high=2.0, size=(n_anomalies, 1))
    anom_burst = rng.uniform(low=3.0, high=6.5, size=(n_anomalies, 1))
    anom_benford = rng.uniform(low=1.0, high=2.8, size=(n_anomalies, 1))
    X_anom = np.hstack([anom_fin, anom_noct, anom_cent, anom_burst, anom_benford])
    y_anom = np.ones(n_anomalies, dtype=int)

    X = np.vstack([X_norm, X_anom])
    y_true = np.concatenate([y_norm, y_anom])

    # 3. Fit Model
    model = IsolationForest(
        n_estimators=150,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1
    )
    raw_preds = model.fit_predict(X)  # -1 = anomaly, 1 = inlier
    y_pred = np.where(raw_preds == -1, 1, 0)

    # 4. Compute Confusion Matrix
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    precision = round(tp / max(tp + fp, 1), 4)
    recall = round(tp / max(tp + fn, 1), 4)
    f1 = round(2 * precision * recall / max(precision + recall, 1e-6), 4)
    fpr = round(fp / max(fp + tn, 1), 4)

    return {
        "benchmark_dataset": "Controlled Synthetic Telemetry Injection",
        "sample_size": n_samples,
        "true_anomalies_count": n_anomalies,
        "contamination_rate": contamination,
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn
        },
        "metrics": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "false_positive_rate": fpr
        },
        "scientific_disclosure": (
            "BENCHMARK DISCLOSURE: These metrics represent recovery of injected anomalies "
            "in synthetic benchmark distributions. Real-world operational crime datasets lack "
            "exhaustive ground truth labels; in operational use, all model outputs must be "
            "treated as advisory investigative leads subject to human officer verification."
        )
    }
