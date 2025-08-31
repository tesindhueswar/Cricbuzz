import streamlit as st

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")

st.logo = "🏏"
st.sidebar.title("Cricbuzz LiveStats")
st.sidebar.success("Use the pages below to navigate.")

st.title("🏏 Cricbuzz LiveStats")
st.markdown("""
A real-time cricket analytics dashboard integrating **Cricbuzz API (RapidAPI)** with a **SQL database**.

**Pages**
-  Live Match updates
- Top Player Stats
-  SQL Analytics
-  CRUD Operations
""")
st.info("Head to the left sidebar to open a page.")
