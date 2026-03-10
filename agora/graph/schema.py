"""Node and edge type definitions for the AGORA graph."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
import uuid


class Stage(str, Enum):
    """Development stages an agent progresses through."""

    SEED = "SEED"
    GROWING = "GROWING"
    FLOURISHING = "FLOURISHING"
    MENTOR = "MENTOR"
    MASTER = "MASTER"


class RelationType(str, Enum):
    """Types of relationships between agents."""

    MENTORS = "MENTORS"
    PEERS = "PEERS"
    INSPIRED_BY = "INSPIRED_BY"
    RECRUITED_BY = "RECRUITED_BY"


@dataclass
class AgentNode:
    """A person in the development graph."""

    name: str
    stage: Stage = Stage.SEED
    belief_level: int = 50
    habit_strength: int = 50
    months_active: int = 0
    income_tier: int = 0
    mentorship_received: int = 0
    bio: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["stage"] = self.stage.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentNode:
        data = dict(data)
        data["stage"] = Stage(data["stage"])
        return cls(**data)


@dataclass
class RelationshipEdge:
    """A directed relationship between two agents."""

    source_id: str
    target_id: str
    rel_type: RelationType = RelationType.PEERS
    strength: int = 50
    months_active: int = 0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["rel_type"] = self.rel_type.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RelationshipEdge:
        data = dict(data)
        data["rel_type"] = RelationType(data["rel_type"])
        return cls(**data)
