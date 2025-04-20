# Applicant Page

import streamlit as st
from datetime import datetime
from pathlib import Path
import requests
from streamlit_lottie import st_lottie

st.set_page_config(
    page_title="AI-powered Resume Scanning System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("👩🏻‍🎓 Applicant")
st.markdown("""
This page allows applicants to upload their resumes and analyze them using the AI Job Match Analyzer.
""")


