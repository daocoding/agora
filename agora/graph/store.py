"""File-based graph storage — JSON, no external database."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agora.graph.schema import AgentNode, RelationshipEdge, RelationType


class GraphStore:
    """In-memory graph with JSON file persistence."""

    def __init__(self) -> None:
        self.nodes: dict[str, AgentNode] = {}
        self.edges: list[RelationshipEdge] = []

    # --- Node operations ---

    def add_node(self, node: AgentNode) -> None:
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> AgentNode | None:
        return self.nodes.get(node_id)

    def update_node(self, node: AgentNode) -> None:
        self.nodes[node.id] = node

    def all_nodes(self) -> list[AgentNode]:
        return list(self.nodes.values())

    # --- Edge operations ---

    def add_edge(self, edge: RelationshipEdge) -> None:
        self.edges.append(edge)

    def get_edges_for(self, node_id: str) -> list[RelationshipEdge]:
        return [e for e in self.edges if e.source_id == node_id or e.target_id == node_id]

    # --- Traversal helpers ---

    def get_mentors(self, node_id: str) -> list[AgentNode]:
        """Get agents who mentor this node (source MENTORS target=node_id)."""
        mentor_ids = [
            e.source_id
            for e in self.edges
            if e.target_id == node_id and e.rel_type == RelationType.MENTORS
        ]
        return [self.nodes[mid] for mid in mentor_ids if mid in self.nodes]

    def get_mentees(self, node_id: str) -> list[AgentNode]:
        """Get agents this node mentors (source=node_id MENTORS target)."""
        mentee_ids = [
            e.target_id
            for e in self.edges
            if e.source_id == node_id and e.rel_type == RelationType.MENTORS
        ]
        return [self.nodes[mid] for mid in mentee_ids if mid in self.nodes]

    def get_peers(self, node_id: str) -> list[AgentNode]:
        """Get agents connected via PEERS relationship."""
        peer_ids = set()
        for e in self.edges:
            if e.rel_type != RelationType.PEERS:
                continue
            if e.source_id == node_id:
                peer_ids.add(e.target_id)
            elif e.target_id == node_id:
                peer_ids.add(e.source_id)
        return [self.nodes[pid] for pid in peer_ids if pid in self.nodes]

    # --- Persistence ---

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> GraphStore:
        path = Path(path)
        data = json.loads(path.read_text())
        store = cls()
        for nd in data["nodes"]:
            store.add_node(AgentNode.from_dict(nd))
        for ed in data["edges"]:
            store.add_edge(RelationshipEdge.from_dict(ed))
        return store

    def summary(self) -> dict[str, Any]:
        from collections import Counter

        stage_counts = Counter(n.stage.value for n in self.nodes.values())
        rel_counts = Counter(e.rel_type.value for e in self.edges)
        return {
            "total_agents": len(self.nodes),
            "total_edges": len(self.edges),
            "stages": dict(stage_counts),
            "relationship_types": dict(rel_counts),
        }
