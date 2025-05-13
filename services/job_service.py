import pandas as pd
from datetime import datetime
from config.supabase_config import supabase_client, JOBS_TABLE_NAME 
from config.constants import COMMON_SKILLS



def load_jobs() -> pd.DataFrame:
    """Load job postings from Supabase."""
    if not supabase_client:
        print("Supabase client not initialized. Cannot load jobs.")
        return pd.DataFrame() # Return empty DataFrame

    try:
        response = supabase_client.table(JOBS_TABLE_NAME).select("*").order("created_at", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Convert 'posted_date' if it's a string, Supabase might return ISO format
            if 'posted_date' in df.columns:
                df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            return df
        else:
            print("No data found in jobs table or error in response.")
            # print("Supabase response:", response) 
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading jobs from Supabase: {e}")
        return pd.DataFrame()

def add_job(job_dict: dict) -> bool:
    """Add a new job posting to Supabase.
    Returns True if successful, False otherwise.
    """
    if not supabase_client:
        print("Supabase client not initialized. Cannot add job.")
        return False
    

    try:
        # Remove 'id' if present, as Supabase handles it
        job_dict.pop('id', None) 
        
        response = supabase_client.table(JOBS_TABLE_NAME).insert(job_dict).execute()
        if response.data: # Check if data is returned on success
            print(f"Job added successfully to Supabase: {response.data[0]['id']}")
            return True
        else:
            # print(f"Failed to add job. Supabase response: {response}") 
            if hasattr(response, 'error') and response.error:
                 print(f"Failed to add job. Error: {response.error.message}")
            else:
                 print(f"Failed to add job. No data returned in response. Full response: {response}")
            return False
    except Exception as e:
        print(f"Error adding job to Supabase: {e}")
        return False

def update_job(job_id: int, updated_job_data: dict) -> bool:
    """Update a job in Supabase by its ID.
    Returns True if successful, False otherwise.
    """
    if not supabase_client:
        print("Supabase client not initialized. Cannot update job.")
        return False

    try:
        # Remove 'id' from updated_job_data if it's there, as it's used for matching
        updated_job_data.pop('id', None)
        
        response = supabase_client.table(JOBS_TABLE_NAME).update(updated_job_data).eq("id", job_id).execute()
        if response.data:
            print(f"Job with ID {job_id} updated successfully in Supabase.")
            return True
        else:
            if hasattr(response, 'error') and response.error:
                 print(f"Failed to update job {job_id}. Error: {response.error.message}")
            elif len(response.data) == 0: # No rows matched the ID, or no change made
                 print(f"Failed to update job {job_id}. No matching record found or no data changed.")
            else:
                 print(f"Failed to update job {job_id}. Response: {response}")
            return False
    except Exception as e:
        print(f"Error updating job {job_id} in Supabase: {e}")
        return False

def delete_job(job_id: int) -> bool:
    """Delete a job posting from Supabase by its ID.
    Returns True if successful, False otherwise.
    """
    if not supabase_client:
        print("Supabase client not initialized. Cannot delete job.")
        return False
    try:
        response = supabase_client.table(JOBS_TABLE_NAME).delete().eq("id", job_id).execute()
        if response.data:
            print(f"Job with ID {job_id} deleted successfully from Supabase.")
            return True
        else:
            if hasattr(response, 'error') and response.error:
                 print(f"Failed to delete job {job_id}. Error: {response.error.message}")
            elif len(response.data) == 0: # No rows matched the ID
                 print(f"Failed to delete job {job_id}. No matching record found.")
            else:
                 print(f"Failed to delete job {job_id}. Response: {response}")
            return False
    except Exception as e:
        print(f"Error deleting job {job_id} from Supabase: {e}")
        return False

def get_job_by_id(job_id: int) -> dict | None:
    """Fetch a single job by its ID from Supabase."""
    if not supabase_client:
        print("Supabase client not initialized. Cannot get job by ID.")
        return None
    try:
        response = supabase_client.table(JOBS_TABLE_NAME).select("*").eq("id", job_id).single().execute()
        if response.data:
            return response.data
        else:
            # print(f"Job with ID {job_id} not found. Response: {response}") 
            return None
    except Exception as e:
        print(f"Error fetching job {job_id} by ID: {e}")
        return None

def get_all_skills() -> list:
    """
    Load all unique skills from the 'Skills Required' column in the Supabase jobs table
    and combine them with a predefined set of common skills.
    """
    df = load_jobs() # Loads from Supabase
    
    all_skills_set = set(s.lower() for s in COMMON_SKILLS)

    if "Skills Required" not in df.columns or df.empty:
        print("No 'Skills Required' column found in jobs data or no jobs loaded. Using only common skills.")
        return list(all_skills_set)

    for skills_entry in df["Skills Required"].dropna():
        for skill in str(skills_entry).split(","):
            cleaned_skill = skill.strip().lower()
            if cleaned_skill: 
                all_skills_set.add(cleaned_skill)
                
    return list(all_skills_set)

# Functions like format_job_short and truncate_description can remain as they are,
# as they operate on DataFrame rows or strings, independent of data source.
def format_job_short(job_row: pd.Series) -> str:
    """Return a short markdown string for the job preview."""
    # Ensure keys exist in the Series, providing defaults if not
    title = job_row.get('Job Title', 'N/A')
    company = job_row.get('Company Name', 'N/A')
    location = job_row.get('Location', 'N/A')
    job_type = job_row.get('Job Type', 'N/A')
    experience = job_row.get('Experience Level', 'N/A')
    salary = job_row.get('Salary Range', 'N/A')
    posted_date_val = job_row.get('posted_date', 'N/A') 

    return f"""
**{title}** 🏢 {company} | 📍 {location} | 💼 {job_type}  
🧠 *{experience}* | 💵 {salary}  
📅 {posted_date_val}
"""

def truncate_description(desc: str, limit: int = 200) -> str:
    return desc[:limit] + "..." if len(desc) > limit else desc