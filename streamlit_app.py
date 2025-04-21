import streamlit as st
from ui.theme import apply_custom_theme
from hide_sidebar.pages import hr_page, applicant_page, dashboard
import app
from config.constants import HOME, HR_PORTAL, APPLICANT_PORTAL, DASHBOARD, SYSTEM_THEME, LIGHT_THEME, DARK_THEME


# config
st.set_page_config(
    page_title="AI-powered Resume Scanning System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Sidebar Theme Toggle === (add dark, light and your system theme here)
# st.sidebar.markdown("Theme")
theme = st.sidebar.selectbox("🌓 Theme ", options=[ SYSTEM_THEME, LIGHT_THEME, DARK_THEME], index=0)

# if system dont apply theme
if theme == LIGHT_THEME:
    apply_custom_theme("Light")
elif theme == DARK_THEME:
    apply_custom_theme("Dark")
else:
    # System theme is handled by Streamlit automatically, so we don't need to apply a custom theme.
    pass

# apply_custom_theme(theme_mode)




# theme_icon = st.sidebar.radio("Theme", ["☀️", "🌙"], index=0, horizontal=True, label_visibility="collapsed")
# theme_mode = "Light" if theme_icon == "☀️" else "Dark"
# apply_custom_theme(theme_mode)

# === Navigation ===
# PAGES = {
#     "🏠 Home": app,
#     "🧑‍💼 HR Portal": hr_page,
#     "👩🏻‍🎓 Applicant Portal": applicant_page,
#     "📊 Dashboard": dashboard
# }

PAGES = {
    HOME: app,
    HR_PORTAL: hr_page,
    APPLICANT_PORTAL: applicant_page,
    DASHBOARD: dashboard
}
    
# selected_page = st.sidebar.selectbox("Navigation", options=list(PAGES.keys()))
# PAGES[selected_page].run()

if "selected_page" not in st.session_state:
    st.session_state.selected_page = HOME

selected_page = st.sidebar.selectbox(
    "Navigation", options=list(PAGES.keys()), index=list(PAGES.keys()).index(st.session_state.selected_page)
)

# This allows programmatic navigation too
st.session_state.selected_page = selected_page
PAGES[selected_page].run()

