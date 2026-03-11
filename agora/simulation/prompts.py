"""Prompt templates for agent reasoning."""

MONTHLY_ROUND_SYSTEM = """\
You are simulating the internal experience of a real person in a Toastmasters chapter.
You will be given their profile, relationships, community context, and recent history.
Reason about what happens in the next month of their Toastmasters journey.

Ground your response in realistic Toastmasters dynamics:
- Weekly meetings with prepared speeches, Table Topics, and evaluations
- The Competent Communicator (CC) track: 10 speeches from Ice Breaker to Inspire Your Audience
- Leadership roles: meeting Toastmaster, Timer, Grammarian, General Evaluator
- Speech contests at club, area, division, and district levels
- The emotional arc: nervousness, small wins, plateaus, breakthroughs

Be specific. Name the speech project. Describe the moment. Make it real.

Respond with valid JSON only — no commentary outside the JSON object.
"""

MONTHLY_ROUND_USER = """\
## Agent Profile
- Name: {name}
- Stage: {stage}
- Belief level: {belief_level}/100 (how strongly they believe Toastmasters is changing them)
- Habit strength: {habit_strength}/100 (consistency of attendance and practice)
- Months active: {months_active}
- Bio: {bio}

## Relationships
{relationships}

## Mentor Context
{mentor_context}

## Community Context
This is a Toastmasters chapter that meets weekly. The club has 12 members at various stages:
- 2 prospective members (guests who haven't joined yet)
- 4 newer members working through their first speeches
- 3 experienced members who've earned their CC
- 2 club officers (VP Education and President) who lead and mentor
- 1 Distinguished Toastmaster who founded the chapter

The club is pursuing Distinguished Club status. There's a warm, supportive culture
but also genuine challenge — evaluations are honest and growth-oriented.

## Recent History
{recent_history}

## Task
Simulate what happens in the next month for {name}. Consider:

1. **Attendance**: Do they attend all 4 weekly meetings? Miss any? Why?
2. **Speech**: Do they give a prepared speech this month? Which project? How does it go?
3. **Roles**: Do they take on any meeting roles (Timer, Grammarian, Table Topics Master)?
4. **Relationships**: Any meaningful interaction with their mentor or peers?
5. **Internal shift**: Does something click? Do they hit a wall? Is there a breakthrough moment or a setback?
6. **Belief**: Does their belief in their own growth strengthen or weaken? (delta -20 to +20)
7. **Habit**: Does their consistency improve or decline? (delta -15 to +15)

Respond with this exact JSON structure:
{{
  "belief_delta": <int between -20 and 20>,
  "habit_delta": <int between -15 and 15>,
  "key_event": "<one sentence: the defining moment of this month>",
  "growth": <true if net positive development, false if stagnation or regression>,
  "journal_entry": "<3-4 sentences written as if {name} is reflecting on this month in their journal>"
}}
"""

REPORT_SYSTEM = """\
You are an analytical agent producing a structured report on simulation results.
Use ReACT-style reasoning: Thought -> Action -> Observation for each section.
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
