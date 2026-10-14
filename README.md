# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:
```
# Daily plan for Jordan on 2026-10-12:
#  08:00 - 08:10 Mochi: Feed Mochi [high] (high priority, fit within remaining time)
#  08:10 - 08:40 Rex: Morning walk [high] (high priority, fit within remaining time)
```


## 🧪 Testing PawPal+

```powershell
# Run the full test suite (collects both files below):
python -m pytest

# Run with coverage:
python -m pytest --cov
```

Two test files, covering the model and the scheduler separately:

- `tests/test_pawpal.py` — the `Owner`/`Pet`/`Task` model: adding pets/tasks, `is_due` recurrence (daily, weekly-by-weekday, completed-today, completed-and-reopened), and the `ValueError` guard against a weekly task with no weekdays.
- `tests/test_scheduler.py` — `Scheduler.build_plan`: sort order (priority first, duration as tiebreak, across pets), recurrence filtering (not-due tasks are excluded, not skipped), and budget conflicts (exact-fit vs. one-minute-over boundary, a bigger task crowding out a smaller one, and scheduled times never overlapping).

======================================================================== test session starts ========================================================================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\HP\codepath\pawpal
plugins: anyio-4.15.1
collected 21 items                                                                                                                                                   

tests\test_pawpal.py ..........                                                                                                                                [ 47%]
tests\test_scheduler.py ...........                                                                                                                            [100%]

======================================================================== 21 passed in 0.10s =========================================================================

Confidence level: 5 stars

## 📐 Smarter Scheduling

**How it works:** `Owner`, `Pet`, and `Task` (in `pawpal_system.py`) model the data — an owner has multiple pets, and each pet has its own list of tasks. `Owner.all_tasks()` is the single method that gathers every task across every pet, each paired with the pet it belongs to. `Scheduler.build_plan` (in `scheduler.py`) reads only from that method, never from one pet's task list directly — that's what lets it build a plan spanning multiple pets instead of just one. It filters the full task list down to what's actually due today, sorts the due tasks by priority then duration, then walks through them in order: each task either fits in the remaining time budget and gets scheduled, or it doesn't and gets recorded as skipped, along with a reason. The result is a `Plan` containing both lists plus the total time used.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.build_plan` | Due tasks are sorted by priority (high → low), then by duration (shortest first) as a tiebreak, so higher-priority and quicker tasks get first claim on the time budget |
| Filtering | `Task.is_due`, `Scheduler.build_plan` | `is_due` excludes tasks not due today (wrong weekday, or already completed today); `build_plan` then skips any remaining task that no longer fits the time budget |
| Conflict handling | `Scheduler.build_plan` | Tasks don't have fixed times, so there's nothing to overlap — each due task is placed right after the previous one ends. A task that would exceed the remaining budget is moved to `Plan.skipped` with a reason instead of being scheduled |
| Recurring tasks | `Task.frequency`, `Task.weekdays`, `Task.is_due`, `Task.mark_completed` / `mark_incomplete` | `DAILY` tasks are due every day; `WEEKLY` tasks carry a set of weekdays (0=Mon..6=Sun) and are due only when today matches one of them. `completed_on` stores the date a task was last marked done, so it drops off today's plan once completed but reappears automatically the next time it's due |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. **Set the owner.** The "Owner" section (`app.py`) starts pre-filled with a default name ("Jordan") stored in `st.session_state.owner`; edit the text box to rename them.
2. **Add pets.** Under "Pets," enter a name + species and click "Add pet" (`Owner.add_pet`). Each pet shows up in the "Pet" dropdown used by the task form below.
3. **Add tasks.** Pick a pet, then fill in title, duration, and priority (Low/Medium/High), plus a frequency: `Daily`, or `Weekly` with specific weekdays via the "Recurs on" multiselect. Clicking "Add task" calls `Pet.add_task`; if `Weekly` is chosen with no weekdays checked, the `Task.__post_init__` guard raises a `ValueError` that's shown as an inline error instead of crashing the app.
4. **Review/edit tasks.** Each pet has an expander listing its tasks (title, duration, priority, and schedule e.g. "weekly on Mon, Wed"). Expanding a task reveals an edit form — change any field and click "Save changes" to update it in place (same weekly/weekday validation applies).
5. **Generate today's schedule.** Under "Build schedule," pick a date and how many minutes are available today, then click "Generate schedule." This calls `Scheduler().build_plan(owner, plan_date, time_budget)`, which:
   - Gathers every pet's tasks via `Owner.all_tasks()` and filters to only what's `is_due` on that date (recurrence + already-completed-today checks).
   - **Sorts** due tasks by priority (High → Low), then by duration (shortest first) as a tiebreak — so urgent, quick wins get scheduled first.
   - Walks the sorted list filling the time budget back-to-back starting at `day_start` (no fixed time slots, so nothing can double-book); any task that would blow the remaining budget is **skipped** with a reason instead of scheduled.
6. **Read the plan.** Scheduled tasks render as a time-stamped list (`08:00–08:10 — Mochi: Feed Mochi (high priority, fit within remaining time)`) each with a "Done" button that calls `Task.mark_completed` and regenerates the plan on the spot. Skipped tasks show in a ⚠️ warning table with pet, task, duration, and why they didn't fit; if nothing was skipped, a ✅ success message confirms everything fit. A caption at the bottom always shows total minutes used vs. the budget.
7. **Come back tomorrow.** Daily tasks reset automatically; weekly tasks reappear on their next matching weekday. Anything marked "Done" today will fall off the plan until its next due date, per `Task.is_due`.


