# app.py (Home Page)
import streamlit as st
from datetime import date,datetime

# Page Config
st.set_page_config(
    page_title="AI-powered Resume Scanning System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)



# === Sidebar Input Form ===
st.sidebar.title("📄 Job Description & Resume Upload")
with st.sidebar.form("job_form"):
    st.subheader("📋 Job Details")
    job_title = st.text_input("Job Title")
    company_name = st.text_input("Company Name")
    job_description = st.text_area("Full Job Description", height=200)

    st.subheader("🌍 Job Metadata")
    location = st.text_input("Location")
    job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Internship", "Temporary"])
    employment_mode = st.selectbox("Employment Mode", ["On-site", "Remote", "Hybrid"])
    experience_level = st.selectbox("Experience Level", ["Entry", "Mid", "Senior"])
    industry = st.text_input("Industry")
    posted_date = st.date_input("Posted Date", value=date.today())

    st.subheader("💰 Compensation & Skills")
    salary_range = st.text_input("Salary Range (e.g., $70k - $100k)")
    skills_required = st.text_area("Skills Required (comma-separated)")

    submit_job = st.form_submit_button("✅ Save Job Description")

# === Sidebar Resume Upload ===
st.sidebar.subheader("📄 Upload Resume & Model Selection")
resume_file = st.sidebar.file_uploader("📤 Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
model_choice = st.sidebar.radio("🧠 Choose Model for Analysis", ["My Custom Model", "Gemini Pro"])

if st.sidebar.button("🔍 Analyze Resume"):
    if not job_title or not job_description:
        st.sidebar.warning("Please fill in the job description before submitting.")
    elif not resume_file:
        st.sidebar.warning("Please upload a resume to analyze.")
    else:
        st.session_state['analyze'] = True
        st.session_state["job_data"] = {
            "Job Title": job_title,
            "Company Name": company_name,
            "Job Description": job_description,
            "Location": location,
            "Job Type": job_type,
            "Salary Range": salary_range,
            "Experience Level": experience_level,
            "Skills Required": skills_required,
            "Industry": industry,
            "Posted Date": str(posted_date),
            "Employment Mode": employment_mode
        }

# === Main Section ===
st.title("💼 AI-powered Resume Scanning System")
st.markdown("""
This intelligent system helps match your resume to job descriptions using AI.
Choose between a **custom ML model** or **Gemini Pro** for analysis.
""")

# === Display Job Overview ===
if submit_job or st.session_state.get('analyze'):
    job_data = st.session_state.get("job_data", {})
    if job_data:
        st.markdown("---")
        st.subheader("📋 Job Overview")
        for key, value in job_data.items():
            st.write(f"**{key}**: {value}")

# === Display Analysis ===
if st.session_state.get('analyze'):
    st.markdown("---")
    st.subheader("🔎 Analysis Result")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ✅ Match Accuracy")
        st.progress(0.75, text="75% Match")

    with col2:
        st.markdown("#### ❌ Missing Requirements")
        st.markdown("- [Placeholder: Python]\n- [Placeholder: AWS]")

    st.markdown("---")
    st.markdown("### 📄 Resume Summary")
    st.text("[Extracted content or key highlights from resume goes here]")

    st.markdown("### 📌 Gemini/Model Suggestions")
    st.info("[Suggestions and insights based on selected model will appear here]")

# === Footer ===

# tHE FOOTER MUST BE AT THE END OF THE PAGE

st.markdown("---")
st.markdown("### 👥 Team Members")

# space between the icons
# st.markdown(
#     """
#     ![GitHub](https://img.icons8.com/ios-filled/25/000000/github.png) [Seidy KANTE](
#     https://github.com/SEIDY-KANTE
#     )     ![GitHub](https://img.icons8.com/ios-filled/25/000000/github.png) [Şeyma KARTAL](
#     https://github.com/kartalicesym
#     )    ![GitHub](https://img.icons8.com/ios-filled/25/000000/github.png) [Hamidoune BARY](
#     https://github.com/hamidoune
#     ) 
#     """
# )
st.markdown(
    """
    <a href="
    https://github.com/SEIDY-KANTE" target="_blank"><img src="https://img.icons8.com/ios-filled/20/github.png"/>Seidy KANTE</a>&nbsp;&nbsp;&nbsp;
        <a href="
    https://github.com/kartalicesym" target="_blank"><img src="https://img.icons8.com/ios-filled/20/github.png"/>Şeyma KARTAL</a>&nbsp;&nbsp;&nbsp;
        <a href="
    https://github.com/hamidoune" target="_blank"><img src="https://img.icons8.com/ios-filled/20/github.png"/>Hamidoune BARY</a>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
st.markdown(f"© {datetime.now().year} AI-Powered Resume Scanning System. All rights reserved.")
