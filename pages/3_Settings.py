import streamlit as st
from demo_store import banner
st.set_page_config(page_title="Settings | My Workspace",page_icon="⚙️")
st.title("⚙️ Demo Settings")
banner()
st.write("Demo mode uses a temporary database for each browser session. It is not permanent storage.")
