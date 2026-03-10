"""ReACT-style report generation from simulation results."""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from agora.graph.store import GraphStore
from agora.simulation.engine import SimulationResult
from agora.simulation.prompts import REPORT_SYSTEM, REPORT_USER


class ReportGenerator:
    """Generates markdown reports from simulation results using LLM reasoning."""

    def __init__(self) -> None:
        base_url = os.environ.get("AGORA_LLM_BASE_URL")
        api_key = os.environ.get("AGORA_LLM_API_KEY", "sk-no-key")
        self.model = os.environ.get("AGORA_LLM_MODEL", "gpt-4o-mini")

        kwargs: dict[str, Any] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.llm = OpenAI(**kwargs)

    def _format_agent_states(self, graph: GraphStore) -> str:
        lines = []
        for node in graph.all_nodes():
            lines.append(
                f"- {node.name}: stage={node.stage.value}, belief={node.belief_level}, "
                f"habit={node.habit_strength}, income_tier={node.income_tier}, "
                f"months={node.months_active}"
            )
        return "\n".join(lines)

    def _format_timeline(self, result: SimulationResult) -> str:
        lines = []
        for h in result.history:
            lines.append(f"- Round {h.round_number} | {h.agent_id}: {h.narrative}")
        return "\n".join(lines) if lines else "No events recorded."

    def generate(self, result: SimulationResult, graph: GraphStore) -> str:
        """Generate a markdown report from simulation results."""
        user_prompt = REPORT_USER.format(
            num_rounds=result.num_rounds,
            num_agents=len(result.agents),
            agent_states=self._format_agent_states(graph),
            timeline=self._format_timeline(result),
        )

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": REPORT_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=2000,
        )

        return response.choices[0].message.content or "Report generation failed."
