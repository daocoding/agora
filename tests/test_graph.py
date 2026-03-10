"""Tests for graph schema and store."""

import json
import tempfile
from pathlib import Path

from agora.graph.schema import AgentNode, RelationshipEdge, Stage, RelationType
from agora.graph.store import GraphStore


class TestAgentNode:
    def test_create_default(self):
        node = AgentNode(name="Test")
        assert node.name == "Test"
        assert node.stage == Stage.SEED
        assert node.belief_level == 50
        assert node.habit_strength == 50
        assert len(node.id) == 12

    def test_roundtrip_dict(self):
        node = AgentNode(
            name="Alice",
            stage=Stage.FLOURISHING,
            belief_level=80,
            habit_strength=70,
            months_active=12,
            income_tier=3,
            id="abc123",
        )
        d = node.to_dict()
        assert d["stage"] == "FLOURISHING"
        restored = AgentNode.from_dict(d)
        assert restored.name == "Alice"
        assert restored.stage == Stage.FLOURISHING
        assert restored.id == "abc123"


class TestRelationshipEdge:
    def test_create(self):
        edge = RelationshipEdge(source_id="a", target_id="b", rel_type=RelationType.MENTORS)
        assert edge.rel_type == RelationType.MENTORS

    def test_roundtrip_dict(self):
        edge = RelationshipEdge(source_id="a", target_id="b", rel_type=RelationType.INSPIRED_BY, strength=90)
        d = edge.to_dict()
        assert d["rel_type"] == "INSPIRED_BY"
        restored = RelationshipEdge.from_dict(d)
        assert restored.strength == 90


class TestGraphStore:
    def _make_store(self) -> GraphStore:
        store = GraphStore()
        mentor = AgentNode(name="Mentor", id="m1", stage=Stage.MENTOR)
        mentee = AgentNode(name="Mentee", id="m2", stage=Stage.GROWING)
        peer = AgentNode(name="Peer", id="p1", stage=Stage.GROWING)
        store.add_node(mentor)
        store.add_node(mentee)
        store.add_node(peer)
        store.add_edge(RelationshipEdge(source_id="m1", target_id="m2", rel_type=RelationType.MENTORS))
        store.add_edge(RelationshipEdge(source_id="m2", target_id="p1", rel_type=RelationType.PEERS))
        return store

    def test_add_and_get(self):
        store = self._make_store()
        assert store.get_node("m1") is not None
        assert store.get_node("nonexistent") is None

    def test_get_mentors(self):
        store = self._make_store()
        mentors = store.get_mentors("m2")
        assert len(mentors) == 1
        assert mentors[0].id == "m1"

    def test_get_mentees(self):
        store = self._make_store()
        mentees = store.get_mentees("m1")
        assert len(mentees) == 1
        assert mentees[0].id == "m2"

    def test_get_peers(self):
        store = self._make_store()
        peers = store.get_peers("m2")
        assert len(peers) == 1
        assert peers[0].id == "p1"

    def test_save_and_load(self):
        store = self._make_store()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "graph.json"
            store.save(path)
            loaded = GraphStore.load(path)
            assert len(loaded.all_nodes()) == 3
            assert len(loaded.edges) == 2

    def test_summary(self):
        store = self._make_store()
        s = store.summary()
        assert s["total_agents"] == 3
        assert s["total_edges"] == 2
        assert "MENTORS" in s["relationship_types"]

    def test_load_seed_data(self):
        """Verify the example seed data loads correctly."""
        seed = Path(__file__).parent.parent / "examples" / "seed_data.json"
        store = GraphStore.load(seed)
        assert len(store.all_nodes()) == 5
        assert len(store.edges) == 6
        casey = store.get_node("casey005")
        assert casey is not None
        assert casey.stage == Stage.MASTER
