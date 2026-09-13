import networkx as nx
import networkx.algorithms.community as nx_comm
import logging
from typing import Dict, Any, List

logger = logging.getLogger("crimenet.graph.communities")

COMMUNITY_COLORS = ["#ef4444", "#f97316", "#3b82f6", "#10b981", "#8b5cf6", "#ec4899", "#14b8a6"]

def compute_communities(G: nx.DiGraph, resolution: float = 1.0) -> Dict[str, Any]:
    """Applies the genuine Louvain Community Detection algorithm (NetworkX 3.6+)
    to unearth structural sub-syndicates and clusters, and computes the modularity score (Q).
    """
    if len(G) == 0:
        return {"total_communities": 0, "modularity": 0.0, "communities": []}

    G_undir = G.to_undirected()

    try:
        # Genuine Louvain Community Detection
        comm_sets = nx_comm.louvain_communities(G_undir, resolution=resolution, seed=42)
    except Exception as e:
        logger.warning(f"Louvain execution error: {e}, falling back to greedy modularity")
        comm_sets = nx_comm.greedy_modularity_communities(G_undir, resolution=resolution)

    # Compute genuine modularity Q
    try:
        q_score = round(float(nx_comm.modularity(G_undir, comm_sets)), 4)
    except Exception:
        q_score = 0.0

    communities_formatted: List[Dict[str, Any]] = []
    for idx, c_nodes in enumerate(comm_sets, start=1):
        color = COMMUNITY_COLORS[(idx - 1) % len(COMMUNITY_COLORS)]
        members = []
        for n in c_nodes:
            node_data = G.nodes.get(n, {})
            members.append({
                "id": node_data.get("id", f"n-{n}"),
                "name": n,
                "type": node_data.get("type", "Person"),
                "risk_score": float(node_data.get("risk_score", 50.0))
            })
        
        # Sort members by threat index
        members.sort(key=lambda m: m["risk_score"], reverse=True)

        communities_formatted.append({
            "community_id": idx,
            "name": f"Syndicate Cluster {idx}",
            "color": color,
            "size": len(members),
            "members": members
        })

    # Sort communities by size descending
    communities_formatted.sort(key=lambda c: c["size"], reverse=True)

    return {
        "algorithm": "Louvain Modularity Optimization (NetworkX)",
        "resolution_parameter": resolution,
        "modularity_score_Q": q_score,
        "total_communities": len(communities_formatted),
        "communities": communities_formatted
    }
