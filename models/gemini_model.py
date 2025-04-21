import re
import json
from config.settings import setup_gemini

def analyze_resume_with_gemini(resume_text, job_description):
    prompt = (
        "You are an expert recruiter. Given the resume and the job description below, "
        "analyze the match between the candidate and the job. Provide a match score (0-100), "
        "list the matched skills, list missing skills, and evaluate experience level fit.\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Resume:\n{resume_text}\n\n"
        "Respond with a JSON object like this:\n"
        "{\n"
        "  \"match_score\": 85,\n"
        "  \"skill_match\": 80,\n"
        "  \"experience_match\": 90,\n"
        "  \"matched_skills\": [\"Python\", \"SQL\"],\n"
        "  \"missing_skills\": [\"Docker\"]\n"
        "   \"suggestions\": \"Give some suggestions for the candidate \"\n"
        "}"
    )

    try:
        model = setup_gemini()
        response = model.generate_content(prompt)

        response_text = response.text.strip()

        # print("Gemini Response Text:", response_text)

        # Remove markdown code block syntax (e.g., ```json ... ```)
        cleaned_json = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not cleaned_json:
            raise ValueError("Gemini response does not contain valid JSON block.")

        json_str = cleaned_json.group(0)

        result = json.loads(json_str)

        # print("Gemini Response:", result)
        return result

    except Exception as e:
        print(f"Error analyzing with Gemini: {e}")
        return None
