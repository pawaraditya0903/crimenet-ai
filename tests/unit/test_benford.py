import pytest
from backend.app.analytics.benford import run_benford_analysis

def test_benford_minimum_sample_size_requirement():
    small_dataset = [120, 230, 450]
    res = run_benford_analysis(small_dataset)
    assert res["status"] == "INSUFFICIENT_DATA"

def test_benford_analysis_on_smurfing_clustered_dataset():
    # Synthetic transactions heavily clustered on digits 4 and 9
    smurfed = [49500, 48200, 49900, 47800, 95000, 98000, 92000, 94000] * 10
    res = run_benford_analysis(smurfed)
    
    assert res["status"] == "COMPLETED"
    assert res["sample_size"] == len(smurfed)
    assert res["degrees_of_freedom"] == 8
    # Chi-square should deviate heavily from natural curve
    assert res["chi_square_statistic"] > res["critical_threshold_alpha_0_05"]
    assert res["is_statistically_deviant"] is True
