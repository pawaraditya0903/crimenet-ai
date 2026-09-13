import pytest
import networkx as nx
from backend.app.graph.communities import compute_communities

def test_louvain_identifies_known_synthetic_clusters():
    G = nx.DiGraph()
    # Cluster 1: Hawala Desks
    for u in ["H1", "H2", "H3", "H4"]:
        for v in ["H1", "H2", "H3", "H4"]:
            if u != v: G.add_edge(u, v, weight=2.0)

    # Cluster 2: Logistics Transport
    for u in ["L1", "L2", "L3", "L4"]:
        for v in ["L1", "L2", "L3", "L4"]:
            if u != v: G.add_edge(u, v, weight=2.0)

    # Single connecting courier
    G.add_edge("H4", "L1", weight=0.2)

    res = compute_communities(G, resolution=1.0)
    assert res["total_communities"] == 2
    assert res["modularity_score_Q"] > 0.35

    # Check that H nodes belong to one community and L nodes to the other
    comm1_members = {m["name"] for m in res["communities"][0]["members"]}
    comm2_members = {m["name"] for m in res["communities"][1]["members"]}

    assert (comm1_members == {"H1", "H2", "H3", "H4"} and comm2_members == {"L1", "L2", "L3", "L4"}) or \
           (comm1_members == {"L1", "L2", "L3", "L4"} and comm2_members == {"H1", "H2", "H3", "H4"})
