import pytest
import networkx as nx
from backend.app.graph.centrality import compute_centralities
from backend.app.graph.communities import compute_communities
from backend.app.graph.paths import find_shortest_path
from backend.app.graph.cycles import detect_financial_cycles

def test_centrality_and_pagerank_convergence():
    G = nx.DiGraph()
    # Star graph topology with a central hub
    G.add_edge("Hub", "Leaf1", weight=1.0)
    G.add_edge("Hub", "Leaf2", weight=1.0)
    G.add_edge("Hub", "Leaf3", weight=1.0)
    G.add_edge("Leaf1", "Hub", weight=2.0)
    G.add_edge("Leaf2", "Hub", weight=2.0)
    G.add_edge("Leaf3", "Hub", weight=2.0)

    res = compute_centralities(G, damping_factor=0.85)
    assert res["status"] == "CONVERGED"
    assert res["nodes_scored"] == 4
    
    influencers = {item["name"]: item for item in res["influencers"]}
    assert "Hub" in influencers
    # Hub should have the highest PageRank and betweenness
    assert influencers["Hub"]["pagerank"] > influencers["Leaf1"]["pagerank"]
    assert influencers["Hub"]["betweenness"] >= influencers["Leaf1"]["betweenness"]

def test_louvain_community_detection_and_modularity():
    G = nx.DiGraph()
    # 2 distinct cliques connected by a single bridge edge
    for u in ["A1", "A2", "A3"]:
        for v in ["A1", "A2", "A3"]:
            if u != v: G.add_edge(u, v, weight=1.0)
    for u in ["B1", "B2", "B3"]:
        for v in ["B1", "B2", "B3"]:
            if u != v: G.add_edge(u, v, weight=1.0)
    G.add_edge("A3", "B1", weight=0.1)  # Bridge

    res = compute_communities(G, resolution=1.0)
    assert res["total_communities"] == 2
    assert res["modularity_score_Q"] > 0.30  # High modularity for separate cliques

def test_dijkstra_shortest_path_calculation():
    G = nx.DiGraph()
    G.add_edge("A", "B", weight=1.5, label="WIRED")
    G.add_edge("B", "C", weight=2.5, label="TRANSFER")
    G.add_edge("A", "C", weight=10.0, label="DIRECT")

    res = find_shortest_path(G, "A", "C", weighted=True)
    assert res["found"] is True
    assert res["path"] == ["A", "B", "C"]  # 1.5 + 2.5 = 4.0 < 10.0
    assert res["total_path_cost"] == 4.0
    assert res["hop_count"] == 2

def test_financial_cycle_detection():
    G = nx.DiGraph()
    G.add_edge("CompanyA", "CompanyB", weight=1.0)
    G.add_edge("CompanyB", "CompanyC", weight=1.0)
    G.add_edge("CompanyC", "CompanyA", weight=1.0)  # 3-hop closed cycle
    G.add_edge("CompanyC", "CompanyD", weight=1.0)

    res = detect_financial_cycles(G, min_hops=2, max_hops=4)
    assert res["total_cycles_detected"] == 1
    cycle = res["cycles"][0]
    assert cycle["hop_count"] == 3
    assert set(cycle["entities"]) == {"CompanyA", "CompanyB", "CompanyC"}
