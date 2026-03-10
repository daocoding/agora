#!/usr/bin/env python3
"""Run a 3-month simulation on the example seed data."""

from pathlib import Path

from rich.console import Console

from agora.graph.store import GraphStore
from agora.simulation.engine import SimulationEngine
from agora.report.generator import ReportGenerator

SEED_DATA = Path(__file__).parent / "seed_data.json"
RESULTS_PATH = Path(__file__).parent / "results.json"
FINAL_GRAPH_PATH = Path(__file__).parent / "seed_data_final.json"
REPORT_PATH = Path(__file__).parent / "report.md"


def main() -> None:
    console = Console()
    console.print("[bold]AGORA Example — 3-Month Simulation[/bold]\n")

    # Load seed data
    graph = GraphStore.load(SEED_DATA)
    summary = graph.summary()
    console.print(f"Loaded {summary['total_agents']} agents, {summary['total_edges']} relationships\n")

    # Run simulation
    engine = SimulationEngine(graph, console=console)
    result = engine.run(num_rounds=3)

    # Save results
    result.save(RESULTS_PATH)
    graph.save(FINAL_GRAPH_PATH)
    console.print(f"\n[green]Results saved to {RESULTS_PATH}[/green]")

    # Generate report
    console.print("\n[bold]Generating report...[/bold]")
    gen = ReportGenerator()
    report_text = gen.generate(result, graph)
    REPORT_PATH.write_text(report_text)
    console.print(f"[green]Report saved to {REPORT_PATH}[/green]")


if __name__ == "__main__":
    main()
