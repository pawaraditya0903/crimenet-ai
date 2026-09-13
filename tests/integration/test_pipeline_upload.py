import io
import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_upload_valid_cdr_csv():
    csv_content = """caller,receiver,timestamp,duration_sec,tower_name,imei
+91-9876543210,+91-9845678901,2026-03-12 01:34:10,342,Bandra-Worli Sea Link Tower,354892019482019
+91-9845678901,+91-9765432109,2026-03-12 01:52:05,185,Juhu North Base Station,359182740192847
"""
    files = {"file": ("test_cdr.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"dataset_type": "cdr"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "DATASET_UPLOAD_SUCCESS"
    assert res["dataset_type"] == "CDR"
    assert res["records_processed"] == 2

def test_upload_valid_banking_csv():
    csv_content = """from_account,to_account,amount,timestamp,from_name,to_name,txn_type
ACC-891024,ACC-441209,48500.0,2026-03-12 01:45:00,Mehta Enterprises Ltd,Mule Account Hub A,IMPS_MICRO_BURST
ACC-441209,ACC-992014,450000.0,2026-03-12 02:05:00,Mule Account Hub A,Phoenix Trading LLC,RTGS_WIRE
"""
    files = {"file": ("test_banking.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"dataset_type": "banking"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "DATASET_UPLOAD_SUCCESS"
    assert res["dataset_type"] == "BANKING"
    assert res["records_processed"] == 2

def test_upload_valid_fir_csv():
    csv_content = """fir_no,police_station,accused_name,suspect_phone,suspect_vehicle
FIR-2026-MUM-892,Bandra Cyber Crime Cell,Arjun Mehta,+91-9876543210,MH-02-DN-4912
"""
    files = {"file": ("test_fir.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"dataset_type": "fir"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "DATASET_UPLOAD_SUCCESS"
    assert res["dataset_type"] == "FIR"
    assert res["records_processed"] == 1

def test_upload_valid_anpr_csv():
    csv_content = """plate_number,camera_id,timestamp,speed_kmh,registered_owner
MH-02-DN-4912,CAM-BANDRA-TOLL-01,2026-03-12 01:40:00,74.2,Arjun Mehta
"""
    files = {"file": ("test_anpr.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"dataset_type": "anpr"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "DATASET_UPLOAD_SUCCESS"
    assert res["dataset_type"] == "ANPR"
    assert res["records_processed"] == 1

def test_upload_valid_wallet_csv():
    csv_content = """sender_wallet,receiver_wallet,amount,timestamp,sender_name,receiver_name
WAL-UPI-ARJUN@OKAXIS,WAL-PAYTM-HAWALA01,95000.0,2026-03-12 02:10:00,Arjun Mehta,Quick Cash Settlement Desk
"""
    files = {"file": ("test_wallet.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"dataset_type": "wallet"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "DATASET_UPLOAD_SUCCESS"
    assert res["dataset_type"] == "WALLET"
    assert res["records_processed"] == 1

def test_upload_missing_required_columns():
    csv_content = """caller,timestamp,duration_sec
+91-9876543210,2026-03-12 01:34:10,342
"""
    files = {"file": ("bad_cdr.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"dataset_type": "cdr"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "missing_columns" in detail
    assert "receiver" in detail["missing_columns"]

def test_upload_empty_csv():
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    data = {"dataset_type": "cdr"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]["message"].lower()

def test_upload_non_csv_extension():
    files = {"file": ("malicious.exe", io.BytesIO(b"binary data"), "application/octet-stream")}
    data = {"dataset_type": "cdr"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 400
    assert "only csv files" in response.json()["detail"]["message"].lower()

def test_upload_unsupported_dataset_type():
    csv_content = "col1,col2\nval1,val2\n"
    files = {"file": ("data.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"dataset_type": "invalid_domain"}
    response = client.post("/api/pipeline/upload-csv", files=files, data=data)
    assert response.status_code == 400
    assert "unsupported dataset type" in response.json()["detail"]["message"].lower()

def test_cross_domain_linking_via_csv_uploads():
    cdr_csv = """caller,receiver,timestamp
+91-9876543210,+91-9845678901,2026-03-12 01:34:10
"""
    client.post("/api/pipeline/upload-csv", files={"file": ("cdr.csv", io.BytesIO(cdr_csv.encode("utf-8")), "text/csv")}, data={"dataset_type": "cdr"})

    bank_csv = """from_account,to_account,amount,timestamp,from_name,linked_phone
ACC-TEST-999,ACC-TEST-888,50000.0,2026-03-12 01:45:00,Arjun Mehta,+91-9876543210
"""
    res = client.post("/api/pipeline/upload-csv", files={"file": ("bank.csv", io.BytesIO(bank_csv.encode("utf-8")), "text/csv")}, data={"dataset_type": "banking"})
    assert res.status_code == 200
    links = res.json()["links"]
    has_cross_domain = any(l["label"] == "CROSS_DOMAIN_IDENTITY" for l in links)
    assert has_cross_domain
