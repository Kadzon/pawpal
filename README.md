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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
# rootdir: C:\Users\HP\codepath\pawpal
# plugins: anyio-4.15.1
# collected 8 items                                                                                                                                                    

tests\test_pawpal.py 
```

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

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
