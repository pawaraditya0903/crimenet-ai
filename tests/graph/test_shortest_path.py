import pytest
import networkx as nx
from backend.app.graph.paths import find_shortest_path

def test_weighted_shortest_path_chooses_lower_weight():
    G = nx.DiGraph()
    # Path 1: A -> B -> D (Weight: 1 + 2 = 3)
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "D", weight=2.0)
    # Path 2: A -> C -> D (Weight: 4 + 4 = 8)
    G.add_edge("A", "C", weight=4.0)
    G.add_edge("C", "D", weight=4.0)

    res = find_shortest_path(G, "A", "D", weighted=True)
    assert res["found"] is True
    assert res["path"] == ["A", "B", "D"]
    assert res["total_path_cost"] == 3.0

def test_missing_node_shortest_path():
    G = nx.DiGraph()
    G.add_edge("A", "B")
    res = find_shortest_path(G, "A", "NonExistentNode")
    assert res["found"] is False
