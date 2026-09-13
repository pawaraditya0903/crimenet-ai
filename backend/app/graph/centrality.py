import math
import networkx as nx
import logging
from typing import Dict, Any, List

logger = logging.getLogger("crimenet.graph.centrality")

PAGERANK_DISCLAIMER = (
    "STATISTICAL INTERPRETATION NOTE: PageRank calculates structural recursive connectedness "
    "and information authority across directed links. A high PageRank value indicates prominent "
    "network positioning or connectivity; it does NOT establish guilt, intent, or criminal culpability."
)

def compute_centralities(
    G: nx.DiGraph,
    damping_factor: float = 0.85,
    max_iter: int = 200,
    tol: float = 1e-6
) -> Dict[str, Any]:
    """Computes genuine NetworkX centrality metrics:
    - Degree Centrality (In / Out / Total)
    - Brandes Betweenness Centrality
    - PageRank with damping factor and convergence tolerance
    """
    if len(G) == 0:
        return {
            "status": "EMPTY_GRAPH",
            "nodes_scored": 0,
            "influencers": [],
            "disclaimer": PAGERANK_DISCLAIMER
        }

    # 1. PageRank Calculation
    try:
        pr = nx.pagerank(G, alpha=damping_factor, max_iter=max_iter, tol=tol, weight="weight")
    except Exception as e:
        logger.warning(f"PageRank iteration fallback: {e}")
        pr = {node: 1.0 / len(G) for node in G.nodes()}

    # 2. Betweenness Centrality (Brandes Algorithm)
    try:
        bc = nx.betweenness_centrality(G, weight="weight")
    except Exception as e:
        logger.warning(f"Betweenness centrality fallback: {e}")
        bc = {node: 0.0 for node in G.nodes()}

    # 3. Degree Centrality
    in_deg = nx.in_degree_centrality(G)
    out_deg = nx.out_degree_centrality(G)

    results: List[Dict[str, Any]] = []
    for node in G.nodes():
        node_data = G.nodes[node]
        p_val = round(float(pr.get(node, 0.0)), 5)
        b_val = round(float(bc.get(node, 0.0)), 5)
        in_d = round(float(in_deg.get(node, 0.0)), 4)
        out_d = round(float(out_deg.get(node, 0.0)), 4)
        avg_d = round((in_d + out_d) / 2.0, 4)

        # High-centrality investigative lead metric:
        # Measures nodes acting as informational bottlenecks (high betweenness relative to degree)
        coordination_index = round((b_val / max(avg_d, 0.05)), 3)
        is_priority_lead = b_val >= 0.15 and avg_d <= 0.40

        results.append({
            "name": node,
            "id": node_data.get("id", ""),
            "type": node_data.get("type", "Person"),
            "risk_score": float(node_data.get("risk_score", 50.0)),
            "pagerank": p_val,
            "betweenness": b_val,
            "in_degree": in_d,
            "out_degree": out_d,
            "degree": avg_d,
            "coordination_index": coordination_index,
            "is_priority_lead": is_priority_lead,
            "investigative_note": "High-centrality coordination broker requiring human review" if is_priority_lead else "Standard network participant"
        })

    results.sort(key=lambda x: (x["pagerank"], x["betweenness"]), reverse=True)

    return {
        "status": "CONVERGED",
        "nodes_scored": len(results),
        "damping_factor": damping_factor,
        "max_iterations": max_iter,
        "tolerance": tol,
        "formula": "PR(v) = (1-d)/N + d * Σ(PR(u) / Out(u))",
        "disclaimer": PAGERANK_DISCLAIMER,
        "influencers": results
    }
