import random
import json
from models.gemini_model import analyze_resume_with_gemini

from models.custom_model_predictor import predict_with_lstm, predict_with_transformer, \
                                          load_lstm_model_and_tokenizer, load_transformer_model_and_tokenizer

from config.constants import (
    MODEL_GEMINI_PRO,
    MODEL_LSTM_CUSTOM,
    MODEL_TRANSFORMER_CUSTOM,
    MODEL_RULE_BASED
)

print("Matcher.py: Attempting to pre-load LSTM model and tokenizer...")
LOADED_LSTM_SUCCESS = load_lstm_model_and_tokenizer()
print(f"Matcher.py: LSTM pre-load status: {'Success' if LOADED_LSTM_SUCCESS else 'Failed/Not Found'}")

print("Matcher.py: Attempting to pre-load Transformer model and tokenizer...")
LOADED_TRANSFORMER_SUCCESS = load_transformer_model_and_tokenizer()
print(f"Matcher.py: Transformer pre-load status: {'Success' if LOADED_TRANSFORMER_SUCCESS else 'Failed/Not Found'}")


def match_resume_to_job(resume_data, job_data, model_choice="Rule-Based Fallback"):
    """
    Matches a resume to a job description using the selected model.

    Args:
        resume_data (dict): Parsed resume data (e.g., from resume_parser.py).
                            Expected keys: "raw_text", "skills" (list of strings), 
                                           "years_experience" (int).
        job_data (dict): Job posting data (e.g., a row from job_df.to_dict()).
                         Expected keys: "Job Description", "Skills Required" (comma-separated string),
                                        "Experience Level" (string).
        model_choice (str): The model to use for matching. 
                           Options: "Gemini Pro", "LSTM Model", "Transformer Model", "Rule-Based Fallback".

    Returns:
        dict: A dictionary containing matching results.
    """
    resume_text = resume_data.get("raw_text", "")
    # Ensure resume skills are lowercase strings in a set for _fallback_result
    resume_skills_set = set(s.lower() for s in resume_data.get("skills", [])) 
    resume_experience_parsed = resume_data.get("years_experience", 0) # Parsed years

    # Ensure job skills are lowercase strings in a set for _fallback_result
    job_skills_str = job_data.get("Skills Required", "")
    job_skills_set = set(s.strip().lower() for s in job_skills_str.split(",") if s.strip())
    job_experience_level_raw = job_data.get("Experience Level", "").lower()
    job_description_text = job_data.get("Job Description", "")

    if model_choice == MODEL_GEMINI_PRO:
        # Construct the detailed job description string for Gemini's prompt
        gemini_job_details = {
            "Job Title": job_data.get("Job Title", ""),
            "Company Name": job_data.get("Company Name", ""),
            "Job Description": job_description_text, # Core description
            "Location": job_data.get("Location", ""),
            "Experience Level": job_data.get("Experience Level", ""), # Raw string for Gemini
            "Skills Required": job_skills_str, # Raw string for Gemini
            "Industry": job_data.get("Industry", ""),
            "Employment Mode": job_data.get("Employment Mode", "")
        }
   
        gemini_response = analyze_resume_with_gemini(resume_text, gemini_job_details)

        if gemini_response and "error" not in gemini_response:
                return {
                "match_score": int(gemini_response.get("match_score", 0)),
                "skill_match": int(gemini_response.get("skill_match_score", gemini_response.get("skill_match", 0))), # Prioritize skill_match_score
                "experience_match": int(gemini_response.get("experience_match_score", gemini_response.get("experience_match", 0))),
                "missing_skills": gemini_response.get("missing_skills_from_resume", gemini_response.get("missing_skills", [])),
                "matched_skills": gemini_response.get("matched_skills", []),
                "suggestions": gemini_response.get("suggestions_for_candidate", gemini_response.get("suggestions", "Review job requirements for further alignment.")),
                "gemini_suitability_summary": gemini_response.get("suitability_summary", "")
            }
        else:
            print(f"Gemini Pro analysis failed or returned error. Response: {gemini_response}")
            # Fallback to rule-based if Gemini fails
            return _fallback_result(resume_skills_set, job_skills_set, resume_experience_parsed, job_experience_level_raw)

    elif model_choice == MODEL_LSTM_CUSTOM:
        print("Using LSTM Model for matching...")
        ml_match_score = predict_with_lstm(resume_text, job_description_text)
        if ml_match_score is not None:
            # Use ML score for overall, fallback for details
            fallback_details = _fallback_result(resume_skills_set, job_skills_set, resume_experience_parsed, job_experience_level_raw)
            fallback_details["match_score"] = int(ml_match_score) # Override with ML model's score
            fallback_details["suggestions"] = "LSTM model provided the overall score. Detailed skill/experience match is rule-based."
            return fallback_details
        else:
            print("LSTM Model prediction failed. Falling back to rule-based.")
            return _fallback_result(resume_skills_set, job_skills_set, resume_experience_parsed, job_experience_level_raw)

    elif model_choice == MODEL_TRANSFORMER_CUSTOM:
        print("Using Transformer Model for matching...")
        ml_match_score = predict_with_transformer(resume_text, job_description_text)
        if ml_match_score is not None:
            # Use ML score for overall, fallback for details
            fallback_details = _fallback_result(resume_skills_set, job_skills_set, resume_experience_parsed, job_experience_level_raw)
            fallback_details["match_score"] = int(ml_match_score) # Override with ML model's score
            fallback_details["suggestions"] = "Transformer model provided the overall score. Detailed skill/experience match is rule-based."
            return fallback_details
        else:
            print("Transformer Model prediction failed. Falling back to rule-based.")
            return _fallback_result(resume_skills_set, job_skills_set, resume_experience_parsed, job_experience_level_raw)
            
    else: # Default to MODEL_RULE_BASED (fallback)
        print(f"Model choice '{model_choice}' not fully recognized or is fallback. Using rule-based.")
        return _fallback_result(resume_skills_set, job_skills_set, resume_experience_parsed, job_experience_level_raw)



def _fallback_result(resume_skills, job_skills, resume_experience_years_parsed, job_experience_level_raw):
    """
    Generates a rule-based matching result.
    resume_experience_years_parsed: integer years extracted from resume.
    job_experience_level_raw: string like "entry", "mid", "senior" from job.
    """
    matched_skills_set = resume_skills & job_skills # Both are sets of lowercase strings
    missing_skills_set = job_skills - resume_skills

    skill_match_pct = 0
    if job_skills:
        skill_match_pct = int((len(matched_skills_set) / len(job_skills)) * 100)
    
    # Experience matching logic (can be refined)
    job_exp_numeric_min = 0
    if "entry" in job_experience_level_raw: job_exp_numeric_min = 0
    elif "mid" in job_experience_level_raw: job_exp_numeric_min = 2 # e.g., Mid-level might expect 2-5 years
    elif "senior" in job_experience_level_raw: job_exp_numeric_min = 5 # e.g., Senior might expect 5+ years

    experience_match_pct = 0
    if resume_experience_years_parsed >= job_exp_numeric_min:
        experience_match_pct = 100
    elif job_exp_numeric_min > 0 and resume_experience_years_parsed > 0:
        experience_match_pct = int((resume_experience_years_parsed / job_exp_numeric_min) * 70)
        experience_match_pct = max(0, min(experience_match_pct, 80)) # Cap at 80%
    elif job_exp_numeric_min == 0 and resume_experience_years_parsed == 0:
        experience_match_pct = 100 # Entry level job, no experience resume = good fit for exp
    elif job_exp_numeric_min == 0 and resume_experience_years_parsed > 0:
        experience_match_pct = 100 # Entry level job, some experience is fine
    else: # job_exp_numeric_min > 0 and resume_experience_years_parsed == 0
        experience_match_pct = 10 # No experience for a job requiring some

    # Calculate overall match score (weighted)
    # Ensure skill_match_pct and experience_match_pct are within 0-100
    skill_match_pct = max(0, min(skill_match_pct, 100))
    experience_match_pct = max(0, min(experience_match_pct, 100))

    overall_match_score = int(0.7 * skill_match_pct + 0.3 * experience_match_pct)
    overall_match_score = min(max(overall_match_score, 0), 100) # Ensure 0-100

    return {
        "match_score": overall_match_score,
        "skill_match": skill_match_pct,
        "experience_match": experience_match_pct,
        "missing_skills": list(missing_skills_set), # Convert set to list for JSON/CSV
        "matched_skills": list(matched_skills_set),
        "suggestions": "Consider highlighting transferable skills or gaining experience in missing areas."
    }
