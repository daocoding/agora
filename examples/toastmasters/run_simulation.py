#!/usr/bin/env python3
"""Run a 6-month Toastmasters chapter simulation."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from agora.graph.store import GraphStore
from agora.graph.schema import AgentNode
from agora.simulation.engine import SimulationEngine

SEED_DATA = Path(__file__).parent / "seed_data.json"
RESULTS_DIR = Path(__file__).parent / "results"
OUTPUT_PATH = RESULTS_DIR / "simulation_output.json"

STAGE_COLORS = {
    "SEED": "dim",
    "GROWING": "green",
    "FLOURISHING": "cyan",
    "MENTOR": "magenta",
    "MASTER": "yellow",
}


def snapshot_agents(graph: GraphStore) -> list[dict]:
    """Capture current state of all agents."""
    return [
        {
            "name": n.name,
            "stage": n.stage.value,
            "belief": n.belief_level,
            "habit": n.habit_strength,
            "months": n.months_active,
        }
        for n in graph.all_nodes()
    ]


def print_progression_table(console: Console, initial: list[dict], monthly: list[list[dict]], num_rounds: int) -> None:
    """Print a Rich table showing agent progression month by month."""
    table = Table(title="Toastmasters Chapter — 6-Month Progression", show_lines=True)
    table.add_column("Agent", style="bold", min_width=18)
    table.add_column("Start", min_width=16)
    for i in range(1, num_rounds + 1):
        table.add_column(f"Month {i}", min_width=16)

    for idx, agent_init in enumerate(initial):
        name = agent_init["name"]
        row = [name]

        # Start state
        s = agent_init
        color = STAGE_COLORS.get(s["stage"], "white")
        row.append(f"[{color}]{s['stage']}[/{color}]\nb:{s['belief']} h:{s['habit']}")

        # Monthly states
        for month_idx in range(num_rounds):
            s = monthly[month_idx][idx]
            color = STAGE_COLORS.get(s["stage"], "white")
            row.append(f"[{color}]{s['stage']}[/{color}]\nb:{s['belief']} h:{s['habit']}")

        table.add_row(*row)

    console.print(table)


def print_summary(console: Console, initial: list[dict], final: list[dict]) -> None:
    """Print text summary comparing start to end."""
    console.print("\n[bold]===== SIMULATION SUMMARY =====[/bold]\n")
    for i, (start, end) in enumerate(zip(initial, final)):
        name = start["name"]
        b_delta = end["belief"] - start["belief"]
        h_delta = end["habit"] - start["habit"]
        stage_change = "" if start["stage"] == end["stage"] else f" -> {end['stage']}"

        b_sign = "+" if b_delta >= 0 else ""
        h_sign = "+" if h_delta >= 0 else ""

        console.print(
            f"  {name}: {start['stage']}{stage_change} | "
            f"belief {start['belief']}->{end['belief']} ({b_sign}{b_delta}) | "
            f"habit {start['habit']}->{end['habit']} ({h_sign}{h_delta})"
        )

    # Overall stats
    total_belief_start = sum(a["belief"] for a in initial)
    total_belief_end = sum(a["belief"] for a in final)
    total_habit_start = sum(a["habit"] for a in initial)
    total_habit_end = sum(a["habit"] for a in final)

    console.print(f"\n  [bold]Club totals:[/bold]")
    console.print(f"    Belief: {total_belief_start} -> {total_belief_end} ({total_belief_end - total_belief_start:+d})")
    console.print(f"    Habit:  {total_habit_start} -> {total_habit_end} ({total_habit_end - total_habit_start:+d})")

    growers = sum(1 for s, e in zip(initial, final) if e["belief"] > s["belief"])
    console.print(f"    Members who grew in belief: {growers}/{len(initial)}")


def main() -> None:
    console = Console(record=True)
    num_rounds = 6

    console.print("[bold]AGORA — Toastmasters Chapter Simulation (6 months)[/bold]\n")

    # Load seed data
    graph = GraphStore.load(SEED_DATA)
    summary = graph.summary()
    console.print(f"Loaded {summary['total_agents']} agents, {summary['total_edges']} relationships")
    console.print(f"Stages: {summary['stages']}\n")

    # Capture initial state
    initial_snapshot = snapshot_agents(graph)
    monthly_snapshots: list[list[dict]] = []

    # Run simulation
    engine = SimulationEngine(graph, console=console)
    result = engine.run(num_rounds=num_rounds)

    # Build monthly snapshots from history
    # We need to reconstruct snapshots from outcomes
    # Re-load and replay to get per-round snapshots
    graph2 = GraphStore.load(SEED_DATA)
    agents_order = [n.name for n in graph2.all_nodes()]
    agent_ids = [n.id for n in graph2.all_nodes()]

    for round_num in range(1, num_rounds + 1):
        round_outcomes = [h for h in result.history if h.round_number == round_num]
        for outcome in round_outcomes:
            node = graph2.get_node(outcome.agent_id)
            if node:
                node.belief_level = max(0, min(100, node.belief_level + outcome.belief_delta))
                node.habit_strength = max(0, min(100, node.habit_strength + outcome.habit_delta))
                node.stage = outcome.new_stage
                node.months_active += 1
        monthly_snapshots.append(snapshot_agents(graph2))

    # Print progression table
    console.print()
    print_progression_table(console, initial_snapshot, monthly_snapshots, num_rounds)

    # Print journal entries for last round
    console.print("\n[bold]===== MONTH 6 JOURNAL ENTRIES =====[/bold]\n")
    last_round = [h for h in result.history if h.round_number == num_rounds]
    for outcome in last_round:
        node = graph.get_node(outcome.agent_id)
        name = node.name if node else outcome.agent_id
        console.print(f"  [cyan]{name}[/cyan]: {outcome.journal_entry}\n")

    # Print summary
    final_snapshot = monthly_snapshots[-1] if monthly_snapshots else snapshot_agents(graph)
    print_summary(console, initial_snapshot, final_snapshot)

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_data = {
        "num_rounds": num_rounds,
        "initial_state": initial_snapshot,
        "monthly_snapshots": monthly_snapshots,
        "history": result.to_dict()["history"],
        "final_state": final_snapshot,
    }
    OUTPUT_PATH.write_text(json.dumps(output_data, indent=2))
    console.print(f"\n[green]Results saved to {OUTPUT_PATH}[/green]")

    # Save terminal output
    text_output = console.export_text()
    sample_output_path = RESULTS_DIR / "sample_output.txt"
    sample_output_path.write_text(text_output)
    console.print(f"[green]Terminal output saved to {sample_output_path}[/green]")


if __name__ == "__main__":
    main()
