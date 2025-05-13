import re
import json
from config.settings import setup_gemini 

def analyze_resume_with_gemini(resume_text_input, job_details_dict_input):
    """
    Analyzes a resume against a job description using the Gemini Pro model.

    Args:
        resume_text_input (str): The raw text of the resume.
        job_details_dict_input (dict): A dictionary containing detailed job information.
                                      Expected keys match those used in the notebook's
                                      Gemini prompt construction (e.g., "Job Title", 
                                      "Job Description", "Skills Required", etc.).
    Returns:
        dict: A dictionary containing the analysis from Gemini, or an error dictionary.
    """
    try:
        # Initialize the Gemini model instance
        model_instance = setup_gemini() 
        if not model_instance:
            return {"error": "Gemini model could not be initialized via setup_gemini().", "raw_response": ""}

    except Exception as e_setup:
        print(f"Error during Gemini setup in analyze_resume_with_gemini: {e_setup}")
        return {"error": f"Gemini setup failed: {e_setup}", "raw_response": ""}

    # Construct the job description prompt text
    job_description_prompt_text = f"""
    Job Title: {job_details_dict_input.get("Job Title", "N/A")}
    Company: {job_details_dict_input.get("Company Name", "N/A")}
    Full Job Description: {job_details_dict_input.get("Job Description", "N/A")}
    Location: {job_details_dict_input.get("Location", "N/A")}
    Experience Level Required: {job_details_dict_input.get("Experience Level", "N/A")}
    Skills Required: {job_details_dict_input.get("Skills Required", "N/A")}
    Industry: {job_details_dict_input.get("Industry", "N/A")}
    Employment Mode: {job_details_dict_input.get("Employment Mode","N/A")}
    """

    prompt = (
        "You are an expert Talent Acquisition Specialist and Resume Analyzer AI. "
        "Your task is to meticulously analyze the candidate's resume against the provided job description. "
        "Provide a comprehensive evaluation focusing on skill alignment, experience relevance, and overall suitability. "
        "Recognize skill variations (e.g., ReactJS, React JS, React are the same; Node.js, NodeJS are the same). "
        "The primary output should be a JSON object.\n\n"
        f"Job Description Details:\n{job_description_prompt_text}\n\n"
        f"Candidate's Resume:\n{resume_text_input}\n\n"
        "Based on your analysis, provide a JSON object with the following structure. Ensure all percentage scores are integers between 0 and 100. "
        "The 'match_score' should be your primary overall assessment. "
        "Be realistic and critical in your assessment.\n"
        "{\n"
        '  "match_score": (integer, 0-100, overall fit of resume to job description),\n'
        '  "skill_match_score": (integer, 0-100, degree of skill alignment),\n' 
        '  "experience_match_score": (integer, 0-100, alignment of experience level and relevance),\n' 
        '  "identified_candidate_skills": ["list", "of", "key", "skills", "found", "in", "resume", "relevant", "to", "job"],\n'
        '  "required_skills_from_jd": ["list", "of", "key", "skills", "explicitly", "or", "implicitly", "required", "by", "job"],\n'
        '  "matched_skills": ["list", "of", "skills", "common", "to", "both", "resume", "and", "job", "requirements"],\n' 
        '  "missing_skills_from_resume": ["list", "of", "key", "skills", "from", "job", "description", "NOT", "found", "in", "resume"],\n' 
        '  "candidate_experience_summary": "(Brief text summary of candidate experience relevant to the role, e.g., X years in Y field, key achievements related to job.)",\n'
        '  "job_experience_requirement_summary": "(Brief text summary of experience required by the job, e.g., Y-Z years in X technology, specific types of projects.)",\n'
        '  "suitability_summary": "(CONCISE text summary: overall fit, key strengths, and critical weaknesses against the JD. Be specific.)",\n' 
        '  "suggestions_for_candidate": "(1-2 actionable text suggestions for candidate to improve profile for THIS or similar roles. Be specific.)"\n' 
        "}"
    )

    try:
        response = model_instance.generate_content(prompt)
        if not response.parts:
            print("Gemini response has no parts.")
            return {"error": "Gemini response has no parts", "raw_response": str(response)}
        
        response_text = ""
        for part in response.parts:
            try:
                response_text += part.text
            except ValueError:
                print(f"Skipping a non-text part in Gemini response: {type(part)}")
                continue
        
        response_text = response_text.strip()
        if not response_text:
            print("Gemini response text is empty after stripping.")
            return {"error": "Empty response text from Gemini", "raw_response": str(response)}


        json_block_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        json_str = ""
        if json_block_match:
            json_str = json_block_match.group(1)
        else:
            first_brace = response_text.find('{')
            last_brace = response_text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = response_text[first_brace : last_brace+1]
            else:
                print("Gemini response does not contain a recognizable JSON block.")
                # print("Raw Gemini Response (for debugging JSON extraction):", response_text)
                return {"error": "Invalid JSON response structure from Gemini", "raw_response": "Response did not contain JSON block."}
        
        result = json.loads(json_str)
        return result

    except json.JSONDecodeError as json_e:
        print(f"Error decoding JSON from Gemini response: {json_e}")
        problematic_json_str = json_str if 'json_str' in locals() and json_str else "Not extracted or empty"
        print("Problematic JSON string attempt:", problematic_json_str)
        # print("Full Raw Gemini Response (on JSON error):", response_text if 'response_text' in locals() else "No response text")
        return {"error": f"JSONDecodeError: {json_e}", "raw_response": "JSON decoding failed."}
    except Exception as e:
        print(f"An unexpected error occurred in analyze_resume_with_gemini: {e}")
        # raw_resp_text_on_error = response.text if 'response' in locals() and hasattr(response, 'text') else "No response object or text attribute"
        return {"error": f"Unexpected error: {e}", "raw_response": "Unexpected error during Gemini call."}