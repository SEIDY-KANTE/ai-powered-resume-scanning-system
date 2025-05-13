import streamlit as st
from datetime import date, datetime 
from services import job_service 
import pandas as pd 


def run():
    st.title("🧑‍💼 HR Portal: Manage Job Postings")
    st.markdown("Add, view, edit, and delete job postings directly in the database.")
    st.markdown("---")

    # === Add New Job Form ===
    with st.expander("➕ Add New Job Posting", expanded=False):
        with st.form("add_job_form_hr"): # Unique form key
            st.subheader("📋 Enter Job Details")
            
            # Using a dictionary to collect form data easily
            new_job_data = {}
            new_job_data["Job Title"] = st.text_input("Job Title")
            new_job_data["Company Name"] = st.text_input("Company Name")
            new_job_data["Job Description"] = st.text_area("Job Description", height=150)
            new_job_data["Location"] = st.text_input("Location (e.g., City, Country)")
            
            cols_type_mode_exp = st.columns(3)
            with cols_type_mode_exp[0]:
                new_job_data["Job Type"] = st.selectbox("Job Type", ["Full-time", "Part-time", "Internship", "Contract", "Temporary"], key="add_job_type")
            with cols_type_mode_exp[1]:
                new_job_data["Employment Mode"] = st.selectbox("Employment Mode", ["Remote", "On-site", "Hybrid"], key="add_emp_mode")
            with cols_type_mode_exp[2]:
                new_job_data["Experience Level"] = st.selectbox("Experience Level", ["Entry", "Mid", "Senior", "Lead", "Principal"], key="add_exp_level")

            new_job_data["Salary Range"] = st.text_input("Salary Range (e.g., $70,000 - $100,000 per year)")
            new_job_data["Skills Required"] = st.text_area("Required Skills (comma-separated, e.g., Python, SQL, Data Analysis)")
            new_job_data["Industry"] = st.text_input("Industry (e.g., Technology, Healthcare, Finance)")
            
            # Ensure 'Posted Date' is a string in 'YYYY-MM-DD' format for Supabase
            posted_date_obj = st.date_input("Posted Date", value=date.today(), key="add_posted_date")
            new_job_data["Posted Date"] = posted_date_obj.isoformat()


            add_job_submitted = st.form_submit_button("✅ Add Job Posting")
            
            if add_job_submitted:
                # Basic validation (optional, but recommended)
                if not all([new_job_data["Job Title"], new_job_data["Company Name"], new_job_data["Job Description"], new_job_data["Skills Required"]]):
                    st.error("🚨 Please fill in all essential fields (Job Title, Company, Description, Skills).")
                else:
                    with st.spinner("Adding job to the database..."):
                        success = job_service.add_job(new_job_data) # add_job now expects a dict
                    if success:
                        st.success(f"✅ Job '{new_job_data['Job Title']}' added successfully!")
                        st.balloons()
                        # Consider clearing form or collapsing expander if needed, st.rerun() will refresh data
                        st.rerun() 
                    else:
                        st.error("❌ Failed to add job. Please check console logs or try again.")

    st.markdown("---")
    st.subheader("📄 Existing Job Postings")
    
    # Load jobs from Supabase via job_service
    job_df = job_service.load_jobs()

    if job_df.empty:
        st.info("No job postings found in the database. Add one using the form above.")
    else:
        st.info(f"Displaying {len(job_df)} job postings from the database.")
        
        # Display jobs in a more structured way, perhaps with a few columns for key info before expanding
        for _ , job_row_series in job_df.iterrows(): # _ is the pandas index, job_row_series has the data
            # IMPORTANT: Use the 'id' from the database for operations, not the pandas index.
            db_job_id = job_row_series.get('id') 
            if db_job_id is None:
                st.warning(f"Job missing 'id', cannot be edited/deleted. Data: {job_row_series.to_dict()}")
                continue

            expander_title = f"ID: {db_job_id} - {job_row_series.get('Job Title', 'N/A')} at {job_row_series.get('Company Name', 'N/A')}"
            
            with st.expander(expander_title):
                # Use a unique key for each form based on the database job ID
                with st.form(f"edit_job_form_{db_job_id}"):
                    st.subheader(f"Edit Job ID: {db_job_id}")
                    
                    edited_job_data = {} # To store edited values

                    # Create form fields, pre-filled with existing data
                    # Column names must match your Supabase table
                    edited_job_data["Job Title"] = st.text_input("Job Title", value=job_row_series.get("Job Title", ""), key=f"title_{db_job_id}")
                    edited_job_data["Company Name"] = st.text_input("Company Name", value=job_row_series.get("Company Name", ""), key=f"company_{db_job_id}")
                    edited_job_data["Job Description"] = st.text_area("Job Description", value=job_row_series.get("Job Description", ""), height=150, key=f"desc_{db_job_id}")
                    edited_job_data["Location"] = st.text_input("Location", value=job_row_series.get("Location", ""), key=f"loc_{db_job_id}")

                    edit_cols1 = st.columns(3)
                    with edit_cols1[0]:
                        job_type_options = ["Full-time", "Part-time", "Internship", "Contract", "Temporary"]
                        current_job_type_idx = job_type_options.index(job_row_series.get("Job Type")) if job_row_series.get("Job Type") in job_type_options else 0
                        edited_job_data["Job Type"] = st.selectbox("Job Type", job_type_options, index=current_job_type_idx, key=f"type_{db_job_id}")
                    with edit_cols1[1]:
                        emp_mode_options = ["Remote", "On-site", "Hybrid"]
                        current_emp_mode_idx = emp_mode_options.index(job_row_series.get("Employment Mode")) if job_row_series.get("Employment Mode") in emp_mode_options else 0
                        edited_job_data["Employment Mode"] = st.selectbox("Employment Mode", emp_mode_options, index=current_emp_mode_idx, key=f"mode_{db_job_id}")
                    with edit_cols1[2]:
                        exp_level_options = ["Entry", "Mid", "Senior", "Lead", "Principal"]
                        current_exp_level_idx = exp_level_options.index(job_row_series.get("Experience Level")) if job_row_series.get("Experience Level") in exp_level_options else 0
                        edited_job_data["Experience Level"] = st.selectbox("Experience Level", exp_level_options, index=current_exp_level_idx, key=f"exp_{db_job_id}")
                    
                    edited_job_data["Salary Range"] = st.text_input("Salary Range", value=job_row_series.get("Salary Range", ""), key=f"salary_{db_job_id}")
                    edited_job_data["Skills Required"] = st.text_area("Required Skills", value=job_row_series.get("Skills Required", ""), key=f"skills_{db_job_id}")
                    edited_job_data["Industry"] = st.text_input("Industry", value=job_row_series.get("Industry", ""), key=f"industry_{db_job_id}")
                    
                    # Handle 'Posted Date'
                    # job_service.load_jobs now formats it to 'YYYY-MM-DD' string
                    try:
                        current_posted_date = datetime.strptime(job_row_series.get("posted_date"), '%Y-%m-%d').date() \
                                            if job_row_series.get("posted_date") else date.today()
                    except (ValueError, TypeError): # Handle cases where date might be missing or in wrong format
                        current_posted_date = date.today()
                    
                    edited_posted_date_obj = st.date_input("Posted Date", value=current_posted_date, key=f"date_{db_job_id}")
                    edited_job_data["Posted Date"] = edited_posted_date_obj.isoformat()

                    # Form submission buttons
                    form_cols = st.columns(2)
                    with form_cols[0]:
                        save_changes_submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
                    with form_cols[1]:
                        delete_job_submitted = st.form_submit_button("❌ Delete Job", type="secondary", use_container_width=True)

                    if save_changes_submitted:
                        with st.spinner(f"Updating Job ID: {db_job_id}..."):
                            # Pass the actual database job ID for update
                            success = job_service.update_job(db_job_id, edited_job_data)
                        if success:
                            st.success(f"✅ Job ID: {db_job_id} updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to update Job ID: {db_job_id}. Check logs.")
                    
                    if delete_job_submitted:
                        # Confirmation for delete 
                        if st.checkbox(f"Confirm deletion of Job ID {db_job_id}", key=f"confirm_delete_{db_job_id}"):
                            with st.spinner(f"Deleting Job ID: {db_job_id}..."):
                                # Pass the actual database job ID for deletion
                                success = job_service.delete_job(db_job_id)
                            if success:
                                st.warning(f"🗑️ Job ID: {db_job_id} deleted.")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete Job ID: {db_job_id}. Check logs.")
                        else:
                            st.info("Deletion not confirmed.")
