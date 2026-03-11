"""Node and edge type definitions for the AGORA graph.

Theoretical foundation: Pine & Gilmore's Transformation Economy framework.
AGORA is the first computational realization of the Transformations tier in
the Progression of Economic Value: Commodities → Goods → Services →
Experiences → Transformations.

Reference: Pine, B.J. (2024). The Transformation Economy: Guiding Customers
to Achieve Their Aspirations.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional
import uuid


# ─────────────────────────────────────────────────────────────────────────────
# Stage Progression (maps to Pine's Delta Model)
# ─────────────────────────────────────────────────────────────────────────────

class Stage(str, Enum):
    """Development stages an agent progresses through.

    Maps to Pine's Delta Model of transformation depth:
        SEED        → Memorable experience (no identity shift yet — prospect)
        GROWING     → Meaningful experience ("I am trying something new")
        FLOURISHING → Transporting experience ("I see who I could become")
        MENTOR      → Full transformation ("I was X, now I am Y" — sustained)
        MASTER      → Metamorphic transformation ("I can't recognize who I was")
    """
    SEED = "SEED"
    GROWING = "GROWING"
    FLOURISHING = "FLOURISHING"
    MENTOR = "MENTOR"
    MASTER = "MASTER"


# ─────────────────────────────────────────────────────────────────────────────
# Transformation Economy Enums (Pine & Gilmore)
# ─────────────────────────────────────────────────────────────────────────────

class AspirationTypes(str, Enum):
    """The four aspiration types from Pine's Transformation Economy (Ch. 3).

    Each type requires a different guide role and community design approach.

    REFINEMENT   — small degree change; guide role: Expert
                   (enhancing existing capabilities, incremental improvement)
    AMBITION     — large degree change; guide role: Coach
                   (dramatic capability expansion, sustained effort required)
    CULTIVATION  — small kind change; guide role: Counselor
                   (identity enrichment, new dimension of self emerging)
    METAMORPHOSIS — large kind change; guide role: Alchemist
                   (core identity transformation, the person is fundamentally different)
    """
    REFINEMENT = "refinement"
    AMBITION = "ambition"
    CULTIVATION = "cultivation"
    METAMORPHOSIS = "metamorphosis"


class TransformationSphere(str, Enum):
    """The four spheres of human flourishing (Pine Ch. 2).

    Every personal transformation belongs to one or more spheres.

    HEALTH_WELLBEING    — physical, mental, emotional flourishing
    WEALTH_PROSPERITY   — financial freedom, economic independence
    KNOWLEDGE_WISDOM    — skill, capability, expertise, mastery
    PURPOSE_MEANING     — mission, identity alignment, Ikigai
    """
    HEALTH_WELLBEING = "health_wellbeing"
    WEALTH_PROSPERITY = "wealth_prosperity"
    KNOWLEDGE_WISDOM = "knowledge_wisdom"
    PURPOSE_MEANING = "purpose_meaning"


class CatalystType(str, Enum):
    """How the agent's aspiration was formed (Pine Ch. 3).

    DIRECTED    — intentional decision to pursue transformation
                  (joined the community on purpose, clear goal from the start)
    DISRUPTION  — external shock that forced change
                  (job loss, health crisis, financial event, life disruption)
    DEVIATION   — conversation, book, chance encounter that shifted worldview
                  (a single exchange changed the trajectory)
    DISCOVERY   — witnessed someone else's transformation
                  (the "convention effect" — one story changed everything)
    """
    DIRECTED = "directed"
    DISRUPTION = "disruption"
    DEVIATION = "deviation"
    DISCOVERY = "discovery"


class DeltaLevel(str, Enum):
    """Pine's Delta Model — depth of transformation currently experienced.

    Tracks where the agent is in their transformation arc, independent of
    calendar time. A MENTOR-stage agent who has stopped growing may still
    be at TRANSPORTING rather than TRANSFORMING delta level.
    """
    MEMORABLE = "memorable"        # Experience registered, no lasting change
    MEANINGFUL = "meaningful"      # Beginning to integrate new identity
    TRANSPORTING = "transporting"  # Consistently transported to new state
    TRANSFORMING = "transforming"  # Sustained "I was X, now I am Y"
    METAMORPHIC = "metamorphic"    # Core identity unrecognizable from before


class GuideRole(str, Enum):
    """The mentor's guide role in this relationship (Pine Ch. 7).

    Derived from the mentee's aspiration_type and transformation sphere.
    The right guide role maximizes transformation effectiveness.

    EXPERT      — enhancing transformation (refinement aspirations)
                  Shares knowledge, provides feedback, optimizes performance
    COACH       — expanding transformation (ambition aspirations)
                  Pushes boundaries, sustains motivation through long arcs
    COUNSELOR   — enriching transformation (cultivation aspirations)
                  Supports identity exploration, holds space for uncertainty
    ALCHEMIST   — metamorphic transformation (metamorphosis aspirations)
                  Facilitates core identity change; the rarest and deepest role
    """
    EXPERT = "expert"
    COACH = "coach"
    COUNSELOR = "counselor"
    ALCHEMIST = "alchemist"


# ─────────────────────────────────────────────────────────────────────────────
# Relationship Types
# ─────────────────────────────────────────────────────────────────────────────

class RelationType(str, Enum):
    """Types of relationships between agents."""
    MENTORS = "MENTORS"
    PEERS = "PEERS"
    INSPIRED_BY = "INSPIRED_BY"
    RECRUITED_BY = "RECRUITED_BY"


# ─────────────────────────────────────────────────────────────────────────────
# Core Data Classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AgentNode:
    """A person in the development graph.

    Core state (belief_level + habit_strength) models the interior arc of
    personal transformation. Transformation Economy properties (aspiration_type,
    transformation_sphere, catalyst_type, delta_level) provide the theoretical
    context for why and how this person is transforming.

    Pine's key insight: transformation is identity change — "I was X, now I am Y."
    The delta_level tracks the depth of that identity change, while stage tracks
    the community-visible milestone progression.
    """

    # Identity
    name: str
    bio: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    # Development state
    stage: Stage = Stage.SEED
    belief_level: int = 50      # 0-100: inner game — belief in self, system, mission
    habit_strength: int = 50    # 0-100: outer game — consistency of daily practice
    months_active: int = 0
    income_tier: int = 0        # 0-5: economic milestone proxy
    mentorship_received: int = 0  # cumulative months of active mentor relationship

    # Transformation Economy properties (Pine & Gilmore)
    aspiration_type: AspirationTypes = AspirationTypes.AMBITION
    transformation_sphere: TransformationSphere = TransformationSphere.KNOWLEDGE_WISDOM
    catalyst_type: CatalystType = CatalystType.DIRECTED
    delta_level: DeltaLevel = DeltaLevel.MEMORABLE
    follow_through_score: float = 50.0  # 0-100: sustaining transformation after milestone

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["stage"] = self.stage.value
        d["aspiration_type"] = self.aspiration_type.value
        d["transformation_sphere"] = self.transformation_sphere.value
        d["catalyst_type"] = self.catalyst_type.value
        d["delta_level"] = self.delta_level.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentNode":
        data = dict(data)
        data["stage"] = Stage(data["stage"])
        if "aspiration_type" in data:
            data["aspiration_type"] = AspirationTypes(data["aspiration_type"])
        if "transformation_sphere" in data:
            data["transformation_sphere"] = TransformationSphere(data["transformation_sphere"])
        if "catalyst_type" in data:
            data["catalyst_type"] = CatalystType(data["catalyst_type"])
        if "delta_level" in data:
            data["delta_level"] = DeltaLevel(data["delta_level"])
        return cls(**data)


@dataclass
class RelationshipEdge:
    """A directed relationship between two agents.

    For MENTORS relationships, guide_role encodes the type of transformation
    guidance being provided (Pine Ch. 7: Expert, Coach, Counselor, Alchemist).
    The guide role should be set based on the mentee's aspiration_type and
    the mentor's own transformation sphere.
    """

    source_id: str
    target_id: str
    rel_type: RelationType = RelationType.PEERS
    strength: int = 50
    months_active: int = 0
    guide_role: Optional[GuideRole] = None  # Only set for MENTORS relationships

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["rel_type"] = self.rel_type.value
        if self.guide_role is not None:
            d["guide_role"] = self.guide_role.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelationshipEdge":
        data = dict(data)
        data["rel_type"] = RelationType(data["rel_type"])
        if data.get("guide_role"):
            data["guide_role"] = GuideRole(data["guide_role"])
        return cls(**data)
