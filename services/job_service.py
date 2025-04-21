import pandas as pd
from pathlib import Path
from datetime import datetime

JOB_CSV_PATH = Path("../data/job_dataset.csv")

JOB_FIELDS = [
    "Job Title", "Company Name", "Job Description", "Location",
    "Job Type", "Salary Range", "Experience Level", "Skills Required",
    "Industry", "Posted Date", "Employment Mode"
]

def load_jobs() -> pd.DataFrame:
    """Load job postings from CSV."""
    if JOB_CSV_PATH.exists():
        return pd.read_csv(JOB_CSV_PATH)
    return pd.DataFrame(columns=JOB_FIELDS)

def save_jobs(df: pd.DataFrame) -> None:
    """Save the DataFrame to the CSV."""
    df.to_csv(JOB_CSV_PATH, index=False)

def add_job(job_dict: dict) -> pd.DataFrame:
    """Add a new job posting to the dataset."""
    df = load_jobs()
    new_job = pd.DataFrame([job_dict], columns=JOB_FIELDS)
    df = pd.concat([df, new_job], ignore_index=True)
    save_jobs(df)
    return df

def update_job(index: int, updated_job: dict) -> pd.DataFrame:
    """Update a job at a specific index."""
    df = load_jobs()
    for key in JOB_FIELDS:
        df.at[index, key] = updated_job.get(key, df.at[index, key])
    save_jobs(df)
    return df

def delete_job(index: int) -> pd.DataFrame:
    """Delete a job posting by index."""
    df = load_jobs()
    df = df.drop(index=index).reset_index(drop=True)
    save_jobs(df)
    return df

def format_job_short(job_row: pd.Series) -> str:
    """Return a short markdown string for the job preview."""
    return f"""
**{job_row['Job Title']}**  
🏢 {job_row['Company Name']} | 📍 {job_row['Location']} | 💼 {job_row['Job Type']}  
🧠 *{job_row['Experience Level']}* | 💵 {job_row['Salary Range']}  
📅 {job_row['Posted Date']}  
"""

def truncate_description(desc: str, limit: int = 200) -> str:
    return desc[:limit] + "..." if len(desc) > limit else desc


COMMON_SKILLS = {
    "Python", "Java", "SQL", "Excel", "Communication", "Project Management", "Machine Learning",
    "Data Analysis", "Leadership", "Problem Solving", "AWS", "Docker", "Kubernetes", "C++", "TensorFlow"
}
def get_all_skills():
    df = load_jobs()
    if "Skills Required" not in df.columns or df.empty:
        print("No skills found in the dataset.")
        return set()

    all_skills = set()
    for skills in df["Skills Required"].dropna():
        for skill in str(skills).split(","):
            all_skills.add(skill.strip().lower())
            
    all_skills.update(COMMON_SKILLS)

    # to list
    all_skills = list(all_skills)

    # print(f"Extracted {len(all_skills)} unique skills from the dataset.")
    # print(all_skills)

    return all_skills