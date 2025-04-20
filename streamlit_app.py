# steamlit_app.py
import streamlit as st

# --- Define Pages ---

main_page = st.Page("app.py", title="Home ", icon="🧠")
hr_page = st.Page("./pages/hr_page.py", title="Human Resources", icon="🧑‍💼")
applicant_page = st.Page("./pages/applicant_page.py", title="Applicant", icon="👩🏻‍🎓")
dashbooard_page = st.Page("./pages/dashboard.py", title="Dashboard", icon="📊")



# --- Navigation ---
selected_page = st.navigation([main_page, hr_page, applicant_page, dashbooard_page])



# --- Run Selected Page ---
selected_page.run()


# --- Sidebar Branding & Theme Toggle ---
# st.sidebar.markdown("## 🌐 Navigation")



# Theme icon toggle
theme_icon = st.sidebar.radio(
    "Theme",
    options=["☀️", "🌙"],
    index=0,
    horizontal=True,
    label_visibility="collapsed"
)

# Map icons to themes
theme_mode = "Light" if theme_icon == "☀️" else "Dark"

# --- Apply Custom Theme ---
def apply_custom_theme(theme):
    if theme == "Dark":
        st.markdown(
            """
            <style>
            html, body, [class*="st-"] {
                background-color: #1e1e1e !important;
                color: #ffffff !important;
            }
            .stApp {
                background-color: #1e1e1e !important;
            }
            .css-18e3th9 {
                background-color: #1e1e1e !important;
            }
            .css-1cpxqw2, .css-ffhzg2, .css-1d391kg, .css-hxt7ib {
                background-color: #2e2e2e !important;
                color: #ffffff !important;
            }
            .stTextInput input, .stTextArea textarea, .stSelectbox div, .stDateInput input {
                background-color: #333 !important;
                color: white !important;
            }
            .stButton button {
                background-color: #444 !important;
                color: white !important;
                border: none;
            }
            .stRadio div {
                background-color: transparent !important;
            }
            .stMarkdown, .stDataFrame, .stText, .stInfo {
                color: white !important;
            }
            .css-1v3fvcr {
                background-color: #2c2c2c !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            html, body, [class*="st-"] {
                background-color: white !important;
                color: black !important;
            }
            .stApp {
                background-color: white !important;
            }
            .stTextInput input, .stTextArea textarea, .stSelectbox div, .stDateInput input {
                background-color: white !important;
                color: black !important;
            }
            .stButton button {
                background-color: #f0f2f6 !important;
                color: black !important;
                border: 1px solid #ccc;
            }
            .stMarkdown, .stDataFrame, .stText, .stInfo {
                color: black !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )



apply_custom_theme(theme_mode)
