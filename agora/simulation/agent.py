"""DevelopmentAgent — LLM-powered persona that reasons through monthly rounds."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

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
    key_event: str = ""
    growth: bool = False
    journal_entry: str = ""
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
            "key_event": self.key_event,
            "growth": self.growth,
            "journal_entry": self.journal_entry,
            "mentorship_given": self.mentorship_given,
            "mentorship_received": self.mentorship_received,
        }


def _parse_llm_json(raw: str) -> dict[str, Any]:
    """Parse JSON from LLM response, stripping markdown fences if present."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
    return json.loads(raw)


def _call_openai(client: Any, model: str, system: str, user: str) -> str:
    """Call OpenAI-compatible API."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content or "{}"


def _call_anthropic(client: Any, model: str, system: str, user: str) -> str:
    """Call Anthropic API."""
    response = client.messages.create(
        model=model,
        max_tokens=500,
        system=system,
        messages=[
            {"role": "user", "content": user},
        ],
        temperature=0.7,
    )
    return response.content[0].text


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

    def _format_mentor_context(self, edges: list[RelationshipEdge], nodes: dict[str, AgentNode]) -> str:
        """Build mentor context string showing mentor details."""
        mentor_lines = []
        for e in edges:
            if e.rel_type != RelationType.MENTORS:
                continue
            if e.target_id == self.node.id:
                mentor = nodes.get(e.source_id)
                if mentor:
                    mentor_lines.append(
                        f"Mentor: {mentor.name} ({mentor.stage.value}, belief: {mentor.belief_level}/100, "
                        f"{mentor.months_active} months active)"
                    )
            elif e.source_id == self.node.id:
                mentee = nodes.get(e.target_id)
                if mentee:
                    mentor_lines.append(
                        f"Mentee: {mentee.name} ({mentee.stage.value}, belief: {mentee.belief_level}/100)"
                    )
        return "\n".join(mentor_lines) if mentor_lines else "No formal mentorship relationship."

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
        llm_client: Any,
        model: str = "gpt-4o-mini",
        api_type: str = "openai",
    ) -> MonthlyOutcome:
        """Run one month of reasoning via the LLM."""
        user_prompt = MONTHLY_ROUND_USER.format(
            name=self.node.name,
            stage=self.node.stage.value,
            belief_level=self.node.belief_level,
            habit_strength=self.node.habit_strength,
            months_active=self.node.months_active,
            bio=self.node.bio,
            relationships=self._format_relationships(edges, all_nodes),
            mentor_context=self._format_mentor_context(edges, all_nodes),
            recent_history=self._format_recent_history(),
        )

        if api_type == "anthropic":
            raw = _call_anthropic(llm_client, model, MONTHLY_ROUND_SYSTEM, user_prompt)
        else:
            raw = _call_openai(llm_client, model, MONTHLY_ROUND_SYSTEM, user_prompt)

        data = _parse_llm_json(raw)

        # Build narrative from new fields, falling back to old format
        key_event = data.get("key_event", "")
        journal_entry = data.get("journal_entry", "")
        narrative = data.get("narrative", key_event or journal_entry)

        outcome = MonthlyOutcome(
            agent_id=self.node.id,
            round_number=round_number,
            belief_delta=int(data.get("belief_delta", 0)),
            habit_delta=int(data.get("habit_delta", 0)),
            new_stage=Stage(data.get("new_stage", self.node.stage.value)),
            income_tier_delta=int(data.get("income_tier_delta", 0)),
            narrative=narrative,
            key_event=key_event,
            growth=bool(data.get("growth", False)),
            journal_entry=journal_entry,
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
