import streamlit as st
from datetime import datetime
from pathlib import Path
import requests
from streamlit_lottie import st_lottie

# Dashboard Page Config
st.set_page_config(
    page_title="AI-powered Resume Scanning System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("📊 Dashboard")
st.markdown("""
This dashboard provides an overview of the AI Job Match Analyzer's performance and user interactions.
""")

