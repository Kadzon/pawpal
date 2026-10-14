"""Tests for Scheduler.build_plan: sort order, recurrence filtering, and budget conflicts."""
from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Priority, Task
from scheduler import Scheduler


def _task(title, duration, priority, **kwargs):
    return Task(title=title, duration_minutes=duration, priority=priority, **kwargs)


# --- Sorting correctness -----------------------------------------------------

def test_higher_priority_is_scheduled_before_lower_priority():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    low = _task("Brush", 10, Priority.LOW)
    high = _task("Feed", 10, Priority.HIGH)
    medium = _task("Walk", 10, Priority.MEDIUM)
    pet.add_task(low)
    pet.add_task(high)
    pet.add_task(medium)
    owner.add_pet(pet)

    plan = Scheduler().build_plan(owner, date(2026, 10, 12), time_budget_minutes=60)

    assert [s.task for s in plan.scheduled] == [high, medium, low]


def test_same_priority_ties_break_by_shorter_duration_first():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    long_task = _task("Long walk", 30, Priority.HIGH)
    short_task = _task("Quick feed", 5, Priority.HIGH)
    pet.add_task(long_task)
    pet.add_task(short_task)
    owner.add_pet(pet)

    plan = Scheduler().build_plan(owner, date(2026, 10, 12), time_budget_minutes=60)

    assert [s.task for s in plan.scheduled] == [short_task, long_task]


def test_sorting_is_global_across_pets_not_grouped_by_pet():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="cat")
    rex = Pet(name="Rex", species="dog")
    mochi_low = _task("Brush", 10, Priority.LOW)
    rex_high = _task("Walk", 10, Priority.HIGH)
    mochi.add_task(mochi_low)
    rex.add_task(rex_high)
    owner.add_pet(mochi)
    owner.add_pet(rex)

    plan = Scheduler().build_plan(owner, date(2026, 10, 12), time_budget_minutes=60)

    assert [s.task for s in plan.scheduled] == [rex_high, mochi_low]


# --- Recurrence logic ---------------------------------------------------------

def test_task_completed_today_is_excluded_from_the_plan_entirely():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    today = date(2026, 10, 12)
    task = _task("Feed", 10, Priority.HIGH)
    task.mark_completed(today)
    pet.add_task(task)
    owner.add_pet(pet)

    plan = Scheduler().build_plan(owner, today, time_budget_minutes=60)

    assert plan.scheduled == []
    assert plan.skipped == []


def test_weekly_task_not_due_today_is_excluded_not_skipped():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    monday = date(2026, 10, 12)
    tuesday = date(2026, 10, 13)
    task = _task("Brushing", 15, Priority.LOW, frequency=Frequency.WEEKLY, weekdays={0})
    pet.add_task(task)
    owner.add_pet(pet)

    plan = Scheduler().build_plan(owner, tuesday, time_budget_minutes=60)

    assert plan.scheduled == []
    assert plan.skipped == []

    plan_on_monday = Scheduler().build_plan(owner, monday, time_budget_minutes=60)
    assert [s.task for s in plan_on_monday.scheduled] == [task]


def test_weekly_task_completed_on_its_due_day_reappears_the_following_week():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    this_monday = date(2026, 10, 12)
    next_monday = date(2026, 10, 19)
    task = _task("Brushing", 15, Priority.LOW, frequency=Frequency.WEEKLY, weekdays={0})
    task.mark_completed(this_monday)
    pet.add_task(task)
    owner.add_pet(pet)

    plan_same_day = Scheduler().build_plan(owner, this_monday, time_budget_minutes=60)
    plan_next_week = Scheduler().build_plan(owner, next_monday, time_budget_minutes=60)

    assert plan_same_day.scheduled == []
    assert [s.task for s in plan_next_week.scheduled] == [task]


# --- Conflict detection (time budget) -----------------------------------------

def test_task_exceeding_remaining_budget_is_skipped_with_reason():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    fits = _task("Walk", 20, Priority.HIGH)
    overflows = _task("Play", 15, Priority.MEDIUM)
    pet.add_task(fits)
    pet.add_task(overflows)
    owner.add_pet(pet)

    plan = Scheduler().build_plan(owner, date(2026, 10, 12), time_budget_minutes=30)

    assert [s.task for s in plan.scheduled] == [fits]
    assert plan.skipped[0].task is overflows
    assert plan.skipped[0].reason == "Not enough time left in today's budget"
    assert plan.total_minutes_used == 20


def test_task_exactly_filling_remaining_budget_is_scheduled_not_skipped():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    task = _task("Walk", 30, Priority.HIGH)
    pet.add_task(task)
    owner.add_pet(pet)

    plan = Scheduler().build_plan(owner, date(2026, 10, 12), time_budget_minutes=30)

    assert [s.task for s in plan.scheduled] == [task]
    assert plan.skipped == []


def test_task_one_minute_over_remaining_budget_is_skipped():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    task = _task("Walk", 31, Priority.HIGH)
    pet.add_task(task)
    owner.add_pet(pet)

    plan = Scheduler().build_plan(owner, date(2026, 10, 12), time_budget_minutes=30)

    assert plan.scheduled == []
    assert plan.skipped[0].task is task


def test_higher_priority_task_can_crowd_out_a_smaller_later_task():
    """A large high-priority task consumes most of the budget, even though
    skipping it in favor of the smaller low-priority task would have let both
    fit sequentially over two days. The scheduler is greedy-by-priority, not
    optimal-by-fit, and this pins that behavior down explicitly."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    big_high = _task("Vet trip", 25, Priority.HIGH)
    small_low = _task("Brush", 10, Priority.LOW)
    pet.add_task(big_high)
    pet.add_task(small_low)
    owner.add_pet(pet)

    plan = Scheduler().build_plan(owner, date(2026, 10, 12), time_budget_minutes=30)

    assert [s.task for s in plan.scheduled] == [big_high]
    assert plan.skipped[0].task is small_low


def test_scheduled_tasks_never_overlap_in_time():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="cat")
    first = _task("Feed", 20, Priority.HIGH)
    second = _task("Walk", 15, Priority.MEDIUM)
    pet.add_task(first)
    pet.add_task(second)
    owner.add_pet(pet)

    plan = Scheduler(day_start=time(8, 0)).build_plan(owner, date(2026, 10, 12), time_budget_minutes=60)

    assert plan.scheduled[0].start_time == time(8, 0)
    assert plan.scheduled[0].end_time == time(8, 20)
    assert plan.scheduled[1].start_time == plan.scheduled[0].end_time
    assert plan.scheduled[1].end_time == time(8, 35)
