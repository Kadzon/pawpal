from datetime import date

import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Task
from scheduler import Scheduler

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care tasks around how much time you actually have.")

# --- Owner + pets live in session_state so they survive Streamlit's reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
if "plan" not in st.session_state:
    st.session_state.plan = None
if "plan_date" not in st.session_state:
    st.session_state.plan_date = None
if "plan_budget" not in st.session_state:
    st.session_state.plan_budget = None

owner = st.session_state.owner


def regenerate_plan() -> None:
    """Rebuild the plan using the last date/budget the user generated with."""
    if st.session_state.plan_date is not None:
        st.session_state.plan = Scheduler().build_plan(
            owner, st.session_state.plan_date, st.session_state.plan_budget
        )


st.divider()
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()
st.subheader("Pets")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    new_pet_name = st.text_input("Pet name", key="new_pet_name")
with col2:
    new_pet_species = st.text_input("Species", key="new_pet_species")
with col3:
    st.write("")
    if st.button("Add pet") and new_pet_name:
        owner.add_pet(Pet(name=new_pet_name, species=new_pet_species))

if not owner.pets:
    st.info("No pets yet. Add one above.")
    st.stop()

st.divider()
st.subheader("Tasks")

pet_names = [pet.name for pet in owner.pets]
selected_pet_name = st.selectbox("Pet", pet_names)
selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", list(Priority), format_func=lambda p: p.value.capitalize())

frequency = st.selectbox("Frequency", list(Frequency), format_func=lambda f: f.value.capitalize())
weekdays: set[int] = set()
if frequency == Frequency.WEEKLY:
    selected_days = st.multiselect("Recurs on", WEEKDAY_NAMES)
    weekdays = {WEEKDAY_NAMES.index(day) for day in selected_days}

if st.button("Add task"):
    try:
        selected_pet.add_task(
            Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
                weekdays=weekdays,
            )
        )
    except ValueError as exc:
        st.error(str(exc))

for pet in owner.pets:
    with st.expander(f"{pet.name}'s tasks ({len(pet.tasks)})", expanded=False):
        if not pet.tasks:
            st.caption("No tasks yet.")
            continue
        for i, task in enumerate(pet.tasks):
            schedule = (
                "daily"
                if task.frequency == Frequency.DAILY
                else "weekly on " + ", ".join(WEEKDAY_NAMES[d][:3] for d in sorted(task.weekdays))
            )
            key_prefix = f"{pet.name}_{i}"
            with st.expander(f"{task.title} — {task.duration_minutes} min, {task.priority.value} priority, {schedule}"):
                edit_title = st.text_input("Title", value=task.title, key=f"{key_prefix}_title")

                col1, col2 = st.columns(2)
                with col1:
                    edit_duration = st.number_input(
                        "Duration (minutes)",
                        min_value=1,
                        max_value=240,
                        value=task.duration_minutes,
                        key=f"{key_prefix}_duration",
                    )
                with col2:
                    edit_priority = st.selectbox(
                        "Priority",
                        list(Priority),
                        index=list(Priority).index(task.priority),
                        format_func=lambda p: p.value.capitalize(),
                        key=f"{key_prefix}_priority",
                    )

                edit_frequency = st.selectbox(
                    "Frequency",
                    list(Frequency),
                    index=list(Frequency).index(task.frequency),
                    format_func=lambda f: f.value.capitalize(),
                    key=f"{key_prefix}_frequency",
                )
                edit_weekdays: set[int] = set()
                if edit_frequency == Frequency.WEEKLY:
                    default_days = [WEEKDAY_NAMES[d] for d in sorted(task.weekdays)]
                    selected_days = st.multiselect(
                        "Recurs on", WEEKDAY_NAMES, default=default_days, key=f"{key_prefix}_weekdays"
                    )
                    edit_weekdays = {WEEKDAY_NAMES.index(day) for day in selected_days}

                if st.button("Save changes", key=f"{key_prefix}_save"):
                    if edit_frequency == Frequency.WEEKLY and not edit_weekdays:
                        st.error("A weekly task needs at least one weekday selected.")
                    else:
                        task.title = edit_title
                        task.duration_minutes = int(edit_duration)
                        task.priority = edit_priority
                        task.frequency = edit_frequency
                        task.weekdays = edit_weekdays
                        st.success("Task updated.")

st.divider()
st.subheader("Build schedule")

col1, col2 = st.columns(2)
with col1:
    plan_date = st.date_input("Date", value=date.today())
with col2:
    time_budget = st.number_input("Time available today (minutes)", min_value=1, max_value=600, value=60)

if st.button("Generate schedule"):
    st.session_state.plan_date = plan_date
    st.session_state.plan_budget = int(time_budget)
    regenerate_plan()

plan = st.session_state.plan
if plan is not None:
    st.markdown(f"#### Plan for {owner.name} on {plan.date}")

    if plan.scheduled:
        for i, scheduled in enumerate(plan.scheduled):
            cols = st.columns([5, 1])
            with cols[0]:
                st.write(
                    f"**{scheduled.start_time.strftime('%H:%M')}–{scheduled.end_time.strftime('%H:%M')}** "
                    f"— {scheduled.pet.name}: {scheduled.task.title} "
                    f"*({scheduled.reason})*"
                )
            with cols[1]:
                if st.button("Done", key=f"complete_{i}"):
                    scheduled.task.mark_completed(plan.date)
                    regenerate_plan()
                    st.rerun()
    else:
        st.caption("Nothing scheduled.")

    if plan.skipped:
        count = len(plan.skipped)
        st.warning(
            f"⚠️ {count} task{'s' if count != 1 else ''} didn't fit in today's "
            f"{st.session_state.plan_budget}-minute budget:"
        )
        st.table(
            [
                {
                    "Pet": skipped.pet.name,
                    "Task": skipped.task.title,
                    "Duration": f"{skipped.task.duration_minutes} min",
                    "Why": skipped.reason,
                }
                for skipped in plan.skipped
            ]
        )
    elif plan.scheduled:
        n = len(plan.scheduled)
        task_word = "task" if n == 1 else "tasks"
        verb = "fits" if n == 1 else "fit"
        st.success(f"✅ All {n} due {task_word} {verb} within today's budget.")

    st.caption(f"Total time used: {plan.total_minutes_used} / {st.session_state.plan_budget} minutes")
