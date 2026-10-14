# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Owner — holds a name and a list of Pets; responsible for owning the pets.
Pet — holds a name, species, and its own list of Tasks.
Task — holds what needs doing (title, duration, priority, how often it recurs); responsible for knowing whether it's due on a given day (is_due).
Scheduler — the only class with real "decision-making" responsibility: given an owner and a time budget, it figures out which due tasks fit and in what order.
Plan, ScheduledTask, SkippedTask — not decision-makers, just structured records of the scheduler's output (what got in, what didn't, and why).

Owner → Pet → Task as a chain (rather than, say, tasks belonging directly to the owner) because a task is inherently about one pet, and an owner can have several pets.
Keeping Scheduler separate from the data classes, so "what things are" (Owner/Pet/Task) is separate from "how a plan gets decided" (Scheduler).
**b. Design changes**

- Designed for recurring tasks that could occur like multiple walks in a week or medications taken twice a day.
-- Possibility of an owner having more than one pets and their schedules being similar or different and having a chance to manage that.
- Made class Scheduler as its own file as it is the engine that handles all the other components like task, pet and owner.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

I prioritized time budget, the time the owner has for their pets and the recurrence of the tasks. As for preferences, i have owner.preffered_start_tune in the scheduler that let's the owner decide what time of the day works for them.

**b. Tradeoffs**

One clear tradeoff: the scheduler is strictly priority-greedy — it fills the time budget with the highest-priority (then shortest) tasks first, which means a lower-priority task can get bumped entirely even if it would've fit alongside a slightly different ordering. That's reasonable here because a missed walk or feeding (high priority) matters far more to a busy owner than a skipped brushing session (low priority), so optimizing for "the most important things definitely happen" beats optimizing for "squeeze in the maximum number of tasks.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    - planning and design of the UML diagrams and verification of the classes
    - fixes to some design
- What kinds of prompts or questions were most helpful?
    - why it decided to make the scheduler a different file instead of a class was because it combined the logic of all the classes and needed its own stand alone
    - code explainations of decoraters and the methods it used

**b. Judgment and verification**

When filling out the readme file, the agent suggested a pytest bash command that was not aligned to powershell. It also hallucinated a command that was not in my pycache neither in the requirements.txt so I had to reject the change and use the standard pytest running command.
Running bash commands to test the functionality of the code. I needed to create a seperate file main.py to visualize the tests and also understand the implementations of what and how i am testing the logic. So when AI wrote the file I perused to ensure it's checking for the implementations i wanted for Pawpal.
However, the AI did not explicitly set a preference list for the owner and implied that the start-time was a preference which could have had a better preference allocation/feature.
---

## 4. Testing and Verification

**a. What you tested**

I tested the model (`is_due` recurrence across daily/weekly/completed states, and the weekly-with-no-weekdays `ValueError`) and the scheduler (priority/duration sort order across pets, not-due tasks being excluded vs. over-budget tasks being skipped, and that scheduled times never overlap), since those are the behaviors a wrong plan would silently depend on.

**b. Confidence**

All 21 tests passing gives me solid confidence in the core sort/filter/budget logic, but with more time I'd add edge cases like a zero-minute time budget, a single task longer than the entire budget, and marking a weekly task complete on a day it isn't even due.

---

## 5. Reflection

**a. What went well**

Understanding more features of streamlit and piecing a whole project together starting from the UML, to building the logic and the UI.

**b. What you would improve**

A little more freedom to explore with my design of how I would manage my pets.

**c. Key takeaway**

Not everything AI suggests is correct, I will also have to verify it, especially the bash commands. Following it sometimes in a manual format helps understand the actions, the agent takes.
