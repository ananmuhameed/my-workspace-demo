import sqlite3
from pathlib import Path
import streamlit as st
st.set_page_config(page_title="My Workspace",page_icon="🗂️",layout="wide")
st.title("🗂️ My Workspace")
st.caption("Public demo workspace for data, reports, and documents")
st.divider()
from demo_store import connect, banner
banner()
with connect() as con:
    count = con.execute("SELECT COUNT(*) FROM records").fetchone()[0]
st.metric("Total records",count)
a,b=st.columns(2)
with a:
    with st.container(border=True):
        st.subheader("📊 Data Management")
        st.write("Import Excel records, search, filter by leader and date, edit, export and analyze.")
        st.page_link("pages/1_Data_Management.py",label="Open Data Management →")
with b:
    with st.container(border=True):
        st.subheader("📄 Word Generator")
        st.write("Generate Word documents from Excel rows and a DOCX template.")
        st.page_link("pages/2_Word_Generator.py",label="Open Word Generator →")
st.page_link("pages/3_Settings.py",label="⚙️ Settings")
