import networkx as nx
from typing import Dict, Any, List

def detect_financial_cycles(G: nx.DiGraph, min_hops: int = 2, max_hops: int = 6) -> Dict[str, Any]:
    """Detects closed circular flow loops using Johnson's simple cycles algorithm.
    Filters cycles between min_hops and max_hops for detecting potential Hawala round-tripping.
    """
    if len(G) == 0:
        return {"total_cycles_detected": 0, "cycles": []}

    all_cycles = list(nx.simple_cycles(G))
    filtered_cycles = [c for c in all_cycles if min_hops <= len(c) <= max_hops]

    formatted_cycles: List[Dict[str, Any]] = []
    for idx, cycle_nodes in enumerate(filtered_cycles, start=1):
        flow_str = " ➔ ".join(cycle_nodes + [cycle_nodes[0]])
        
        # Calculate aggregate cycle edge weight
        cycle_weight = 0.0
        for i in range(len(cycle_nodes)):
            u = cycle_nodes[i]
            v = cycle_nodes[(i + 1) % len(cycle_nodes)]
            edge = G.get_edge_data(u, v) or {}
            cycle_weight += float(edge.get("weight", 1.0))

        formatted_cycles.append({
            "cycle_id": f"CYCLE-AML-{idx:02d}",
            "hop_count": len(cycle_nodes),
            "entities": cycle_nodes,
            "flow_description": flow_str,
            "cumulative_cycle_weight": round(cycle_weight, 2),
            "classification": "POTENTIALLY_SUSPICIOUS_CIRCULAR_ROUTING",
            "investigative_guidance": "Closed financial flow loop detected; requires human audit of underlying invoices and customs filings."
        })

    return {
        "algorithm": "Johnson's Directed Simple Cycles (NetworkX)",
        "total_cycles_detected": len(formatted_cycles),
        "cycles": formatted_cycles
    }
