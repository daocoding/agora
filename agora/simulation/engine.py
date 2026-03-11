"""SimulationEngine — runs monthly rounds across all agents."""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import track

from agora.graph.store import GraphStore
from agora.simulation.agent import DevelopmentAgent, MonthlyOutcome


@dataclass
class SimulationResult:
    """Full result of a simulation run."""

    num_rounds: int
    agents: list[str]
    history: list[MonthlyOutcome] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "num_rounds": self.num_rounds,
            "agents": self.agents,
            "history": [h.to_dict() for h in self.history],
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> SimulationResult:
        data = json.loads(Path(path).read_text())
        result = cls(
            num_rounds=data["num_rounds"],
            agents=data["agents"],
        )
        for h in data["history"]:
            from agora.graph.schema import Stage

            result.history.append(
                MonthlyOutcome(
                    agent_id=h["agent_id"],
                    round_number=h["round_number"],
                    belief_delta=h["belief_delta"],
                    habit_delta=h["habit_delta"],
                    new_stage=Stage(h["new_stage"]),
                    income_tier_delta=h.get("income_tier_delta", 0),
                    narrative=h.get("narrative", ""),
                    key_event=h.get("key_event", ""),
                    growth=h.get("growth", False),
                    journal_entry=h.get("journal_entry", ""),
                    mentorship_given=h.get("mentorship_given", 0),
                    mentorship_received=h.get("mentorship_received", 0),
                )
            )
        return result


class SimulationEngine:
    """Runs the simulation: monthly rounds, sequential agent processing."""

    def __init__(self, graph: GraphStore, console: Console | None = None) -> None:
        self.graph = graph
        self.console = console or Console()
        self._init_llm()

    def _init_llm(self) -> None:
        self.api_type = os.environ.get("AGORA_LLM_API", "openai")

        if self.api_type == "anthropic":
            import anthropic

            self.model = os.environ.get("AGORA_LLM_MODEL", "claude-sonnet-4-20250514")
            api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
            self.llm = anthropic.Anthropic(api_key=api_key)
        else:
            from openai import OpenAI

            base_url = os.environ.get("AGORA_LLM_BASE_URL")
            api_key = os.environ.get("AGORA_LLM_API_KEY", "sk-no-key")
            self.model = os.environ.get("AGORA_LLM_MODEL", "gpt-4o-mini")

            kwargs: dict[str, Any] = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            self.llm = OpenAI(**kwargs)

    def run(self, num_rounds: int) -> SimulationResult:
        """Run the simulation for the given number of monthly rounds."""
        agents = {
            node.id: DevelopmentAgent(node) for node in self.graph.all_nodes()
        }
        result = SimulationResult(
            num_rounds=num_rounds,
            agents=list(agents.keys()),
        )

        for round_num in track(range(1, num_rounds + 1), description="Simulating...", console=self.console):
            self.console.print(f"\n[bold]— Month {round_num} —[/bold]")
            for agent_id, agent in agents.items():
                edges = self.graph.get_edges_for(agent_id)
                outcome = agent.reason_monthly_round(
                    round_number=round_num,
                    edges=edges,
                    all_nodes=self.graph.nodes,
                    llm_client=self.llm,
                    model=self.model,
                    api_type=self.api_type,
                )
                self.graph.update_node(agent.node)
                result.history.append(outcome)
                growth_icon = "+" if outcome.growth else "-"
                self.console.print(
                    f"  [{growth_icon}] [cyan]{agent.node.name}[/cyan] "
                    f"({agent.node.stage.value}) "
                    f"b:{agent.node.belief_level} h:{agent.node.habit_strength} | "
                    f"{outcome.key_event[:70]}"
                )

        return result
