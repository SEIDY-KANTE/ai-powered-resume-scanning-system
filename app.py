import streamlit as st
from services import job_service
from config.constants import APPLICANT_PORTAL

def run():

    st.title("🧠 AI-Powered Resume Scanning System")
    st.header("💼 Explore Open Jobs")
    st.markdown("Browse and apply to jobs. Click 'Read More' to analyze your resume!")

    # Load job data
    job_df = job_service.load_jobs()

    if job_df.empty:
        st.warning("No jobs available yet. HR can add jobs via the HR portal.")
    else:
        cols = st.columns(3)
        for idx, row in job_df.iterrows():
            with cols[idx % 3]:
                st.image("https://cdn-icons-png.flaticon.com/512/3135/3135768.png", width=80)
                st.subheader(row["Job Title"])
                st.caption(f"📍 {row['Location']} | 💼 {row['Job Type']} | 🏢 {row['Company Name']}")
                st.markdown(f"**Description:** {row['Job Description'][:200]}...")
                if st.button("🔎 Read More & Apply", key=f"read_{idx}"):
                    st.session_state["job_data"] = row.to_dict()
                    st.session_state.selected_page = APPLICANT_PORTAL
                    st.rerun()
                   
        