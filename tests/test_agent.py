"""Tests for DevelopmentAgent."""

from agora.graph.schema import AgentNode, Stage, RelationshipEdge, RelationType
from agora.simulation.agent import DevelopmentAgent, MonthlyOutcome


class TestDevelopmentAgent:
    def test_create_agent(self):
        node = AgentNode(name="Test", id="t1")
        agent = DevelopmentAgent(node)
        assert agent.node.name == "Test"
        assert agent.history == []

    def test_apply_outcome(self):
        node = AgentNode(name="Test", id="t1", belief_level=50, habit_strength=50, income_tier=2)
        agent = DevelopmentAgent(node)
        outcome = MonthlyOutcome(
            agent_id="t1",
            round_number=1,
            belief_delta=10,
            habit_delta=-5,
            new_stage=Stage.GROWING,
            income_tier_delta=1,
            narrative="Made progress.",
            mentorship_received=2,
        )
        agent._apply_outcome(outcome)
        assert agent.node.belief_level == 60
        assert agent.node.habit_strength == 45
        assert agent.node.stage == Stage.GROWING
        assert agent.node.income_tier == 3
        assert agent.node.months_active == 1
        assert agent.node.mentorship_received == 2

    def test_apply_outcome_clamps(self):
        node = AgentNode(name="Test", id="t1", belief_level=5, habit_strength=95, income_tier=5)
        agent = DevelopmentAgent(node)
        outcome = MonthlyOutcome(
            agent_id="t1",
            round_number=1,
            belief_delta=-20,
            habit_delta=15,
            new_stage=Stage.SEED,
            income_tier_delta=1,
        )
        agent._apply_outcome(outcome)
        assert agent.node.belief_level == 0
        assert agent.node.habit_strength == 100
        assert agent.node.income_tier == 5

    def test_format_relationships(self):
        node = AgentNode(name="Mentee", id="m2")
        agent = DevelopmentAgent(node)
        edges = [RelationshipEdge(source_id="m1", target_id="m2", rel_type=RelationType.MENTORS, strength=80)]
        nodes = {"m1": AgentNode(name="Mentor", id="m1"), "m2": node}
        text = agent._format_relationships(edges, nodes)
        assert "MENTORS" in text
        assert "Mentor" in text

    def test_format_empty_relationships(self):
        node = AgentNode(name="Solo", id="s1")
        agent = DevelopmentAgent(node)
        text = agent._format_relationships([], {})
        assert "No current relationships" in text

    def test_monthly_outcome_to_dict(self):
        outcome = MonthlyOutcome(
            agent_id="t1",
            round_number=1,
            belief_delta=5,
            habit_delta=3,
            new_stage=Stage.GROWING,
            narrative="Good month.",
        )
        d = outcome.to_dict()
        assert d["new_stage"] == "GROWING"
        assert d["narrative"] == "Good month."
