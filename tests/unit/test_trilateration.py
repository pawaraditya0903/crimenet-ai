import pytest
from backend.app.analytics.trilateration import calculate_wls_trilateration

def test_tier1_multi_tower_wls_trilateration():
    towers = [
        {"name": "Tower A", "lat": 19.1663, "lng": 72.8526, "rssi_dbm": -65.0, "tx_power": -42.0},
        {"name": "Tower B", "lat": 19.1712, "lng": 72.8610, "rssi_dbm": -72.0, "tx_power": -42.0},
        {"name": "Tower C", "lat": 19.0596, "lng": 72.8295, "rssi_dbm": -80.0, "tx_power": -42.0}
    ]
    res = calculate_wls_trilateration(towers)
    assert res["status"] == "CONVERGED_TIER1_WLS"
    assert "estimated_latitude" in res
    assert "estimated_longitude" in res
    assert res["uncertainty_radius_meters"] > 0
    assert res["gdop_dilution_of_precision"] >= 1.0

def test_tier2_two_tower_fallback():
    towers = [
        {"name": "Tower A", "lat": 19.1663, "lng": 72.8526, "rssi_dbm": -65.0, "tx_power": -42.0},
        {"name": "Tower B", "lat": 19.1712, "lng": 72.8610, "rssi_dbm": -72.0, "tx_power": -42.0}
    ]
    res = calculate_wls_trilateration(towers)
    assert res["status"] == "CONVERGED_TIER2_BI_CELL"
    assert res["towers_participating"] == 2
