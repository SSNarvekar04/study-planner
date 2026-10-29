# Study Planner

A Streamlit app that helps students organize study schedules, manage academic tasks and plan learning time.

## Features
- **Dashboard** – pending/completed/overdue counts, progress bar, upcoming deadlines, today's sessions, hours studied per subject
- **Tasks** – add, complete, delete; filter and sort by due date or priority; overdue warning
- **Study Sessions** – schedule sessions (subject, topic, date, time, duration) and mark them done
- **Focus Timer** – Pomodoro planner that splits a study block into focus rounds and breaks
- Data saved locally in `planner_data.json`

## Install and run (Windows)
```
git clone https://github.com/Jay208mane/study-planner
cd study-planner
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Tech stack
Python, Streamlit, pandas, JSON storage.

## Conclusion
The project demonstrates a study-planning application that helps students organize academic activities and manage study time effectively.
