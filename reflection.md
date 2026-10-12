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

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
Running bash commands to test the functionality of the code. I needed to create a seperate file main.py to visualize the tests and also understand the implementations of what and how i am testing the logic. So when AI wrote the file I perused to ensure it's checking for the implementations i wanted for Pawpal.
However, the AI did not explicitly set a preference list for the owner and implied that the start-time was a preference which could have had a better preference allocation/feature.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
