"""Tests for task addition (Pet/Owner) and task completion/recurrence (Task)."""
from datetime import date

import pytest

from pawpal_system import Frequency, Owner, Pet, Priority, Task


def test_add_task_appends_to_pet_task_list():
    pet = Pet(name="Mochi", species="cat")
    task = Task(title="Feed Mochi", duration_minutes=10, priority=Priority.HIGH)

    pet.add_task(task)

    assert pet.tasks == [task]


def test_add_pet_appends_to_owner_pet_list():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")

    owner.add_pet(pet)

    assert owner.pets == [pet]


def test_owner_all_tasks_pairs_each_task_with_its_pet():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="cat")
    rex = Pet(name="Rex", species="dog")
    feeding = Task(title="Feed Mochi", duration_minutes=10, priority=Priority.HIGH)
    walk = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH)

    mochi.add_task(feeding)
    rex.add_task(walk)
    owner.add_pet(mochi)
    owner.add_pet(rex)

    assert owner.all_tasks() == [(mochi, feeding), (rex, walk)]


def test_daily_task_is_due_until_marked_completed_today():
    task = Task(title="Feed Mochi", duration_minutes=10, priority=Priority.HIGH)
    today = date(2026, 10, 12)

    assert task.is_due(today) is True

    task.mark_completed(today)

    assert task.is_due(today) is False


def test_completed_task_is_due_again_on_a_new_day():
    task = Task(title="Feed Mochi", duration_minutes=10, priority=Priority.HIGH)
    today = date(2026, 10, 12)
    tomorrow = date(2026, 10, 13)

    task.mark_completed(today)

    assert task.is_due(tomorrow) is True


def test_mark_incomplete_undoes_completion():
    task = Task(title="Feed Mochi", duration_minutes=10, priority=Priority.HIGH)
    today = date(2026, 10, 12)

    task.mark_completed(today)
    task.mark_incomplete()

    assert task.is_due(today) is True


def test_weekly_task_only_due_on_its_selected_weekdays():
    monday = date(2026, 10, 12)
    tuesday = date(2026, 10, 13)
    task = Task(
        title="Brushing",
        duration_minutes=15,
        priority=Priority.LOW,
        frequency=Frequency.WEEKLY,
        weekdays={0},  # Monday only
    )

    assert task.is_due(monday) is True
    assert task.is_due(tuesday) is False


def test_weekly_task_without_weekdays_raises_on_creation():
    with pytest.raises(ValueError):
        Task(
            title="Brushing",
            duration_minutes=15,
            priority=Priority.LOW,
            frequency=Frequency.WEEKLY,
        )
