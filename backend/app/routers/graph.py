import networkx as nx
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from backend.app.schemas.analytics import AnalyticsRunRequest, ShortestPathRequest
from backend.app.security.rbac import require_authenticated_user
from backend.app.graph.engine import build_network_graph
from backend.app.graph.centrality import compute_centralities
from backend.app.graph.communities import compute_communities
from backend.app.graph.paths import find_shortest_path
from backend.app.services.graph_service import GraphService

router = APIRouter(tags=["Graph Analytics"])

@router.get("/api/graph/network")
async def get_network():
    """Returns the full criminal intelligence knowledge graph with Cytoscape-compliant elements."""
    return GraphService.get_cytoscape_network()


@router.get("/api/entities/all")
async def get_all_entities():
    G, entities, _ = build_network_graph()
    return {"entities": entities, "total": len(entities)}

@router.get("/api/entities/search")
async def search_entities(q: str = Query("", min_length=0)):
    G, entities, _ = build_network_graph()
    query = q.lower().strip()
    if not query:
        return {"results": entities[:15], "total": len(entities)}
    results = [
        e for e in entities
        if query in e.get("name", "").lower() or query in e.get("role", "").lower() or query in e.get("city", "").lower()
    ]
    return {"results": results, "total": len(results)}

@router.get("/api/relationships/all")
async def get_all_relationships():
    G, _, relationships = build_network_graph()
    return {"relationships": relationships, "total": len(relationships)}

@router.get("/api/analytics/top-influencers")
async def influencers():
    G, _, _ = build_network_graph()
    res = compute_centralities(G)
    return {"influencers": res.get("influencers", [])}

@router.get("/api/analytics/communities")
async def communities():
    G, _, _ = build_network_graph()
    return compute_communities(G)

@router.get("/api/analytics/network-stats")
async def network_stats():
    G, entities, relationships = build_network_graph()
    G_undir = G.to_undirected()

    density = round(nx.density(G), 4) if len(G) > 0 else 0.0
    avg_clustering = round(nx.average_clustering(G_undir), 4) if len(G_undir) > 0 else 0.0
    num_components = nx.number_weakly_connected_components(G) if len(G) > 0 else 0

    return {
        "total_nodes": len(entities),
        "total_edges": len(relationships),
        "density": density,
        "weakly_connected_components": num_components,
        "average_clustering": avg_clustering
    }

@router.post("/api/analytics/run")
async def run_analytics(req: AnalyticsRunRequest = AnalyticsRunRequest()):
    G, _, _ = build_network_graph()
    centralities = compute_centralities(G, damping_factor=req.damping_factor or 0.85)
    comm = compute_communities(G, resolution=req.louvain_resolution or 1.0)
    
    return {
        "status": "CONVERGED",
        "damping_factor": req.damping_factor,
        "louvain_resolution": req.louvain_resolution,
        "influencers": centralities.get("influencers", []),
        "communities": comm.get("communities", []),
        "modularity_score_Q": comm.get("modularity_score_Q", 0.0),
        "message": f"NetworkX Analysis Converged (Damping d={req.damping_factor:.2f}, Louvain Resolution={req.louvain_resolution:.2f})"
    }

@router.post("/api/analytics/shortest-path")
async def shortest_path_endpoint(req: ShortestPathRequest):
    res = GraphService.find_path(req.source, req.target, weighted=req.weighted or True)
    if not res.get("found"):
        raise HTTPException(status_code=404, detail=res.get("error", "Path not found."))
    return res
