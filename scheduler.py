"""Scheduling logic for PawPal+: turns an Owner's due tasks into a daily Plan."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from pawpal_system import Owner, Pet, Priority, Task

_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}


@dataclass
class ScheduledTask:
    task: Task
    pet: Pet
    start_time: time
    end_time: time
    reason: str


@dataclass
class SkippedTask:
    task: Task
    pet: Pet
    reason: str


@dataclass
class Plan:
    date: date
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[SkippedTask] = field(default_factory=list)
    total_minutes_used: int = 0


class Scheduler:
    def __init__(self, day_start: time = time(8, 0)) -> None:
        self.day_start = day_start

    def build_plan(self, owner: Owner, on_date: date, time_budget_minutes: int) -> Plan:
        due_tasks = [pair for pair in owner.all_tasks() if pair[1].is_due(on_date)]
        due_tasks.sort(key=lambda pair: (_PRIORITY_ORDER[pair[1].priority], pair[1].duration_minutes))

        plan = Plan(date=on_date)
        clock = datetime.combine(on_date, self.day_start)

        for pet, task in due_tasks:
            if plan.total_minutes_used + task.duration_minutes > time_budget_minutes:
                plan.skipped.append(
                    SkippedTask(
                        task=task,
                        pet=pet,
                        reason="Not enough time left in today's budget",
                    )
                )
                continue

            start = clock.time()
            clock += timedelta(minutes=task.duration_minutes)
            plan.scheduled.append(
                ScheduledTask(
                    task=task,
                    pet=pet,
                    start_time=start,
                    end_time=clock.time(),
                    reason=f"{task.priority.value} priority, fit within remaining time",
                )
            )
            plan.total_minutes_used += task.duration_minutes

        return plan
