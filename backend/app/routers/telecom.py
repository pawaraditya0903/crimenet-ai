from fastapi import APIRouter
from backend.app.schemas.analytics import CDRBatchRequest, TrilaterationRequest
from backend.app.analytics.telecom import analyze_cdr_telemetry
from backend.app.analytics.trilateration import calculate_wls_trilateration

router = APIRouter(prefix="/api/telecom", tags=["Telecom Intelligence"])

@router.get("/sample-cdr")
async def get_sample_cdr():
    """Returns sample synthetic CDR telemetry records."""
    sample_records = [
        {"call_id":"CDR-1001","timestamp":"2026-03-12 01:34:10","caller":"9834702432","receiver":"+91-9654321098","duration_sec":342,"tower_id":"MUM-GOR-4041","imei":"354892019482019","imsi":"404-45-891029","lat":19.1663,"lng":72.8526,"type":"OUTBOUND_VOICE"},
        {"call_id":"CDR-1002","timestamp":"2026-03-12 01:52:05","caller":"9834702432","receiver":"+91-9845678901","duration_sec":185,"tower_id":"MUM-GOR-4042","imei":"354892019482019","imsi":"404-45-891029","lat":19.1668,"lng":72.8530,"type":"OUTBOUND_VOICE"},
        {"call_id":"CDR-1003","timestamp":"2026-03-12 02:14:40","caller":"9834702432","receiver":"+91-9765432109","duration_sec":512,"tower_id":"MUM-BAN-4010","imei":"354892019482019","imsi":"404-45-891029","lat":19.0544,"lng":72.8402,"type":"INBOUND_VOICE"},
        {"call_id":"CDR-1004","timestamp":"2026-03-12 02:30:15","caller":"9834702432","receiver":"+91-9876543210","duration_sec":620,"tower_id":"MUM-JUH-4022","imei":"354892019482019","imsi":"404-45-891029","lat":19.1075,"lng":72.8263,"type":"OUTBOUND_VOICE"},
        {"call_id":"CDR-1005","timestamp":"2026-03-12 21:15:00","caller":"9834702432","receiver":"+91-9822019283","duration_sec":45,"tower_id":"MUM-JUH-4022","imei":"354892019482019","imsi":"404-45-998811","lat":19.1075,"lng":72.8263,"type":"BURST_CALL"},
        {"call_id":"CDR-1006","timestamp":"2026-03-12 21:16:30","caller":"9834702432","receiver":"+91-9845678901","duration_sec":55,"tower_id":"MUM-JUH-4022","imei":"354892019482019","imsi":"404-45-998811","lat":19.1075,"lng":72.8263,"type":"BURST_CALL"},
        {"call_id":"CDR-1007","timestamp":"2026-03-12 21:18:10","caller":"9834702432","receiver":"+91-9654321098","duration_sec":62,"tower_id":"MUM-JUH-4022","imei":"354892019482019","imsi":"404-45-998811","lat":19.1075,"lng":72.8263,"type":"BURST_CALL"},
    ]
    return {"total_records": len(sample_records), "records": sample_records}

@router.post("/analyze")
async def analyze_cdr_batch_endpoint(req: CDRBatchRequest):
    """Analyzes CDR batch for nocturnal communication, call bursts, and burner SIM swaps."""
    return analyze_cdr_telemetry(req.records)

@router.post("/triangulate-math")
async def calculate_trilateration_endpoint(req: TrilaterationRequest = TrilaterationRequest()):
    """Calculates cellular multi-tower Weighted Least Squares radio trilateration."""
    towers = req.towers or [
        {"name": "Goregaon East Sector 1", "lat": 19.1663, "lng": 72.8526, "rssi_dbm": -68.5, "tx_power": -42.0},
        {"name": "Goregaon Sector 4 Depot", "lat": 19.1712, "lng": 72.8610, "rssi_dbm": -74.2, "tx_power": -42.0},
        {"name": "Bandra West Link Relay", "lat": 19.0596, "lng": 72.8295, "rssi_dbm": -82.0, "tx_power": -42.0}
    ]
    return calculate_wls_trilateration(towers)
