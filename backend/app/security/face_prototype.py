import math
from typing import List, Dict, Any

FACE_PROTOTYPE_DISCLAIMER = (
    "PROTOTYPE DISCLAIMER: This facial similarity verification mechanism applies Zero-Normalized "
    "Cross-Correlation (ZNCC) across feature vectors for demonstration and testing purposes. It does NOT "
    "satisfy ISO/IEC 30107-3 Presentation Attack Detection standards and must NOT be deployed as an "
    "exclusive production biometric authentication system."
)

def compute_zncc_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Computes Zero-Normalized Cross-Correlation (ZNCC) percentage [0 to 100]."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    mean_a = sum(vec_a) / len(vec_a)
    mean_b = sum(vec_b) / len(vec_b)

    norm_a = [a - mean_a for a in vec_a]
    norm_b = [b - mean_b for b in vec_b]

    dot_product = sum(a * b for a, b in zip(norm_a, norm_b))
    var_a = math.sqrt(sum(a * a for a in norm_a))
    var_b = math.sqrt(sum(b * b for b in norm_b))

    if var_a == 0 or var_b == 0:
        return 0.0

    r = dot_product / (var_a * var_b)
    if r < 0:
        return 0.0

    return round(r * 100.0, 1)

def evaluate_face_prototype(
    probe_vector: List[float],
    master_vector: List[float],
    threshold: float = 62.0
) -> Dict[str, Any]:
    """Evaluates probe facial vector against enrolled master vector."""
    if not master_vector:
        return {
            "authorized": False,
            "similarity_percentage": 0.0,
            "threshold_required": threshold,
            "status": "NO_MASTER_ENROLLED",
            "message": "No master face vector enrolled on the server.",
            "disclaimer": FACE_PROTOTYPE_DISCLAIMER
        }

    similarity = compute_zncc_similarity(probe_vector, master_vector)
    is_match = similarity >= threshold

    return {
        "authorized": is_match,
        "similarity_percentage": similarity,
        "threshold_required": threshold,
        "status": "AUTHORIZED_DEMO" if is_match else "REJECTED_MISMATCH",
        "message": f"Similarity score: {similarity}% (Required: {threshold}%).",
        "disclaimer": FACE_PROTOTYPE_DISCLAIMER
    }
