# scripts/upload_jobs_to_supabase.py
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

try:
    from config.supabase_config import supabase_client, JOBS_TABLE_NAME 
except ImportError:
    print("Error: Could not import Supabase configuration. \n"
          "Ensure 'config.supabase_config' is accessible and SUPABASE_URL/KEY are set in .env.\n"
          "This script should ideally be run from the project root directory.")
    supabase_client = None # Ensure it's None if import fails
    JOBS_TABLE_NAME = "jobs" # Default


# print("Supabase client", supabase_client)

CSV_FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "job_dataset.csv"

def format_job_for_supabase(job_row_dict):
    """
    Formats a job dictionary from the CSV to match Supabase table schema.
    Especially handles date formatting and ensures all expected keys are present.
    """
    formatted_job = {}
    
  
    expected_columns = [
        "Job Title", "Company Name", "Job Description", "Location",
        "Job Type", "Salary Range", "Experience Level", "Skills Required",
        "Industry", "Posted Date", "Employment Mode"
    ]
    
    for col in expected_columns:
        formatted_job[col] = job_row_dict.get(col)

    # Date formatting for 'Posted Date'
    # CSV might have dates in various formats. Supabase DATE or TIMESTAMP needs 'YYYY-MM-DD' or ISO 8601.
    posted_date_str = job_row_dict.get("Posted Date")
    if posted_date_str:
        try:
            # Attempt to parse common date formats from CSV
            # Example: '4/12/2025' or '2025-04-12'
            dt_obj = pd.to_datetime(posted_date_str).date() # Convert to date object
            formatted_job["Posted Date"] = dt_obj.isoformat() # 'YYYY-MM-DD'
        except ValueError:
            print(f"Warning: Could not parse date '{posted_date_str}'. Setting to None.")
            formatted_job["Posted Date"] = None
    else:
        formatted_job["Posted Date"] = None # Handle missing dates

    # Remove 'id' if it exists in the CSV, as Supabase will generate it
    formatted_job.pop('id', None)
    
    # Ensure no NaN values are sent, convert them to None (NULL in SQL)
    for key, value in formatted_job.items():
        if pd.isna(value):
            formatted_job[key] = None
            
    return formatted_job

def upload_csv_to_supabase():
    """Reads the job_dataset.csv and uploads its content to the Supabase 'jobs' table."""
    if not supabase_client:
        print("Supabase client is not initialized. Aborting upload.")
        return

    if not CSV_FILE_PATH.exists():
        print(f"Error: CSV file not found at {CSV_FILE_PATH}")
        return

    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Successfully read {len(df)} rows from {CSV_FILE_PATH}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    successful_uploads = 0
    failed_uploads = 0

    print(f"\nStarting upload to Supabase table: '{JOBS_TABLE_NAME}'...")

    for index, row in df.iterrows():
        job_data_dict = row.to_dict()
        formatted_job_data = format_job_for_supabase(job_data_dict)
        
        print(f"  Uploading job: {formatted_job_data.get('Job Title', 'N/A Title')}...")
        
        try:

            response = supabase_client.table(JOBS_TABLE_NAME).insert(formatted_job_data).execute()
            
            # Check for errors in the response
            if hasattr(response, 'error') and response.error:
                print(f"    Error uploading job '{formatted_job_data.get('Job Title')}': {response.error.message}")
                # print(f"    Problematic data: {formatted_job_data}") 
                failed_uploads += 1
            elif response.data: # Successfully inserted
                # print(f"Successfully uploaded job ID: {response.data[0].get('id')}")
                successful_uploads += 1
            else: # No data and no explicit error - unusual, log it
                print(f"Warning: Upload for job '{formatted_job_data.get('Job Title')}' returned no data and no explicit error. Response: {response}")
                failed_uploads += 1

        except Exception as e:
            print(f"    Exception during upload for job '{formatted_job_data.get('Job Title')}': {e}")
            # print(f"Problematic data: {formatted_job_data}") 
            failed_uploads += 1
        
        # A small delay to avoid overwhelming the database or hitting rate limits
        time.sleep(0.1) 

    print("\n--- Upload Summary ---")
    print(f"Successfully uploaded: {successful_uploads} jobs.")
    print(f"Failed uploads: {failed_uploads} jobs.")
    if failed_uploads > 0:
        print("Please check the error messages above for details on failed uploads.")

if __name__ == "__main__":
    print("This script will upload data from 'job_dataset.csv' to your Supabase 'jobs' table.")
    confirmation = input("Are you sure you want to proceed? This may duplicate data if run multiple times without care. (yes/no): ")
    if confirmation.lower() == 'yes':
        upload_csv_to_supabase()
    else:
        print("Upload cancelled by user.")

