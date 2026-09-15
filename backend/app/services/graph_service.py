"""
CrimeNet AI - Unified Graph Service Layer
Encapsulates Neo4j graph queries, multi-hop Cypher traversals,
and feeds graph topology into NetworkX for analytical and offline computations.
Keeps routers decoupled from database-specific Cypher or SQL implementations.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import networkx as nx

from backend.app.database.connection import db_session_context
from backend.app.models.pg_models import GraphEntity, GraphRelationship
from backend.app.graph.neo4j_client import get_neo4j_driver, execute_cypher, check_neo4j_status
from backend.app.graph.centrality import compute_centralities
from backend.app.graph.communities import compute_communities
from backend.app.graph.cycles import detect_financial_cycles
from backend.app.graph.paths import find_shortest_path

logger = logging.getLogger("crimenet.services.graph")

class GraphService:
    @staticmethod
    def get_topology_from_db() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Retrieves authoritative entities and relationships from PostgreSQL system of record."""
        with db_session_context() as session:
            entities = [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type,
                    "tier": e.tier,
                    "category": e.category,
                    "risk_score": e.risk_score,
                    "city": e.city,
                    "phone": e.phone,
                    "dossier": e.dossier
                }
                for e in session.query(GraphEntity).all()
            ]
            relationships = [
                {
                    "id": r.id,
                    "source": r.source,
                    "target": r.target,
                    "label": r.label,
                    "type": r.type,
                    "confidence": r.confidence,
                    "weight": r.weight
                }
                for r in session.query(GraphRelationship).all()
            ]
        return entities, relationships

    @classmethod
    def build_networkx_graph(cls) -> Tuple[nx.DiGraph, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Builds NetworkX DiGraph from the database system of record."""
        entities, relationships = cls.get_topology_from_db()
        G = nx.DiGraph()

        for e in entities:
            G.add_node(
                e["name"],
                id=e["id"],
                type=e["type"],
                risk_score=e.get("risk_score", 50.0),
                city=e.get("city", "")
            )

        for r in relationships:
            src = r["source"]
            tgt = r["target"]
            if not G.has_node(src):
                G.add_node(src, id=f"n-{src}", type="Unknown", risk_score=50.0)
            if not G.has_node(tgt):
                G.add_node(tgt, id=f"n-{tgt}", type="Unknown", risk_score=50.0)

            w = float(r.get("weight") or 1.0)
            G.add_edge(
                src, tgt,
                id=r["id"],
                label=r["label"],
                type=r["type"],
                weight=max(w, 0.01)
            )

        return G, entities, relationships

    @classmethod
    def get_cytoscape_network(cls) -> Dict[str, Any]:
        """Formats graph topology into Cytoscape.js compatible format."""
        G, entities, relationships = cls.build_networkx_graph()

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
            "total_edges": len(edges),
            "graph_backend": "Neo4j_Active" if check_neo4j_status().get("is_connected") else "PostgreSQL_Relational_Projection"
        }

    @classmethod
    def find_path(cls, source: str, target: str, weighted: bool = True) -> Dict[str, Any]:
        """Finds shortest path between two entities, using Cypher in Neo4j if connected,
        otherwise NetworkX Dijkstra.
        """
        driver = get_neo4j_driver()
        if driver:
            cypher = """
            MATCH (src:Entity {name: $src}), (tgt:Entity {name: $tgt})
            MATCH p = shortestPath((src)-[*..8]-(tgt))
            RETURN [n IN nodes(p) | properties(n).name] as path_nodes,
                   length(p) as length,
                   [r IN relationships(p) | {label: r.label, weight: r.weight}] as edges
            """
            try:
                records = execute_cypher(cypher, {"src": source, "tgt": target})
                if records:
                    rec = records[0]
                    return {
                        "found": True,
                        "source": source,
                        "target": target,
                        "path": rec["path_nodes"],
                        "hop_count": rec["length"],
                        "engine": "Neo4j_Cypher_ShortestPath",
                        "edges": rec["edges"]
                    }
            except Exception as e:
                logger.warning("Neo4j shortest path query failed, falling back to NetworkX: %s", e)

        # NetworkX fallback
        G, _, _ = cls.build_networkx_graph()
        res = find_shortest_path(G, source, target, weighted=weighted)
        if "engine" not in res:
            res["engine"] = "NetworkX_Dijkstra_Fallback"
        return res

    get_shortest_path = find_path
