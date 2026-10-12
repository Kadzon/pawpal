"""Quick manual test of the Owner/Pet/Task/Scheduler logic, run directly from the CLI."""
from datetime import date

from pawpal_system import Frequency, Owner, Pet, Priority, Task
from scheduler import Scheduler


def build_sample_owner() -> Owner:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="cat")
    mochi.add_task(Task(title="Feed Mochi", duration_minutes=10, priority=Priority.HIGH))

    rex = Pet(name="Rex", species="dog")
    rex.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH))
    rex.add_task(
        Task(
            title="Brushing",
            duration_minutes=15,
            priority=Priority.LOW,
            frequency=Frequency.WEEKLY,
            weekdays={0, 2, 4},  # Mon / Wed / Fri
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(rex)
    return owner


def main() -> None:
    owner = build_sample_owner()
    today = date(2026, 10, 12)  # a Monday

    plan = Scheduler().build_plan(owner, today, time_budget_minutes=45)

    print(f"Daily plan for {owner.name} on {today}:")
    for scheduled in plan.scheduled:
        print(
            f"  {scheduled.start_time.strftime('%H:%M')} - {scheduled.end_time.strftime('%H:%M')} "
            f"{scheduled.pet.name}: {scheduled.task.title} "
            f"[{scheduled.task.priority.value}] ({scheduled.reason})"
        )

    if plan.skipped:
        print("\nSkipped:")
        for skipped in plan.skipped:
            print(f"  {skipped.pet.name}: {skipped.task.title} - {skipped.reason}")

    print(f"\nTotal minutes used: {plan.total_minutes_used}")


if __name__ == "__main__":
    main()
