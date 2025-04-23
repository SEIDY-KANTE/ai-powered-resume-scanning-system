import random
import json
from models.gemini_model import analyze_resume_with_gemini

def match_resume_to_job(resume_data, job_data, model="My Custom Model"):
    job_skills = set(map(str.strip, job_data.get("Skills Required", "").lower().split(",")))
    job_experience = job_data.get("Experience Level", "").lower()

    resume_skills = set(map(str.strip, resume_data.get("skills", [])))
    resume_experience = resume_data.get("experience_level", "").lower()
    resume_text = resume_data.get("raw_text", "")

    if model == "Gemini Pro":
        # Build a plain job description string
        job_description = f"""
        Job Title: {job_data.get("Job Title", "")}
        Company: {job_data.get("Company Name", "")}
        Description: {job_data.get("Job Description", "")}
        Location: {job_data.get("Location", "")}
        Experience Level: {job_experience}
        Skills Required: {', '.join(job_skills)}
        """

        gemini_response = analyze_resume_with_gemini(resume_text, job_description)

        if gemini_response:
            try:
                # gemini_data = json.loads(gemini_response)
                gemini_data = gemini_response


                # print("Gemini Data:", gemini_data)

                return {
                    "match_score": min(int(gemini_data.get("match_score", 0)), 100),
                    "skill_match": int(gemini_data.get("skill_match", 0)),
                    "experience_match": int(gemini_data.get("experience_match", 0)),
                    "missing_skills": gemini_data.get("missing_skills", []),
                    "Suggestions": str(gemini_data.get("suggestions")),
                }
            except json.JSONDecodeError:
                return _fallback_result(resume_skills, job_skills, resume_experience, job_experience)
            

        print("Gemini response was not valid JSON. Falling back to custom model.")

        # Fallback if Gemini failed
        return _fallback_result(resume_skills, job_skills, resume_experience, job_experience)

    else:
        return _fallback_result(resume_skills, job_skills, resume_experience, job_experience)


def _fallback_result(resume_skills, job_skills, resume_experience, job_experience):
    matched_skills = resume_skills & job_skills
    missing_skills = job_skills - resume_skills

    skill_match_pct = int((len(matched_skills) / len(job_skills)) * 100) if job_skills else 0
    experience_match_pct = 100 if job_experience in resume_experience else 60

    match_score = int(0.7 * skill_match_pct + 0.3 * experience_match_pct)

    return {
        "match_score": min(match_score, 100),
        "skill_match": skill_match_pct,
        "experience_match": experience_match_pct,
        "missing_skills": list(missing_skills),
        "Suggestions": None,
    }
