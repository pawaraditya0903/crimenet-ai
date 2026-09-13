import networkx as nx
from typing import Dict, Any, List

def find_shortest_path(G: nx.DiGraph, source: str, target: str, weighted: bool = True) -> Dict[str, Any]:
    """Calculates genuine Dijkstra shortest path across weighted or unweighted directed graph edges.
    Returns the ordered path, hop count, and cumulative traversal cost.
    """
    if not G.has_node(source):
        return {
            "found": False,
            "source": source,
            "target": target,
            "error": f"Source entity '{source}' does not exist in graph topology."
        }
    if not G.has_node(target):
        return {
            "found": False,
            "source": source,
            "target": target,
            "error": f"Target entity '{target}' does not exist in graph topology."
        }

    weight_attr = "weight" if weighted else None

    # Try directed path first
    try:
        path = nx.shortest_path(G, source=source, target=target, weight=weight_attr)
        cost = round(float(nx.shortest_path_length(G, source=source, target=target, weight=weight_attr)), 3)
        is_directed = True
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        # Fallback to undirected traversal if no directed flow exists
        G_undir = G.to_undirected()
        try:
            path = nx.shortest_path(G_undir, source=source, target=target, weight=weight_attr)
            cost = round(float(nx.shortest_path_length(G_undir, source=source, target=target, weight=weight_attr)), 3)
            is_directed = False
        except nx.NetworkXNoPath:
            return {
                "found": False,
                "source": source,
                "target": target,
                "error": f"No connected pathway exists between '{source}' and '{target}' in the network."
            }

    # Extract intermediate hop metadata
    hops_detail: List[Dict[str, Any]] = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        edge_data = G.get_edge_data(u, v) or G.get_edge_data(v, u) or {}
        hops_detail.append({
            "step": i + 1,
            "from_node": u,
            "to_node": v,
            "label": edge_data.get("label", "ASSOCIATED_WITH"),
            "weight": edge_data.get("weight", 1.0)
        })

    return {
        "found": True,
        "algorithm": "Dijkstra's Shortest Path (NetworkX)",
        "source": source,
        "target": target,
        "hop_count": len(path) - 1,
        "total_path_cost": cost,
        "is_strictly_directed": is_directed,
        "path": path,
        "hops": hops_detail,
        "citations": [f"[Entity: {n}]" for n in path]
    }
