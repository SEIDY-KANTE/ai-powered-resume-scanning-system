import streamlit as st
from datetime import date
from services import job_service
import pandas as pd


def run():
    st.title("🧑‍💼 HR Portal: Manage Job Postings")

    job_df = job_service.load_jobs()

    # === Add New Job Form ===
    with st.expander("➕ Add New Job Posting", expanded=False):
        with st.form("add_job_form"):
            st.subheader("📋 Job Details")
            job_title = st.text_input("Job Title")
            company = st.text_input("Company Name")
            description = st.text_area("Job Description", height=100)
            location = st.text_input("Location")
            job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Internship", "Contract", "Temporary"])
            salary = st.text_input("Salary Range (e.g., $70k - $100k)")
            experience = st.selectbox("Experience Level", ["Entry", "Mid", "Senior"])
            skills = st.text_area("Required Skills (comma-separated)")
            industry = st.text_input("Industry")
            posted_date = st.date_input("Posted Date", value=date.today())
            employment_mode = st.selectbox("Employment Mode", ["Remote", "On-site", "Hybrid"])

            submitted = st.form_submit_button("✅ Add Job")
            if submitted:
                job_service.add_job({
                    "Job Title": job_title,
                    "Company Name": company,
                    "Job Description": description,
                    "Location": location,
                    "Job Type": job_type,
                    "Employment Mode": employment_mode,
                    "Experience Level": experience,
                    "Industry": industry,
                    "Posted Date": str(posted_date),
                    "Salary Range": salary,
                    "Skills Required": skills,
                })
                st.success("✅ Job added successfully!")
                st.rerun()

    st.markdown("### 📄 Existing Job Postings")
    job_df = job_service.load_jobs()
    if job_df.empty:
        st.info("No job postings yet.")
    else:
        for idx, row in job_df.iterrows():
            with st.expander(f"{idx+1} - {row['Job Title']} at {row['Company Name']}"):
                with st.form(f"edit_form_{idx}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        job_title = st.text_input("Job Title", value=row['Job Title'], key=f"title_{idx}")
                        company = st.text_input("Company Name", value=row['Company Name'], key=f"company_{idx}")
                        location = st.text_input("Location", value=row['Location'], key=f"loc_{idx}")
                        job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Internship", "Contract", "Temporary"], index=["Full-time", "Part-time", "Internship", "Contract", "Temporary"].index(row['Job Type']), key=f"type_{idx}")
                        employment_mode = st.selectbox("Employment Mode", ["Remote", "On-site", "Hybrid"], index=["Remote", "On-site", "Hybrid"].index(row['Employment Mode']), key=f"mode_{idx}")
                        experience = st.selectbox("Experience Level", ["Entry", "Mid", "Senior"], index=["Entry", "Mid", "Senior"].index(row['Experience Level']), key=f"exp_{idx}")
                    with col2:
                        industry = st.text_input("Industry", value=row['Industry'], key=f"industry_{idx}")
                        posted_date = st.date_input("Posted Date", value=pd.to_datetime(row['Posted Date']), key=f"date_{idx}")
                        salary = st.text_input("Salary Range", value=row['Salary Range'], key=f"salary_{idx}")
                        skills = st.text_area("Required Skills", value=row['Skills Required'], key=f"skills_{idx}")
                        description = st.text_area("Job Description", value=row['Job Description'], height=100, key=f"desc_{idx}")

                    col_save, col_del = st.columns([1, 1])
                    with col_save:
                        if st.form_submit_button("📎 Save Changes"):
                            job_service.update_job(idx, {
                                "Job Title": job_title,
                                "Company Name": company,
                                "Job Description": description,
                                "Location": location,
                                "Job Type": job_type,
                                "Employment Mode": employment_mode,
                                "Experience Level": experience,
                                "Industry": industry,
                                "Posted Date": str(posted_date),
                                "Salary Range": salary,
                                "Skills Required": skills,
                            })
                            st.success("✅ Changes saved!")
                            st.rerun()
                            st.session_state[f"edit_form_{idx}"] = None
                            st.session_state[f"expander_{idx}"] = False

                    with col_del:
                        if st.form_submit_button("❌ Delete Job"):
                            job_service.delete_job(idx)
                            st.warning("Job deleted.")
                            st.rerun()
