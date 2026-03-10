"""Prompt templates for agent reasoning."""

MONTHLY_ROUND_SYSTEM = """\
You are simulating the internal reasoning of a person on a development journey.
You will be given their current profile, relationships, and recent history.
Reason about what happens in the next month of their journey.

Respond with valid JSON only — no commentary outside the JSON object.
"""

MONTHLY_ROUND_USER = """\
## Agent Profile
- Name: {name}
- Stage: {stage}
- Belief level: {belief_level}/100
- Habit strength: {habit_strength}/100
- Months active: {months_active}
- Income tier: {income_tier}/5
- Mentorship received: {mentorship_received} sessions
- Bio: {bio}

## Relationships
{relationships}

## Recent History
{recent_history}

## Task
Simulate what happens in the next month. Consider:
1. Does this person's belief strengthen or weaken? By how much (delta -20 to +20)?
2. Does their habit strength improve or decline? By how much (delta -15 to +15)?
3. Do they advance to a new stage, stay, or regress?
4. What key event or decision defines this month?
5. Does their income tier change?

Respond with this exact JSON structure:
{{
  "belief_delta": <int>,
  "habit_delta": <int>,
  "new_stage": "<SEED|GROWING|FLOURISHING|MENTOR|MASTER>",
  "income_tier_delta": <int -1 to 1>,
  "narrative": "<2-3 sentence description of what happened this month>",
  "mentorship_given": <int 0-5>,
  "mentorship_received": <int 0-3>
}}
"""

REPORT_SYSTEM = """\
You are an analytical agent producing a structured report on simulation results.
Use ReACT-style reasoning: Thought → Action → Observation for each section.
Be specific and data-driven. Reference agent names and metrics.
"""

REPORT_USER = """\
## Simulation Summary
- Rounds: {num_rounds}
- Agents: {num_agents}

## Final Agent States
{agent_states}

## Key Events Timeline
{timeline}

## Task
Produce a structured report with these sections:
1. Executive Summary (3-5 sentences)
2. Trajectory Analysis — for each agent, summarize their arc
3. Relationship Impact — how mentorship and peer connections affected outcomes
4. Risk Factors — agents at risk of stagnation or regression
5. Recommendations — what conditions would improve outcomes

Format as markdown.
"""
