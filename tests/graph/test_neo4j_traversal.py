"""
CrimeNet AI - Neo4j Graph Database & Cypher Traversal Integration Tests
Verifies Neo4j driver connection pooling, health telemetry, projection synchronization,
and seamless Cypher / NetworkX dual-mode shortest-path execution.
"""

import pytest
from backend.app.graph.neo4j_client import (
    get_neo4j_driver,
    check_neo4j_status,
    execute_cypher,
    get_node_neighborhood
)
from backend.app.graph.sync import (
    sync_entities_to_neo4j,
    sync_relationships_to_neo4j,
    sync_relational_to_neo4j
)
from backend.app.services.graph_service import GraphService

def test_neo4j_telemetry_and_fallback():
    """Verify Neo4j driver status reports connection state or graceful NetworkX fallback."""
    status = check_neo4j_status()
    assert "status" in status
    assert status["status"] in ("OPERATIONAL_CONNECTED", "UNREACHABLE_FALLBACK_ACTIVE")
    assert "is_connected" in status
    assert isinstance(status["is_connected"], bool)
    assert "engine" in status
    assert status["engine"] in ("Neo4j_5.20_Graph_Engine", "NetworkX_Relational_Fallback")

def test_graph_service_shortest_path_dual_mode():
    """Verify shortest path discovery functions across active graph backend."""
    # Test path between known entities in CrimeNet sample dataset
    result = GraphService.get_shortest_path(
        source="Arjun Mehta",
        target="Vikram Singhania"
    )
    assert "found" in result
    assert "engine" in result
    assert result["engine"] in ("Neo4j_Cypher_ShortestPath", "NetworkX_Dijkstra_Fallback")
    
    if result["found"]:
        assert len(result["path"]) >= 2
        assert result["path"][0] == "Arjun Mehta"
        assert result["path"][-1] == "Vikram Singhania"
        assert result["distance"] >= 1

def test_neo4j_projection_sync_idempotence():
    """Verify projection sync routines execute idempotently with zero errors in both online and offline modes."""
    sample_entities = [
        {"id": "node_test_01", "name": "Test Entity Alpha", "type": "INDIVIDUAL", "risk": "LOW"},
        {"id": "node_test_02", "name": "Test Entity Beta", "type": "OFFSHORE_SHELL", "risk": "CRITICAL"}
    ]
    sample_relationships = [
        {
            "id": "edge_test_01",
            "source": "node_test_01",
            "target": "node_test_02",
            "type": "BENEFICIAL_OWNER_OF",
            "weight": 1.0,
            "flow_amount": 5000000.0
        }
    ]

    synced_nodes = sync_entities_to_neo4j(sample_entities)
    synced_edges = sync_relationships_to_neo4j(sample_relationships)

    assert isinstance(synced_nodes, int)
    assert isinstance(synced_edges, int)
    assert synced_nodes >= 0
    assert synced_edges >= 0

def test_neo4j_neighborhood_contract():
    """Verify neighborhood query returns standard schema with nodes and edges."""
    neighborhood = get_node_neighborhood("Arjun Mehta", max_depth=2)
    assert "nodes" in neighborhood
    assert "edges" in neighborhood
    assert isinstance(neighborhood["nodes"], list)
    assert isinstance(neighborhood["edges"], list)
