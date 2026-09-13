import networkx as nx
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from backend.app.schemas.analytics import AnalyticsRunRequest, ShortestPathRequest
from backend.app.security.rbac import require_authenticated_user
from backend.app.graph.engine import build_network_graph
from backend.app.graph.centrality import compute_centralities
from backend.app.graph.communities import compute_communities
from backend.app.graph.paths import find_shortest_path

router = APIRouter(tags=["Graph Analytics"])

@router.get("/api/graph/network")
async def get_network():
    """Returns the full criminal intelligence knowledge graph with Cytoscape-compliant elements."""
    G, entities, relationships = build_network_graph()

    ID_MAP = {
        "Arjun Mehta": "n1",
        "Mohammed Rafiq": "n2",
        "Vikram Singh": "n3",
        "Priya Desai": "n4",
        "Mehta Enterprises Ltd": "n5",
        "+91-9876543210": "n6",
        "Goregaon Warehouse": "n7",
        "Goregaon Tower 4041": "n7_tower",
        "BMW X5 (MH-01-AB)": "n8",
        "Phoenix Trading LLC": "n9",
        "Phoenix Trading LLC (Dubai)": "n9",
        "Al-Rafiq Trading Co": "n10",
        "Bandra West Safehouse": "n11",
        "Mercedes G-Wagon": "n12",
        "Desai Financial Consultancy": "n13",
        "Mule Account Hub A": "n14",
        "Mule Account Hub B": "n15",
        "Crypto Tumbler Gateway": "n16"
    }

    color_map = {
        "Person": "#ef4444",
        "Organization": "#a855f7",
        "PhoneNumber": "#38bdf8",
        "Location": "#10b981",
        "Vehicle": "#6366f1",
        "FinancialAccount": "#06b6d4",
        "CryptoWallet": "#ec4899",
        "CellTower": "#f59e0b"
    }

    name_to_nid = {}
    nodes = []
    seen_node_ids = set()

    for idx, e in enumerate(entities, 1):
        name = e["name"]
        raw_id = e.get("id") or f"n{idx}"
        nid = ID_MAP.get(name, raw_id)
        if nid in seen_node_ids:
            nid = f"{nid}_{idx}"
        seen_node_ids.add(nid)

        name_to_nid[name] = nid
        name_to_nid[name.strip()] = nid
        name_to_nid[name.lower()] = nid
        if raw_id:
            name_to_nid[raw_id] = nid
        name_to_nid[nid] = nid

        risk = float(e.get("risk_score", 50.0))
        ntype = e.get("type", "Person")
        color = color_map.get(ntype, "#38bdf8")
        if ntype == "Person":
            color = "#ef4444" if risk >= 85 else "#f97316" if risk >= 75 else "#eab308"
        size = 48 + int((risk / 100) * 20)

        nodes.append({
            "id": nid,
            "name": name,
            "label": f"{name} (Kingpin)" if nid == "n1" else name,
            "type": ntype,
            "tier": e.get("tier", "core"),
            "category": e.get("category", "general"),
            "role": e.get("dossier", "").split(".")[0][:45] or ntype,
            "risk_score": risk,
            "risk": risk,
            "color": color,
            "size": size,
            "city": e.get("city", "")
        })

    valid_node_ids = {n["id"] for n in nodes}

    edges = []
    seen_edge_ids = set()
    for idx, r in enumerate(relationships, 1):
        src_raw = r["source"]
        tgt_raw = r["target"]
        src_id = name_to_nid.get(src_raw) or name_to_nid.get(src_raw.strip()) or name_to_nid.get(src_raw.lower())
        tgt_id = name_to_nid.get(tgt_raw) or name_to_nid.get(tgt_raw.strip()) or name_to_nid.get(tgt_raw.lower())

        # Crucial for Cytoscape: only create edge if both source and target exist in nodes
        if src_id and tgt_id and src_id in valid_node_ids and tgt_id in valid_node_ids:
            eid = r.get("id") or f"e{idx}"
            if eid in seen_edge_ids:
                eid = f"{eid}_{idx}"
            seen_edge_ids.add(eid)

            edges.append({
                "id": eid,
                "source": src_id,
                "target": tgt_id,
                "label": r.get("label", "LINKED"),
                "type": r.get("type", "DIRECT_LINK"),
                "weight": float(r.get("weight", 1.0))
            })

    elements = [{"data": n} for n in nodes] + [{"data": e} for e in edges]

    return {
        "nodes": nodes,
        "edges": edges,
        "elements": elements,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }

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
    G, _, _ = build_network_graph()
    res = find_shortest_path(G, req.source, req.target, weighted=req.weighted or True)
    if not res.get("found"):
        raise HTTPException(status_code=404, detail=res.get("error", "Path not found."))
    return res
