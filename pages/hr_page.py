# Human resources page

import streamlit as st
from datetime import datetime
from pathlib import Path
import requests
from streamlit_lottie import st_lottie

# Human Resources Page Config
st.set_page_config(
    page_title="AI-powered Resume Scanning System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Human Resources Title with iccon to entry job description 
st.title("🧑‍💼 Human Resources")
st.markdown("""
This page allows HR professionals to enter job descriptions and analyze them using the AI Job Match Analyzer.
""")

