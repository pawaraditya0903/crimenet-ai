import math
from typing import List, Dict, Any

def analyze_cdr_telemetry(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyzes Call Detail Records (CDR) for nocturnal clustering, call bursts, and burner SIM swaps."""
    if not records:
        return {"status": "EMPTY_BATCH", "error": "No CDR records provided."}

    total_calls = len(records)
    hourly_histogram = [0] * 24
    nocturnal_count = 0
    imei_to_imsis: Dict[str, set] = {}
    tower_counts: Dict[str, int] = {}
    unique_contacts: set = set()

    for r in records:
        ts = str(r.get("timestamp", ""))
        try:
            time_part = ts.split(" ")[1] if " " in ts else ts
            hour = int(time_part.split(":")[0])
            if 0 <= hour <= 23:
                hourly_histogram[hour] += 1
                if 1 <= hour <= 4:
                    nocturnal_count += 1
        except Exception:
            pass

        imei = str(r.get("imei", "UNKNOWN"))
        imsi = str(r.get("imsi", "UNKNOWN"))
        if imei not in imei_to_imsis:
            imei_to_imsis[imei] = set()
        imei_to_imsis[imei].add(imsi)

        t_id = str(r.get("tower_id", "DEFAULT_TOWER"))
        tower_counts[t_id] = tower_counts.get(t_id, 0) + 1

        caller = r.get("caller")
        receiver = r.get("receiver")
        if caller: unique_contacts.add(caller)
        if receiver: unique_contacts.add(receiver)

    # 1. Nocturnal Ratio
    nocturnal_ratio = round((nocturnal_count / total_calls) * 100.0, 1)

    # 2. Hourly Z-Score Burst
    hourly_mean = total_calls / 24.0
    variance = sum((h - hourly_mean) ** 2 for h in hourly_histogram) / 24.0
    hourly_std = math.sqrt(variance) or 1.0
    max_hour_count = max(hourly_histogram)
    z_score_burst = round((max_hour_count - hourly_mean) / hourly_std, 2)

    # 3. Burner SIM Multiplexing
    max_sims_per_handset = max(len(s) for s in imei_to_imsis.values()) if imei_to_imsis else 1
    burner_swap_detected = max_sims_per_handset >= 2

    # 4. Threat Indicator
    composite_threat = min(98.0, round(
        40.0 + (z_score_burst * 7.5) + (nocturnal_ratio * 0.35) + (20.0 if burner_swap_detected else 0.0), 1
    ))

    top_tower = max(tower_counts, key=tower_counts.get) if tower_counts else "Unknown Tower"

    return {
        "status": "ANALYZED",
        "total_calls_parsed": total_calls,
        "unique_contacts_count": len(unique_contacts),
        "nocturnal_ratio_pct": nocturnal_ratio,
        "hourly_call_histogram": hourly_histogram,
        "z_score_burst": z_score_burst,
        "is_burst_anomaly": z_score_burst >= 2.5,
        "unique_handsets_imei": len(imei_to_imsis),
        "max_sims_per_handset": max_sims_per_handset,
        "burner_sim_swap_detected": burner_swap_detected,
        "primary_cell_tower": top_tower,
        "composite_telecom_threat_score": composite_threat,
        "investigative_assessment": (
            "Anomalous nocturnal burst and hardware multiplexing detected; recommends formal verification against lawful call intercept metadata."
            if (burner_swap_detected or z_score_burst >= 2.5) else
            "Standard telecommunication pattern within baseline variance limits."
        )
    }
