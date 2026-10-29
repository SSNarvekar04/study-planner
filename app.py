"""Study Planner - Practical Assignment 7
A Streamlit app to plan study sessions, track academic tasks and
manage study time. Data is stored locally in planner_data.json.
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path("planner_data.json")
PRIORITIES = ["High", "Medium", "Low"]


# ---------- storage ----------
def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"tasks": [], "sessions": [], "next_id": 1}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def new_id(data):
    i = data["next_id"]
    data["next_id"] += 1
    return i


# ---------- page ----------
st.set_page_config(page_title="Study Planner", page_icon="📚", layout="wide")
st.title("📚 Study Planner")
st.caption("Organize study sessions, track academic tasks, manage your time.")

data = load_data()
today = date.today()

tab_dash, tab_tasks, tab_sessions, tab_timer = st.tabs(
    ["Dashboard", "Tasks", "Study Sessions", "Focus Timer"]
)

# ---------- dashboard ----------
with tab_dash:
    tasks = data["tasks"]
    done = sum(t["done"] for t in tasks)
    pending = len(tasks) - done
    overdue = sum(
        1 for t in tasks if not t["done"] and date.fromisoformat(t["due"]) < today
    )
    mins = sum(s["minutes"] for s in data["sessions"] if s["done"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pending tasks", pending)
    c2.metric("Completed", done)
    c3.metric("Overdue", overdue)
    c4.metric("Hours studied", f"{mins / 60:.1f}")

    if tasks:
        st.progress(done / len(tasks), text=f"{done}/{len(tasks)} tasks completed")

    st.subheader("Upcoming deadlines (next 7 days)")
    soon = [
        t for t in tasks
        if not t["done"] and today <= date.fromisoformat(t["due"]) <= today + timedelta(days=7)
    ]
    if soon:
        soon.sort(key=lambda t: t["due"])
        st.dataframe(
            pd.DataFrame(soon)[["title", "subject", "due", "priority"]],
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No deadlines in the next 7 days.")

    st.subheader("Today's study sessions")
    todays = [s for s in data["sessions"] if s["date"] == today.isoformat()]
    if todays:
        st.dataframe(
            pd.DataFrame(todays)[["start", "subject", "topic", "minutes", "done"]],
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("Nothing scheduled today.")

    if data["sessions"]:
        st.subheader("Study time by subject (completed sessions)")
        df = pd.DataFrame([s for s in data["sessions"] if s["done"]])
        if not df.empty:
            st.bar_chart(df.groupby("subject")["minutes"].sum())

# ---------- tasks ----------
with tab_tasks:
    with st.form("add_task", clear_on_submit=True):
        st.subheader("Add task")
        a, b = st.columns(2)
        title = a.text_input("Task title")
        subject = b.text_input("Subject")
        d, p = st.columns(2)
        due = d.date_input("Due date", today)
        priority = p.selectbox("Priority", PRIORITIES, index=1)
        if st.form_submit_button("Add task") and title.strip():
            data["tasks"].append({
                "id": new_id(data), "title": title.strip(),
                "subject": subject.strip() or "General",
                "due": due.isoformat(), "priority": priority, "done": False,
            })
            save_data(data)
            st.rerun()

    st.subheader("Your tasks")
    f1, f2 = st.columns(2)
    show = f1.selectbox("Show", ["Pending", "Completed", "All"])
    sort_by = f2.selectbox("Sort by", ["Due date", "Priority"])

    items = [
        t for t in data["tasks"]
        if show == "All" or (show == "Pending") == (not t["done"])
    ]
    if sort_by == "Due date":
        items.sort(key=lambda t: t["due"])
    else:
        items.sort(key=lambda t: PRIORITIES.index(t["priority"]))

    if not items:
        st.info("No tasks to show.")
    for t in items:
        late = (not t["done"]) and date.fromisoformat(t["due"]) < today
        c = st.columns([5, 2, 1, 1, 1])
        label = f"~~{t['title']}~~" if t["done"] else f"**{t['title']}**"
        c[0].markdown(f"{label}  \n{t['subject']} · due {t['due']}" + (" ⚠️ overdue" if late else ""))
        c[1].write(t["priority"])
        if c[2].button("✔" if not t["done"] else "↩", key=f"tg{t['id']}"):
            t["done"] = not t["done"]
            save_data(data)
            st.rerun()
        if c[3].button("🗑", key=f"dl{t['id']}"):
            data["tasks"] = [x for x in data["tasks"] if x["id"] != t["id"]]
            save_data(data)
            st.rerun()

# ---------- sessions ----------
with tab_sessions:
    with st.form("add_session", clear_on_submit=True):
        st.subheader("Schedule a study session")
        a, b = st.columns(2)
        s_subject = a.text_input("Subject")
        s_topic = b.text_input("Topic")
        c1, c2, c3 = st.columns(3)
        s_date = c1.date_input("Date", today, key="sd")
        s_start = c2.time_input("Start time", datetime.now().replace(minute=0, second=0).time())
        s_min = c3.number_input("Duration (minutes)", 15, 480, 60, step=15)
        if st.form_submit_button("Add session") and s_subject.strip():
            data["sessions"].append({
                "id": new_id(data), "subject": s_subject.strip(),
                "topic": s_topic.strip(), "date": s_date.isoformat(),
                "start": s_start.strftime("%H:%M"), "minutes": int(s_min), "done": False,
            })
            save_data(data)
            st.rerun()

    st.subheader("Weekly schedule")
    week = sorted(data["sessions"], key=lambda s: (s["date"], s["start"]))
    if not week:
        st.info("No sessions scheduled yet.")
    for s in week:
        c = st.columns([5, 1, 1, 1])
        c[0].markdown(
            f"**{s['subject']}** – {s['topic'] or 'general'}  \n"
            f"{s['date']} at {s['start']} · {s['minutes']} min"
        )
        c[1].write("✅" if s["done"] else "⏳")
        if c[2].button("✔" if not s["done"] else "↩", key=f"sg{s['id']}"):
            s["done"] = not s["done"]
            save_data(data)
            st.rerun()
        if c[3].button("🗑", key=f"sx{s['id']}"):
            data["sessions"] = [x for x in data["sessions"] if x["id"] != s["id"]]
            save_data(data)
            st.rerun()

# ---------- focus timer (Pomodoro helper) ----------
with tab_timer:
    st.subheader("Pomodoro planner")
    st.write("Splits a study block into focused work and short breaks.")
    total = st.number_input("Total study time (minutes)", 25, 480, 120, step=5)
    work = st.slider("Focus length (min)", 15, 60, 25)
    brk = st.slider("Short break (min)", 3, 15, 5)
    plan, t, n = [], 0, 1
    while t + work <= total:
        plan.append({"Round": n, "Focus (min)": work, "Break (min)": brk if t + work + brk < total else 0})
        t += work + brk
        n += 1
    if plan:
        st.dataframe(pd.DataFrame(plan), hide_index=True, use_container_width=True)
        st.success(f"{len(plan)} focus rounds fit into {total} minutes.")
    else:
        st.warning("Total time is shorter than one focus round.")
