import math
from typing import List, Dict, Any

BENFORD_LIMITATIONS = (
    "STATISTICAL METHODOLOGY & LIMITATIONS: Benford's Law applies to naturally occurring, "
    "scale-invariant datasets spanning multiple orders of magnitude without artificial minimums or maximums. "
    "A statistically significant deviation indicates numerical clustering (e.g. structured smurfing "
    "below statutory reporting thresholds); it does NOT constitute judicial proof of fraud or intent."
)

def _chi2_sf(x: float, df: int = 8) -> float:
    """Approximation of Chi-Square Survival Function (p-value) for df=8."""
    if x <= 0:
        return 1.0
    # For df=8: k=4. Gamma(4) = 6.
    # CDF for even df=2k: 1 - exp(-x/2) * sum_{j=0}^{k-1} (x/2)^j / j!
    # SF = exp(-x/2) * sum_{j=0}^{3} (x/2)^j / j!
    s = x / 2.0
    term = 1.0 + s + (s**2) / 2.0 + (s**3) / 6.0
    p_val = math.exp(-s) * term
    return max(0.0, min(1.0, p_val))

def run_benford_analysis(numbers: List[float]) -> Dict[str, Any]:
    """Applies Benford's First-Digit Analysis across input transaction amounts."""
    # Filter valid positive numbers
    clean_nums = [n for n in numbers if n > 0]
    total_n = len(clean_nums)

    if total_n < 30:
        return {
            "status": "INSUFFICIENT_DATA",
            "total_records": total_n,
            "error": "Benford analysis requires a minimum sample size of 30 records for statistical validity.",
            "limitations": BENFORD_LIMITATIONS
        }

    # Count observed leading digits 1..9
    observed = {d: 0 for d in range(1, 10)}
    for val in clean_nums:
        s = f"{val:.6f}".lstrip("0").replace(".", "")
        if s and s[0].isdigit() and int(s[0]) > 0:
            observed[int(s[0])] += 1

    # Theoretical probabilities under Benford's logarithmic curve
    expected_prob = {d: math.log10(1.0 + 1.0 / d) for d in range(1, 10)}
    expected_counts = {d: total_n * expected_prob[d] for d in range(1, 10)}

    chi_square = 0.0
    distribution_comparison = []

    for d in range(1, 10):
        obs = observed[d]
        exp = expected_counts[d]
        diff_sq = ((obs - exp) ** 2) / max(exp, 0.001)
        chi_square += diff_sq

        distribution_comparison.append({
            "digit": d,
            "observed_count": obs,
            "expected_count": round(exp, 1),
            "observed_percentage": round((obs / total_n) * 100, 2),
            "expected_percentage": round(expected_prob[d] * 100, 2),
            "chi2_contribution": round(diff_sq, 3)
        })

    # Critical value for df = 8 at alpha = 0.05 is 15.507
    critical_threshold = 15.507
    is_anomalous = chi_square > critical_threshold
    p_value = round(_chi2_sf(chi_square, df=8), 5)

    return {
        "status": "COMPLETED",
        "sample_size": total_n,
        "degrees_of_freedom": 8,
        "chi_square_statistic": round(chi_square, 3),
        "critical_threshold_alpha_0_05": critical_threshold,
        "p_value": p_value,
        "is_statistically_deviant": is_anomalous,
        "investigative_interpretation": (
            "Statistically significant deviation from Benford curve detected (p < 0.05); "
            "consistent with artificial number clustering or sub-threshold smurfing."
            if is_anomalous else
            "Numbers conform to expected natural logarithmic distribution within standard variance."
        ),
        "digit_distributions": distribution_comparison,
        "methodology_and_limitations": BENFORD_LIMITATIONS
    }
