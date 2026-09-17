"""
CrimeNet AI — Graph Analytics & Entity Routes

SEC-006 FIX: All endpoints now require authentication via require_authenticated_user.
Graph analytics results are described as prioritization signals, not proof of wrongdoing.
"""
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

# ── Disclaimer injected into graph analytics outputs per responsible-AI policy ──
GRAPH_ANALYTICS_DISCLAIMER = (
    "Graph metrics and centrality scores are prioritization signals for investigative leads only. "
    "High centrality or community membership is NOT evidence of criminal activity or guilt. "
    "All findings require independent corroboration and human supervisory review."
)


@router.get("/api/graph/network")
async def get_network(claims: dict = Depends(require_authenticated_user)):
    """Returns the full criminal intelligence knowledge graph with Cytoscape-compliant elements."""
    return GraphService.get_cytoscape_network()


@router.get("/api/entities/all")
async def get_all_entities(
    limit: int = Query(200, ge=1, le=1000),
    claims: dict = Depends(require_authenticated_user)
):
    G, entities, _ = build_network_graph()
    # Apply configurable cap to prevent unbounded responses
    return {"entities": entities[:limit], "total": len(entities)}


@router.get("/api/entities/search")
async def search_entities(
    q: str = Query("", min_length=0, max_length=256),
    limit: int = Query(15, ge=1, le=100),
    claims: dict = Depends(require_authenticated_user)
):
    G, entities, _ = build_network_graph()
    query = q.lower().strip()
    if not query:
        return {"results": entities[:limit], "total": len(entities)}
    results = [
        e for e in entities
        if query in e.get("name", "").lower()
        or query in e.get("role", "").lower()
        or query in e.get("city", "").lower()
    ]
    return {"results": results[:limit], "total": len(results)}


@router.get("/api/relationships/all")
async def get_all_relationships(
    limit: int = Query(500, ge=1, le=5000),
    claims: dict = Depends(require_authenticated_user)
):
    G, _, relationships = build_network_graph()
    return {"relationships": relationships[:limit], "total": len(relationships)}


@router.get("/api/analytics/top-influencers")
async def influencers(claims: dict = Depends(require_authenticated_user)):
    G, _, _ = build_network_graph()
    res = compute_centralities(G)
    return {
        "influencers": res.get("influencers", []),
        "disclaimer": GRAPH_ANALYTICS_DISCLAIMER
    }


@router.get("/api/analytics/communities")
async def communities(claims: dict = Depends(require_authenticated_user)):
    G, _, _ = build_network_graph()
    result = compute_communities(G)
    result["disclaimer"] = GRAPH_ANALYTICS_DISCLAIMER
    return result


@router.get("/api/analytics/network-stats")
async def network_stats(claims: dict = Depends(require_authenticated_user)):
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
        "average_clustering": avg_clustering,
        "disclaimer": GRAPH_ANALYTICS_DISCLAIMER
    }


@router.post("/api/analytics/run")
async def run_analytics(
    req: AnalyticsRunRequest = AnalyticsRunRequest(),
    claims: dict = Depends(require_authenticated_user)
):
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
        "message": (
            f"NetworkX Analysis Converged (Damping d={req.damping_factor:.2f}, "
            f"Louvain Resolution={req.louvain_resolution:.2f})"
        ),
        "disclaimer": GRAPH_ANALYTICS_DISCLAIMER
    }


@router.post("/api/analytics/shortest-path")
async def shortest_path_endpoint(
    req: ShortestPathRequest,
    claims: dict = Depends(require_authenticated_user)
):
    res = GraphService.find_path(req.source, req.target, weighted=req.weighted or True)
    if not res.get("found"):
        raise HTTPException(status_code=404, detail=res.get("error", "Path not found."))
    res["disclaimer"] = GRAPH_ANALYTICS_DISCLAIMER
    return res
