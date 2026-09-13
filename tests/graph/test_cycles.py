import pytest
import networkx as nx
from backend.app.graph.cycles import detect_financial_cycles

def test_bounded_cycle_detection():
    G = nx.DiGraph()
    # 2-node cycle: A <-> B
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "A", weight=1.0)

    # 4-node cycle: C -> D -> E -> F -> C
    G.add_edge("C", "D", weight=1.0)
    G.add_edge("D", "E", weight=1.0)
    G.add_edge("E", "F", weight=1.0)
    G.add_edge("F", "C", weight=1.0)

    # Detect 2-hop to 5-hop cycles
    res = detect_financial_cycles(G, min_hops=2, max_hops=5)
    assert res["total_cycles_detected"] == 2
    
    hop_counts = {c["hop_count"] for c in res["cycles"]}
    assert 2 in hop_counts
    assert 4 in hop_counts
