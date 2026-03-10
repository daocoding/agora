"""DevelopmentAgent — LLM-powered persona that reasons through monthly rounds."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from agora.graph.schema import AgentNode, Stage, RelationshipEdge, RelationType
from agora.simulation.prompts import MONTHLY_ROUND_SYSTEM, MONTHLY_ROUND_USER


@dataclass
class MonthlyOutcome:
    """Result of one month's reasoning for an agent."""

    agent_id: str
    round_number: int
    belief_delta: int = 0
    habit_delta: int = 0
    new_stage: Stage = Stage.SEED
    income_tier_delta: int = 0
    narrative: str = ""
    mentorship_given: int = 0
    mentorship_received: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "round_number": self.round_number,
            "belief_delta": self.belief_delta,
            "habit_delta": self.habit_delta,
            "new_stage": self.new_stage.value,
            "income_tier_delta": self.income_tier_delta,
            "narrative": self.narrative,
            "mentorship_given": self.mentorship_given,
            "mentorship_received": self.mentorship_received,
        }


class DevelopmentAgent:
    """Wraps an AgentNode with LLM reasoning capability."""

    def __init__(self, node: AgentNode) -> None:
        self.node = node
        self.history: list[MonthlyOutcome] = []

    def _format_relationships(self, edges: list[RelationshipEdge], nodes: dict[str, AgentNode]) -> str:
        if not edges:
            return "No current relationships."
        lines = []
        for e in edges:
            other_id = e.target_id if e.source_id == self.node.id else e.source_id
            other = nodes.get(other_id)
            other_name = other.name if other else other_id
            lines.append(f"- {e.rel_type.value} with {other_name} (strength: {e.strength}/100)")
        return "\n".join(lines)

    def _format_recent_history(self, last_n: int = 3) -> str:
        if not self.history:
            return "No prior history — this is the first month."
        recent = self.history[-last_n:]
        lines = []
        for h in recent:
            lines.append(f"- Month {h.round_number}: {h.narrative}")
        return "\n".join(lines)

    def reason_monthly_round(
        self,
        round_number: int,
        edges: list[RelationshipEdge],
        all_nodes: dict[str, AgentNode],
        llm_client: OpenAI,
        model: str = "gpt-4o-mini",
    ) -> MonthlyOutcome:
        """Run one month of reasoning via the LLM."""
        user_prompt = MONTHLY_ROUND_USER.format(
            name=self.node.name,
            stage=self.node.stage.value,
            belief_level=self.node.belief_level,
            habit_strength=self.node.habit_strength,
            months_active=self.node.months_active,
            income_tier=self.node.income_tier,
            mentorship_received=self.node.mentorship_received,
            bio=self.node.bio,
            relationships=self._format_relationships(edges, all_nodes),
            recent_history=self._format_recent_history(),
        )

        response = llm_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": MONTHLY_ROUND_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        raw = response.choices[0].message.content or "{}"
        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        data = json.loads(raw)

        outcome = MonthlyOutcome(
            agent_id=self.node.id,
            round_number=round_number,
            belief_delta=int(data.get("belief_delta", 0)),
            habit_delta=int(data.get("habit_delta", 0)),
            new_stage=Stage(data.get("new_stage", self.node.stage.value)),
            income_tier_delta=int(data.get("income_tier_delta", 0)),
            narrative=data.get("narrative", ""),
            mentorship_given=int(data.get("mentorship_given", 0)),
            mentorship_received=int(data.get("mentorship_received", 0)),
        )

        self._apply_outcome(outcome)
        self.history.append(outcome)
        return outcome

    def _apply_outcome(self, outcome: MonthlyOutcome) -> None:
        """Apply a monthly outcome to the agent's node state."""
        self.node.belief_level = max(0, min(100, self.node.belief_level + outcome.belief_delta))
        self.node.habit_strength = max(0, min(100, self.node.habit_strength + outcome.habit_delta))
        self.node.stage = outcome.new_stage
        self.node.income_tier = max(0, min(5, self.node.income_tier + outcome.income_tier_delta))
        self.node.months_active += 1
        self.node.mentorship_received += outcome.mentorship_received
