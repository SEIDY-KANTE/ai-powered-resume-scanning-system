import streamlit as st
from services.resume_parser import parse_resume
from services.matcher import match_resume_to_job
from datetime import datetime
import pandas as pd
import time
import os
import plotly.express as px
from streamlit_pdf_viewer import pdf_viewer
import tempfile
from docx import Document

def save_prediction_to_csv(resume_data, job_data, analysis_result, model_used):
    directory = "data"
    if not os.path.exists(directory):
        os.makedirs(directory)
    history_file = os.path.join(directory, "prediction_history.csv")

    # history_file = "prediction_history.csv"
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        # "applicant_name": resume_data.get("name", "N/A"),
        "job_title": job_data.get("Job Title", "N/A"),
        "model_used": model_used,
        "match_score": analysis_result['match_score'],
        "skill_match": analysis_result['skill_match'],
        "experience_match": analysis_result['experience_match'],
        "missing_skills": ", ".join(analysis_result['missing_skills'])
    }
    df_new = pd.DataFrame([new_entry])
    if os.path.exists(history_file):
        df_existing = pd.read_csv(history_file)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(history_file, index=False)

def run():
    st.title("🧑‍💼 Applicant Portal")
    st.markdown("""
    <style>
    .big-font { font-size:22px !important; font-weight:600; }
    .small-muted { color:gray; font-size:14px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='big-font'>📄 Upload Resume & Get Matched Instantly</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Using AI to match your profile to job roles in real-time.</div>", unsafe_allow_html=True)
    st.markdown("---")

    if "job_data" not in st.session_state:
        st.warning("⚠️ Please select a job from the Home page first.")
        return

    job_data = st.session_state["job_data"]

    with st.expander("📋 View Job Description", expanded=True):
        for key, val in job_data.items():
            st.markdown(f"**{key}:** {val}")

    st.markdown("---")
    st.subheader("📤 Upload Your Resume")

    if "model_choice" not in st.session_state:
        st.session_state.model_choice = "My Custom Model"

    selected_model = st.radio(
        "Choose Analysis Model",
        ["My Custom Model", "Gemini Pro"],
        captions=[
            "Custom model trained on your data",
            "Gemini Pro model for general analysis"
        ],
        horizontal=True,
        index=["My Custom Model", "Gemini Pro"].index(st.session_state.model_choice),
        key="model_choice_radio"
    )
    st.session_state.model_choice = selected_model

    if st.session_state.model_choice == "My Custom Model":
        st.info("Using your custom trained model for resume analysis.")
    else:
        st.info("Using Gemini Pro for powerful generative suggestions.")

    with st.form("resume_form"):
        resume_file = st.file_uploader("Choose a Resume File (PDF or DOCX)", type=["pdf", "docx"])
        submitted = st.form_submit_button("🚀 Analyze Resume")

    if submitted:
        if not resume_file:
            st.warning("⚠️ Please upload a resume before submitting.")
            return

        with st.spinner("🔧 Parsing your resume..."):
            resume_data = parse_resume(resume_file)
            time.sleep(1)

        with st.spinner("⚙️ Matching resume with job requirements..."):
            analysis_result = match_resume_to_job(resume_data, job_data, model=st.session_state.model_choice)
            time.sleep(1)

        st.success("✅ Resume analysis complete!")
        st.toast("Results ready! Scroll down to view insights. 🎉")
        save_prediction_to_csv(resume_data, job_data, analysis_result, selected_model)

        st.markdown("---")
        st.subheader("📊 Match Results")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Match Score", f"{analysis_result['match_score']}%")
            st.progress(analysis_result['match_score'] / 100)

            st.metric("Skill Match", f"{analysis_result['skill_match']}%")
            st.progress(analysis_result['skill_match'] / 100)

        with col2:
            st.metric("Experience Fit", f"{analysis_result['experience_match']}%")
            st.progress(analysis_result['experience_match'] / 100)

            st.metric("Missing Skills", f"{len(analysis_result['missing_skills'])}")
            if analysis_result['missing_skills']:
                st.warning(", ".join(analysis_result['missing_skills']))

        st.markdown("---")
        st.subheader("📈 Visual Breakdown")
        fig = px.pie(
            names=["Skill Match", "Experience Match", "Missing Skills"],
            values=[analysis_result['skill_match'], analysis_result['experience_match'], len(analysis_result['missing_skills'])],
            title="Resume Fit Breakdown"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🧠 Suggestions")
        if analysis_result['missing_skills']:
            with st.expander("🛠️ Recommended Skills to Learn"):
                st.info("Consider learning the following skills:")
                for skill in analysis_result['missing_skills']:
                    st.markdown(f"- {skill}")
        else:
            st.success("You're a great match! Your resume aligns well with this job.")

        if selected_model == "Gemini Pro" and "Suggestions" in analysis_result:
            st.markdown("---")
            st.subheader("🔍 Gemini Pro Insights")
            st.info("Additional suggestions to improve your resume:")
            st.markdown(analysis_result["Suggestions"])

        # with st.expander("📂 Raw Resume Preview"):
        #     st.code(resume_data.get("raw_text", "N/A")[:1000] + "...", language="text")



        with st.expander("📂 Resume Preview"):
            # Initialize session state for resume
            if "resume_ref" not in st.session_state:
                st.session_state.resume_ref = None

            # Store resume in session state on upload
            if resume_file:
                st.session_state.resume_ref = resume_file

            if st.session_state.resume_ref:
                try:
                    resume_bytes = st.session_state.resume_ref.getvalue()

                    if st.session_state.resume_ref.type == "application/pdf":
                        # Use binary content directly for PDF viewer
                        if resume_bytes:
                            pdf_viewer(input=resume_bytes)
                        else:
                            st.warning("⚠️ The uploaded PDF seems to be empty.")

                    elif st.session_state.resume_ref.type in [
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "application/msword"
                    ]:
                        # Save to temp and load with python-docx
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx", mode="wb") as tmp_file:
                            tmp_file.write(resume_bytes)
                            tmp_path = tmp_file.name

                        try:
                            doc = Document(tmp_path)
                            full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
                            # st.markdown("**Resume Preview (DOCX):**")
                            # st.text_area("Extracted Resume Text", full_text[:3000] + ("..." if len(full_text) > 3000 else ""), height=400)
                            st.code(full_text[:3000] + ("..." if len(full_text) > 3000 else ""), language="text")
                        except Exception as e:
                            st.error(f"⚠️ Error reading DOCX file: {e}")
                        finally:
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)

                    else:
                        st.warning("⚠️ Unsupported file format for preview.")
                    
                    # Download button
                    st.download_button(
                        label="Download Resume",
                        data=resume_bytes,
                        file_name=st.session_state.resume_ref.name,
                        mime=st.session_state.resume_ref.type
                    )

                except Exception as e:
                    st.error(f"❌ Unexpected error: {e}")
            else:
                st.info("📄 Please upload a resume to preview it here.")

        st.caption(f"Analyzed using **{selected_model}** on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
