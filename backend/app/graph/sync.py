"""
CrimeNet AI - PostgreSQL to Neo4j Synchronization Engine
Maintains PostgreSQL as the single source of truth while projecting
relationships and topological entities into Neo4j for high-speed graph traversal.
"""

import logging
from typing import Dict, Any, List, Optional
from backend.app.graph.neo4j_client import get_neo4j_driver, execute_cypher
from backend.app.database.connection import db_session_context
from backend.app.models.pg_models import GraphEntity, GraphRelationship

logger = logging.getLogger("crimenet.graph.sync")

def sync_entities_to_neo4j(entities: List[Dict[str, Any]]) -> int:
    """Idempotently projects entities into Neo4j using UNWIND and MERGE."""
    driver = get_neo4j_driver()
    if not driver or not entities:
        return 0

    batch = [
        {
            "id": str(e.get("id", "")),
            "name": str(e.get("name", "")).strip(),
            "type": str(e.get("type", "Person")),
            "tier": str(e.get("tier", "general")),
            "category": str(e.get("category", "general")),
            "risk_score": float(e.get("risk_score") or 50.0),
            "city": str(e.get("city", "") or ""),
            "phone": str(e.get("phone", "") or ""),
            "dossier": str(e.get("dossier", "") or "")
        }
        for e in entities if e.get("name")
    ]

    cypher = """
    UNWIND $batch AS item
    MERGE (e:Entity {name: item.name})
    ON CREATE SET
        e.id = item.id,
        e.type = item.type,
        e.tier = item.tier,
        e.category = item.category,
        e.risk_score = item.risk_score,
        e.city = item.city,
        e.phone = item.phone,
        e.dossier = item.dossier,
        e.created_at = timestamp()
    ON MATCH SET
        e.risk_score = item.risk_score,
        e.tier = item.tier,
        e.category = item.category,
        e.phone = CASE WHEN item.phone <> '' THEN item.phone ELSE e.phone END,
        e.dossier = CASE WHEN item.dossier <> '' THEN item.dossier ELSE e.dossier END,
        e.updated_at = timestamp()
    """
    try:
        with driver.session() as session:
            session.run(cypher, {"batch": batch})
        logger.info("Synchronized %d entities into Neo4j.", len(batch))
        return len(batch)
    except Exception as e:
        logger.error("Failed to sync entities to Neo4j: %s", e)
        return 0

def sync_relationships_to_neo4j(relationships: List[Dict[str, Any]]) -> int:
    """Idempotently projects relationships into Neo4j between verified source and target nodes."""
    driver = get_neo4j_driver()
    if not driver or not relationships:
        return 0

    batch = [
        {
            "id": str(r.get("id", "")),
            "source": str(r.get("source", "")).strip(),
            "target": str(r.get("target", "")).strip(),
            "label": str(r.get("label", "LINKED")).strip(),
            "type": str(r.get("type", "DIRECT_LINK")).strip(),
            "confidence": float(r.get("confidence") or 1.0),
            "weight": float(r.get("weight") or 1.0)
        }
        for r in relationships if r.get("source") and r.get("target")
    ]

    # Cypher query creating dynamic relationship types safely
    cypher = """
    UNWIND $batch AS rel
    MATCH (src:Entity {name: rel.source})
    MATCH (tgt:Entity {name: rel.target})
    MERGE (src)-[r:LINKED_TO {id: rel.id}]->(tgt)
    SET r.label = rel.label,
        r.type = rel.type,
        r.confidence = rel.confidence,
        r.weight = rel.weight,
        r.updated_at = timestamp()
    """
    try:
        with driver.session() as session:
            session.run(cypher, {"batch": batch})
        logger.info("Synchronized %d relationships into Neo4j.", len(batch))
        return len(batch)
    except Exception as e:
        logger.error("Failed to sync relationships to Neo4j: %s", e)
        return 0

def sync_all_from_postgres() -> Dict[str, Any]:
    """Reads all graph entities and relationships from PostgreSQL and projects them to Neo4j."""
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

    synced_entities = sync_entities_to_neo4j(entities)
    synced_rels = sync_relationships_to_neo4j(relationships)

    return {
        "status": "SYNC_COMPLETE",
        "entities_in_postgres": len(entities),
        "entities_synced_to_neo4j": synced_entities,
        "relationships_in_postgres": len(relationships),
        "relationships_synced_to_neo4j": synced_rels
    }

sync_relational_to_neo4j = sync_all_from_postgres
