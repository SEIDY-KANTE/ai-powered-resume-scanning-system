# ui/theme.py
import streamlit as st
from pathlib import Path

THEME_PATH = Path("assets/themes")

def load_css(file_path):
    with open(file_path) as f:
        return f"<style>{f.read()}</style>"

def apply_custom_theme(theme_mode="Light"):
    if theme_mode == "Dark":
        css = load_css(THEME_PATH / "dark.css")
    else:
        css = load_css(THEME_PATH / "light.css")
    st.markdown(css, unsafe_allow_html=True)
