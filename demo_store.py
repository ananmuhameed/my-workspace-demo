"""Per-browser-session temporary demo data; not suitable for production storage."""
import sqlite3
import tempfile
import uuid
from pathlib import Path
import streamlit as st

SAMPLES = [
 ("Sample Organization A", "Sample Leader 1", "2026-01-05", "2026-01-09", "Example reason A"),
 ("Sample Organization B", "Sample Leader 2", "2026-02-12", "2026-02-19", "Example reason B"),
 ("Sample Organization C", "Sample Leader 1", "2026-03-01", "2026-03-03", "Example reason C"),
 ("Sample Organization A", "Sample Leader 3", "2026-04-07", "2026-04-12", "Example reason D"),
 ("Sample Organization D", "Sample Leader 2", "2026-05-11", "2026-05-20", "Example reason E"),
]

def database_path():
    if "demo_id" not in st.session_state:
        st.session_state.demo_id = uuid.uuid4().hex
    return Path(tempfile.gettempdir()) / ("my_workspace_demo_" + st.session_state.demo_id + ".db")

def connect():
    con = sqlite3.connect(database_path())
    con.execute("""CREATE TABLE IF NOT EXISTS records (
      id INTEGER PRIMARY KEY AUTOINCREMENT, entity TEXT NOT NULL,
      leader TEXT NOT NULL DEFAULT '', date_from TEXT, date_to TEXT,
      reason TEXT NOT NULL DEFAULT '')""")
    if not con.execute("SELECT 1 FROM records LIMIT 1").fetchone() and not st.session_state.get("demo_seeded",False):
        con.executemany("INSERT INTO records(entity,leader,date_from,date_to,reason) VALUES (?,?,?,?,?)",SAMPLES)
        st.session_state.demo_seeded = True
    con.commit()
    return con

def reset():
    p=database_path()
    if p.exists(): p.unlink()
    st.session_state.demo_seeded=False
    st.rerun()

def banner():
    st.info("PUBLIC DEMO · Sample data only. Changes are temporary and may disappear when the app restarts. Do not upload personal or confidential information.")
    if st.sidebar.button("Reset my demo data"):
        reset()
