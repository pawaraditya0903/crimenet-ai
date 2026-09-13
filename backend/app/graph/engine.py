import networkx as nx
import logging
from typing import Tuple, Dict, Any, List
from backend.app.models.database import get_db

logger = logging.getLogger("crimenet.graph.engine")

def build_network_graph() -> Tuple[nx.DiGraph, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Loads entities and relationships from SQLite and builds a NetworkX DiGraph.
    Applies edge confidence weighting and prevents division by zero.
    """
    G = nx.DiGraph()
    entities: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, tier, category, risk_score, city, phone, dossier FROM graph_entities")
        for row in cursor.fetchall():
            entity_dict = dict(row)
            entities.append(entity_dict)
            G.add_node(
                entity_dict["name"],
                id=entity_dict["id"],
                type=entity_dict["type"],
                risk_score=entity_dict.get("risk_score", 50.0),
                city=entity_dict.get("city", "")
            )

        cursor.execute("SELECT id, source, target, label, type, confidence, weight FROM graph_relationships")
        for row in cursor.fetchall():
            rel_dict = dict(row)
            relationships.append(rel_dict)
            src = rel_dict["source"]
            tgt = rel_dict["target"]
            # Ensure both nodes exist before adding edge
            if not G.has_node(src):
                G.add_node(src, id=f"n-{src}", type="Unknown", risk_score=50.0)
            if not G.has_node(tgt):
                G.add_node(tgt, id=f"n-{tgt}", type="Unknown", risk_score=50.0)
            
            w = float(rel_dict.get("weight") or 1.0)
            G.add_edge(
                src, tgt,
                id=rel_dict["id"],
                label=rel_dict["label"],
                type=rel_dict["type"],
                weight=max(w, 0.01)
            )

    return G, entities, relationships
