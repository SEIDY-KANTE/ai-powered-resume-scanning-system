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


from config.constants import (
    MODEL_GEMINI_PRO,
    MODEL_LSTM_CUSTOM,
    MODEL_TRANSFORMER_CUSTOM,
    MODEL_RULE_BASED,
    HOME
    # PREDICTION_HISTORY_CSV
)
from config.supabase_config import supabase_client, PREDICTION_HISTORY_TABLE_NAME


def save_prediction_to_supabase(resume_filename_str, job_title_str, analysis_result_dict, model_used_str):
    """Saves the prediction result to the Supabase prediction_history table."""
    if not supabase_client:
        st.error("Supabase client not initialized. Cannot save prediction.")
        print("Supabase client not initialized in save_prediction_to_supabase.")
        return False

    new_entry = {
        "timestamp": datetime.now().isoformat(), # ISO format for Supabase timestamp
        "resume_name": resume_filename_str if resume_filename_str else "N/A",
        "job_title": job_title_str if job_title_str else "N/A",
        "model_used": model_used_str,
        "match_score": analysis_result_dict.get('match_score', 0),
        "skill_match_score": analysis_result_dict.get('skill_match', 0),
        "experience_match_score": analysis_result_dict.get('experience_match', 0),
        "missing_skills_count": len(analysis_result_dict.get('missing_skills', [])),
        "missing_skills_list": ", ".join(analysis_result_dict.get('missing_skills', [])), # Store as comma-separated string
        "suggestions": analysis_result_dict.get('suggestions', "")
        # 'created_at' will be handled by Supabase default value
    }
    
    try:
        response = supabase_client.table(PREDICTION_HISTORY_TABLE_NAME).insert(new_entry).execute()
        if response.data:
            print(f"Prediction history saved to Supabase successfully. ID: {response.data[0].get('id')}")
            return True
        else:
            # print(f"Failed to save prediction to Supabase. Response: {response}")
            error_message = "Unknown error."
            if hasattr(response, 'error') and response.error:
                error_message = response.error.message
            st.error(f"Failed to save prediction history to Supabase: {error_message}")
            print(f"Failed to save prediction to Supabase. Error: {error_message}, Full response: {response}")
            return False
    except Exception as e:
        st.error(f"Exception while saving prediction history to Supabase: {e}")
        print(f"Exception saving prediction to Supabase: {e}")
        return False


def run():
    st.title("👩🏻‍🎓 Applicant Portal")
    st.markdown("""
    <style>
    .big-font { font-size:22px !important; font-weight:600; }
    .small-muted { color:gray; font-size:14px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='big-font'>📄 Upload Resume & Get Matched Instantly</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Select a model to analyze your resume against the chosen job.</div>", unsafe_allow_html=True)
    st.markdown("---")


    if "job_data" not in st.session_state or not st.session_state.job_data:
        st.warning("⚠️ Please select a job from the Home page first.")
        if st.button("Go to Home Page"):
            # st.switch_page("streamlit_app.py") 
            # st.session_state["selected_page"] = HOME
            st.session_state.selected_page = HOME
            st.rerun()
                   
        return

    job_data_dict_selected = st.session_state["job_data"]

    with st.expander("📋 View Selected Job Description", expanded=True):
        st.subheader(job_data_dict_selected.get("Job Title", "N/A"))
        st.caption(f"🏢 {job_data_dict_selected.get('Company Name', 'N/A')} | 📍 {job_data_dict_selected.get('Location', 'N/A')}")
        st.markdown(f"**Experience Level:** {job_data_dict_selected.get('Experience Level', 'N/A')}")
        st.markdown(f"**Skills Required:**")
        st.markdown(f"> {job_data_dict_selected.get('Skills Required', 'N/A')}")
        st.markdown("**Full Description:**")
        st.markdown(f"> {job_data_dict_selected.get('Job Description', 'N/A')}")

    st.markdown("---")
    st.subheader("📤 Upload Your Resume & Choose Analysis Model")

    model_options_list = [MODEL_GEMINI_PRO, MODEL_LSTM_CUSTOM, MODEL_TRANSFORMER_CUSTOM, MODEL_RULE_BASED]
    model_captions_list = [
        "Advanced analysis by Google's Gemini Pro.",
        "Custom Deep Learning (LSTM) model for overall score.",
        "Custom Fine-tuned Transformer model for overall score.",
        "Basic rule-based matching for quick assessment."
    ]

    if "applicant_model_choice_v2" not in st.session_state:
        st.session_state.applicant_model_choice_v2 = MODEL_GEMINI_PRO 

    selected_model_name = st.radio(
        "🤖 Choose Analysis Model:",
        options=model_options_list,
        captions=model_captions_list,
        horizontal=False,
        index=model_options_list.index(st.session_state.applicant_model_choice_v2),
        key="model_choice_radio_applicant_v2"
    )
    st.session_state.applicant_model_choice_v2 = selected_model_name
    
    if selected_model_name == MODEL_GEMINI_PRO: st.info("Using Gemini Pro for comprehensive analysis.")
    elif selected_model_name == MODEL_LSTM_CUSTOM: st.info("LSTM model provides AI-driven overall score; detailed breakdown is rule-based.")
    elif selected_model_name == MODEL_TRANSFORMER_CUSTOM: st.info("Transformer model provides AI-driven overall score; detailed breakdown is rule-based.")
    else: st.info("Using rule-based matching for skills and experience.")


    with st.form("resume_upload_form_applicant"):
        resume_file_uploaded = st.file_uploader(
            "📁 Choose a Resume File (PDF, DOCX, DOC, TXT)",
            type=["pdf", "docx", "doc", "txt"],
            key="resume_uploader_applicant_v2"
        )
        analyze_button = st.form_submit_button("🚀 Analyze Resume")

    if analyze_button:
        if not resume_file_uploaded:
            st.warning("⚠️ Please upload a resume file.")
        else:
            st.session_state.uploaded_resume_file_applicant = resume_file_uploaded
            
            progress_bar_analysis = st.progress(0, text="Starting analysis...")
            
            with st.spinner("🔧 Parsing your resume..."):
                progress_bar_analysis.progress(25, text="🔧 Parsing resume...")
                parsed_resume_data = parse_resume(resume_file_uploaded) 
                time.sleep(0.2) 

            if not parsed_resume_data or not parsed_resume_data.get("raw_text"):
                st.error("❌ Could not parse the resume or extracted text is empty.")
                progress_bar_analysis.empty()
            else:
                with st.spinner(f"⚙️ Matching with {selected_model_name}..."):
                    progress_bar_analysis.progress(65, text=f"⚙️ Matching with {selected_model_name}...")
                    analysis_output = match_resume_to_job(
                        parsed_resume_data, 
                        job_data_dict_selected, 
                        model_choice=selected_model_name 
                    )
                    time.sleep(0.2)
                
                progress_bar_analysis.progress(100, text="✅ Analysis complete!")
                st.success("✅ Resume analysis complete!")
                st.toast("Results ready! Scroll down to view insights. 🎉")
                

                save_prediction_to_supabase(
                    resume_file_uploaded.name, 
                    job_data_dict_selected.get("Job Title", "N/A"),
                    analysis_output, 
                    selected_model_name
                )
                
                st.session_state.analysis_output_applicant = analysis_output
                st.session_state.show_applicant_results_v2 = True
                st.rerun()

    if st.session_state.get("show_applicant_results_v2", False) and "analysis_output_applicant" in st.session_state:
        analysis_output = st.session_state.analysis_output_applicant
        model_used_for_display = st.session_state.applicant_model_choice_v2

        st.markdown("---")
        st.subheader(f"📊 Match Results (using {model_used_for_display})")

        overall_score_val = analysis_output.get('match_score', 0)
        skill_score_val = analysis_output.get('skill_match', 0)
        exp_score_val = analysis_output.get('experience_match', 0)
        missing_skills_items = analysis_output.get('missing_skills', [])
        
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric("🎯 Overall Match Score", f"{overall_score_val}%", delta_color="off")
            st.progress(int(overall_score_val) / 100)
        with res_col2:
            st.metric("🛠️ Skill Match", f"{skill_score_val}%", delta_color="off")
            st.progress(int(skill_score_val) / 100)
        
        st.metric("📈 Experience Fit", f"{exp_score_val}%", delta_color="off")
        st.progress(int(exp_score_val) / 100)
            
        if missing_skills_items:
            st.warning(f"**Missing Skills ({len(missing_skills_items)}):** {', '.join(missing_skills_items)}")
        else:
            st.success("No critical skills seem to be missing based on this analysis!")

        st.markdown("---")
        st.subheader("💡 Suggestions & Insights")
        
        suggestions_text_val = analysis_output.get("suggestions")
        gemini_summary_val = analysis_output.get("gemini_suitability_summary")

        if model_used_for_display == MODEL_GEMINI_PRO and gemini_summary_val:
            with st.expander("🔍 Gemini Pro Detailed Insights", expanded=True):
                st.markdown("**Suitability Summary:**")
                st.info(gemini_summary_val)
                if suggestions_text_val:
                    st.markdown("**Suggestions for Candidate:**")
                    st.warning(suggestions_text_val)
        elif suggestions_text_val:
            st.info(f"**Suggestions:** {suggestions_text_val}")
        else:
            st.info("No specific suggestions provided by this model.")
        
        try:
            pie_values = [
                float(skill_score_val) * 0.7 if skill_score_val is not None else 0,
                float(exp_score_val) * 0.3 if exp_score_val is not None else 0
            ]
            # Ensure overall_score_val is numeric before subtraction
            overall_score_numeric = float(overall_score_val) if overall_score_val is not None else 0
            pie_values.append(max(0, 100 - overall_score_numeric))


            fig_breakdown = px.pie(
                names=["Skill Match Contribution", "Experience Match Contribution", "Gap (100 - Score)"],
                values=pie_values,
                title="Approximate Score Contribution"
            )
            st.plotly_chart(fig_breakdown, use_container_width=True)
        except ValueError:
            st.caption("Could not generate score contribution chart due to non-numeric score components.")


        if "uploaded_resume_file_applicant" in st.session_state and st.session_state.uploaded_resume_file_applicant is not None:
            with st.expander("📂 Resume Preview"):
                # Initialize session state for resume
                if "resume_ref" not in st.session_state:
                    st.session_state.resume_ref = None

                # Store resume in session state on upload
                if resume_file_uploaded:
                    st.session_state.resume_ref = resume_file_uploaded

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
                            label="📥 Download Uploaded Resume",
                            data=resume_bytes,
                            file_name=st.session_state.resume_ref.name,
                            mime=st.session_state.resume_ref.type
                        )

                    except Exception as e:
                        st.error(f"❌ Unexpected error: {e}")
                else:
                    st.info("📄 Please upload a resume to preview it here.")

        st.caption(f"Analysis performed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

