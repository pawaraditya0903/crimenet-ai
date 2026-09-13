import pytest
import networkx as nx
from backend.app.graph.centrality import compute_centralities

def test_pagerank_damping_factor_influence():
    G = nx.DiGraph()
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "C", weight=1.0)
    G.add_edge("C", "A", weight=1.0)
    G.add_edge("D", "A", weight=1.0)

    # Standard damping 0.85
    res_85 = compute_centralities(G, damping_factor=0.85)
    # Low damping 0.50
    res_50 = compute_centralities(G, damping_factor=0.50)

    pr_85 = {item["name"]: item["pagerank"] for item in res_85["influencers"]}
    pr_50 = {item["name"]: item["pagerank"] for item in res_50["influencers"]}

    # Node A receives inbound link from D, so should have highest PageRank
    assert pr_85["A"] >= pr_85["B"]
    # With lower damping, scores are pulled closer to uniform 1/N
    assert abs(pr_50["A"] - 0.25) < abs(pr_85["A"] - 0.25)
