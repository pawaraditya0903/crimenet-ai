"""
CrimeNet AI - Dedicated Neo4j Graph Database Client
Handles connection pooling, Cypher query execution with parameterized inputs,
schema constraints, neighborhood traversals, and shortest-path queries.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from neo4j import GraphDatabase, Driver, Session
from backend.app.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

logger = logging.getLogger("crimenet.graph.neo4j")

_driver: Optional[Driver] = None
_is_connected: bool = False

def get_neo4j_driver() -> Optional[Driver]:
    """Returns singleton Neo4j Bolt driver or None if connection fails."""
    global _driver, _is_connected
    if _driver is None:
        try:
            _driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=3.0
            )
            # Connectivity check
            _driver.verify_connectivity()
            _is_connected = True
            logger.info("Connected to Neo4j Graph DB at %s", NEO4J_URI)
            init_neo4j_constraints(_driver)
        except Exception as e:
            _is_connected = False
            logger.warning("Neo4j instance unreachable at %s (%s). Using relational/NetworkX projection fallback.", NEO4J_URI, e)
            _driver = None
    return _driver

def init_neo4j_constraints(driver: Driver):
    """Initializes uniqueness constraints and indexes on graph labels."""
    constraints = [
        "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
        "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
        "CREATE INDEX entity_type_idx IF NOT EXISTS FOR (e:Entity) ON (e.type)"
    ]
    try:
        with driver.session() as session:
            for c in constraints:
                session.run(c)
        logger.info("Neo4j constraints and indexes verified.")
    except Exception as e:
        logger.warning("Could not create Neo4j constraints: %s", e)

def check_neo4j_status() -> Dict[str, Any]:
    """Returns connection telemetry, node counts, and relationship counts.

    SEC-018 FIX: Explicitly surfaces degraded mode when NetworkX fallback is active.
    """
    driver = get_neo4j_driver()
    # SEC-018: Public flag indicating whether Neo4j is actually connected or running in degraded mode
    NEO4J_DEGRADED_MODE = not _is_connected
    if not driver:
        return {
            "status": "UNREACHABLE_FALLBACK_ACTIVE",
            # SEC-027: Do not expose internal URI / credentials in health check
            "is_connected": False,
            "degraded_mode": True,
            "engine": "NetworkX_Relational_Fallback",
            "warning": (
                "Neo4j is unavailable. Graph analytics are served from the NetworkX/PostgreSQL projection. "
                "Results may be less real-time than the dedicated graph engine."
            ),
            "node_count": 0,
            "relationship_count": 0
        }

    try:
        with driver.session() as session:
            nodes = session.run("MATCH (n:Entity) RETURN count(n) as count").single()["count"]
            rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            return {
                "status": "OPERATIONAL_CONNECTED",
                "uri": NEO4J_URI,
                "is_connected": True,
                "engine": "Neo4j_5.20_Graph_Engine",
                "node_count": nodes,
                "relationship_count": rels
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "is_connected": False
        }

def execute_cypher(query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Executes parameterized Cypher query and returns record dictionaries."""
    driver = get_neo4j_driver()
    if not driver:
        return []
    params = parameters or {}
    with driver.session() as session:
        result = session.run(query, params)
        return [record.data() for record in result]

def get_node_neighborhood(node_id_or_name: str, max_depth: int = 2) -> Dict[str, Any]:
    """Traverses graph outwards from target node up to max_depth hops using Cypher."""
    driver = get_neo4j_driver()
    if not driver:
        return {"nodes": [], "edges": []}

    cypher = """
    MATCH (start:Entity)
    WHERE start.id = $target OR start.name = $target
    CALL apoc.path.subgraphAll(start, {maxLevel: $max_depth})
    YIELD nodes, relationships
    RETURN [n IN nodes | properties(n)] AS nodes,
           [r IN relationships | {
               id: elementId(r),
               source: properties(startNode(r)).name,
               target: properties(endNode(r)).name,
               label: type(r),
               weight: r.weight,
               confidence: r.confidence
           }] AS edges
    """
    # Standard fallback if APOC not enabled
    cypher_standard = """
    MATCH path = (start:Entity)-[r*1..2]-(m:Entity)
    WHERE start.id = $target OR start.name = $target
    WITH nodes(path) AS ns, relationships(path) AS rs
    UNWIND ns AS n
    UNWIND rs AS rel
    RETURN collect(DISTINCT properties(n)) AS nodes,
           collect(DISTINCT {
               id: elementId(rel),
               source: properties(startNode(rel)).name,
               target: properties(endNode(rel)).name,
               label: type(rel),
               weight: coalesce(rel.weight, 1.0),
               confidence: coalesce(rel.confidence, 1.0)
           }) AS edges
    """
    try:
        res = execute_cypher(cypher_standard, {"target": node_id_or_name})
        if res:
            return res[0]
        return {"nodes": [], "edges": []}
    except Exception as e:
        logger.error("Error fetching neighborhood from Neo4j: %s", e)
        return {"nodes": [], "edges": []}
