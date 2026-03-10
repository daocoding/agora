# AGORA

**Agent-based Growth and Opportunity Research Architecture**

> *A simulation framework for personal development, grounded in complexity science and powered by large language models.*

---

## What is AGORA?

AGORA is an open-source LLM-native simulation platform for modeling human development trajectories. Where existing agent-based frameworks simulate markets, disease spread, or social media dynamics — AGORA simulates the arc of personal transformation: how people build habits, develop belief, grow through mentorship, overcome stagnation, and gradually become someone they were not when they started.

The word **agent** carries three meanings simultaneously — and all three are load-bearing:

- **AI agent** — LLM-powered entities that reason, decide, and act each simulation round
- **Human agency** — what the simulation models: the capacity of a person to exercise choice, form habits, and develop
- **Agent-based organization** — the distributed network structures through which development communities operate

These three meanings do not compete. They reinforce each other. The AI agents serve human agency inside agent-based organizations.

---

## The Gap This Fills

Agent-based modeling has produced powerful frameworks for social simulation:

- **OASIS** *(Camel-AI)* — Open Agent Social Interaction Simulations with One Million Agents. Designed for social media dynamics: viral spread, opinion formation, platform interactions. [GitHub](https://github.com/camel-ai/oasis)
- **MiroFish** — A swarm intelligence prediction engine built on OASIS for public opinion and narrative forecasting. [GitHub](https://github.com/666ghj/MiroFish)

Both are designed for population-scale social dynamics. Neither addresses the interior arc of personal development:

- Habit formation and breakdown
- Belief development and doubt
- Mentorship relationships and their compound effects
- The non-linear trajectory from intention to sustained transformation

AGORA fills this gap. It models **1,000 agents** — not one million. The scale is intentional. Personal development communities operate at human scale, not platform scale. Depth over breadth.

---

## Design Principles

**Monthly rounds, not milliseconds.** Each simulation round represents one month of a person's development journey. Transformation compounds slowly and non-linearly. The time unit must match the phenomenon.

**Sequential reasoning, not parallel spread.** Agent behavior in personal development is deliberate: Did they show up this week? Did they do the hard conversation? Did they run toward or away from discomfort? LLM-powered sequential reasoning captures this better than parallel social media interaction models.

**Inner game and outer game.** The simulation models both measurable activity (meetings, mentorship sessions, milestones reached) and internal state (belief level, doubt threshold, motivation patterns). Outcomes without interiority are incomplete.

**Historically grounded.** AGORA is designed to be seeded with real longitudinal data from development communities — the narrative history of real people who walked the arc. The simulation learns from what actually happened, not from synthetic assumptions.

**Research artifact and operational tool.** Each simulation run is both a prediction instrument (what trajectory is this person likely to follow?) and a research contribution (what conditions enable flourishing at scale?).

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AGORA Platform                        │
│                                                         │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │  Graph Layer │    │  Simulation  │    │   Report   │ │
│  │             │    │   Engine     │    │   Agent    │ │
│  │  - Nodes:   │───▶│             │───▶│            │ │
│  │    People   │    │  36 rounds  │    │  ReACT     │ │
│  │  - Edges:   │    │  (months)   │    │  reasoning │ │
│  │    Rels,    │    │             │    │            │ │
│  │    History  │    │  LLM agents │    │  PDF output│ │
│  └─────────────┘    └──────────────┘    └────────────┘ │
│         ▲                                               │
│         │                                               │
│  ┌─────────────┐                                        │
│  │  Seed Data  │                                        │
│  │             │                                        │
│  │  Narratives │                                        │
│  │  Milestones │                                        │
│  │  Journeys   │                                        │
│  └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

### Components

**Graph Layer** — Stores people, relationships, and historical patterns as a knowledge graph. Nodes represent individuals at different stages of development. Edges represent mentorship, recruitment, shared experiences, and influence relationships. File-based, fully owned, no external graph database required.

**Simulation Engine** — LLM-powered agents run month-by-month through a development arc. Each round, agents make decisions based on their profile, their relationships, the events of the prior round, and their accumulated history. Sequential execution enables deep reasoning per agent.

**Report Agent** — A ReACT-style reasoning agent that queries the simulation results and knowledge graph, reasons across multiple sections, and produces a structured prediction report: trajectory forecast, risk points, inflection factors, comparable historical patterns.

---

## Theoretical Foundation

AGORA is grounded in complexity science. Personal development communities are complex adaptive systems: individuals following emergent rules produce collective behavior — culture, momentum, flourishing — that no single designer intended.

Key concepts from complexity science that AGORA operationalizes:

- **Emergence** — collective flourishing arising from individual agent interactions
- **Edge of chaos** — the productive tension between enough structure and enough freedom that enables development
- **Attractors** — the stable states a system naturally moves toward (flourishing or stagnation)
- **Non-linearity** — long periods of apparent stillness followed by rapid breakthrough (the Lyubishchev pattern: categories of work that compound only when sustained over time)

---

## Inspiration and Citations

AGORA builds on and cites:

```bibtex
@misc{oasis2024,
  title={OASIS: Open Agent Social Interaction Simulations with One Million Agents},
  author={Camel-AI Team},
  year={2024},
  url={https://github.com/camel-ai/oasis}
}

@misc{mirofish2025,
  title={MiroFish: A Simple and Universal Swarm Intelligence Engine},
  author={MiroFish Team},
  year={2025},
  url={https://github.com/666ghj/MiroFish}
}
```

---

## Vision

> *Mass flourishing — not just for elites.*

The conditions that enabled the Renaissance — mentorship, community, economic opportunity, a shared philosophical framework, the freedom to develop one's full capacities — were available only to those with access to patronage. AGORA is built on the conviction that these conditions can be modeled, understood, and made widely accessible.

One thousand agents. One thousand trajectories. Every one of them a person learning to become more fully themselves.

---

## Status

🔬 **Early research stage.** Architecture defined. Implementation in progress.

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

Apache 2.0
