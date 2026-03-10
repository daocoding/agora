"""CLI entry point for AGORA."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from agora.graph.store import GraphStore
from agora.simulation.engine import SimulationEngine, SimulationResult
from agora.report.generator import ReportGenerator

console = Console()


@click.group()
@click.version_option(package_name="agora-sim")
def cli() -> None:
    """AGORA — Agent-based Growth and Opportunity Research Architecture."""


@cli.command()
@click.option("--agents", required=True, type=click.Path(exists=True), help="Path to seed data JSON.")
@click.option("--rounds", default=3, type=int, help="Number of monthly rounds to simulate.")
@click.option("--output", default="results.json", type=click.Path(), help="Output path for results.")
def simulate(agents: str, rounds: int, output: str) -> None:
    """Run a development simulation."""
    console.print(f"[bold]Loading agents from[/bold] {agents}")
    graph = GraphStore.load(agents)
    summary = graph.summary()
    console.print(f"  {summary['total_agents']} agents, {summary['total_edges']} relationships")

    engine = SimulationEngine(graph, console=console)
    result = engine.run(num_rounds=rounds)

    result.save(output)
    graph.save(agents.replace(".json", "_final.json"))
    console.print(f"\n[green]Results saved to {output}[/green]")


@cli.command()
@click.option("--results", required=True, type=click.Path(exists=True), help="Path to simulation results JSON.")
@click.option("--agents", required=True, type=click.Path(exists=True), help="Path to final graph JSON.")
@click.option("--output", default="report.md", type=click.Path(), help="Output path for report.")
def report(results: str, agents: str, output: str) -> None:
    """Generate a report from simulation results."""
    console.print("[bold]Generating report...[/bold]")
    sim_result = SimulationResult.load(results)
    graph = GraphStore.load(agents)

    gen = ReportGenerator()
    report_text = gen.generate(sim_result, graph)

    Path(output).write_text(report_text)
    console.print(f"[green]Report saved to {output}[/green]")


@cli.group()
def graph() -> None:
    """Graph inspection commands."""


@graph.command(name="show")
@click.option("--agents", required=True, type=click.Path(exists=True), help="Path to graph JSON.")
def graph_show(agents: str) -> None:
    """Show a summary of the agent graph."""
    store = GraphStore.load(agents)

    table = Table(title="Agent Graph")
    table.add_column("Name", style="cyan")
    table.add_column("Stage", style="magenta")
    table.add_column("Belief", justify="right")
    table.add_column("Habit", justify="right")
    table.add_column("Months", justify="right")
    table.add_column("Income Tier", justify="right")

    for node in store.all_nodes():
        table.add_row(
            node.name,
            node.stage.value,
            str(node.belief_level),
            str(node.habit_strength),
            str(node.months_active),
            str(node.income_tier),
        )

    console.print(table)

    summary = store.summary()
    console.print(f"\nRelationships: {summary['total_edges']}")
    for rel_type, count in summary.get("relationship_types", {}).items():
        console.print(f"  {rel_type}: {count}")
