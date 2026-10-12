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
    weekdays: set[int] = field(default_factory=set)  # 0=Monday..6=Sunday; only used when frequency is WEEKLY
    completed_on: date | None = None  # date this task was last marked done; None means not completed

    def __post_init__(self) -> None:
        """Reject a weekly task that has no weekdays selected."""
        if self.frequency == Frequency.WEEKLY and not self.weekdays:
            raise ValueError("A weekly task needs at least one weekday selected.")

    def is_due(self, on_date: date) -> bool:
        """Return whether this task needs doing on the given date."""
        if self.completed_on == on_date:
            return False
        if self.frequency == Frequency.DAILY:
            return True
        return on_date.weekday() in self.weekdays

    def mark_completed(self, on_date: date) -> None:
        """Record that this task was done on the given date."""
        self.completed_on = on_date

    def mark_incomplete(self) -> None:
        """Clear this task's completion status."""
        self.completed_on = None


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Every task across every pet, each paired with the pet it belongs to."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]
