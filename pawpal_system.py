"""Domain models for PawPal+: Owner, Pet, and Task. No scheduling logic here."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    frequency: Frequency = Frequency.DAILY
    weekday: int | None = None  # 0=Monday .. 6=Sunday; only used when frequency is WEEKLY

    def is_due(self, on_date: date) -> bool:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError
