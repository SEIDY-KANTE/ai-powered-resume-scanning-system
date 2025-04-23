import re
import json
from config.settings import setup_gemini

def analyze_resume_with_gemini(resume_text, job_description):
    prompt = (

        "As an expert talent acquisition specialist, your task is to meticulously analyze a candidate's resume against a given job description. "
        "Your goal is to determine the overall suitability of the candidate for the role and provide specific insights to support this assessment.\n\n"
        "Consider the following aspects in your analysis:\n"
        "- **Skill Match:** Identify both explicitly stated skills and implicitly demonstrated capabilities within the resume that align with the requirements of the job description. **Crucially, recognize that variations in skill phrasing, abbreviations, and common alternative names should be treated as the same skill.** For example, 'ReactJS', 'React JS', and 'React' should all be considered matches for the core React skill. Similarly, 'Node.js', 'NodeJS', and 'Node JS' are equivalent.\n"
        "- **Experience Level:** Evaluate if the candidate's described experience, including the duration and scope of their roles, aligns with the expected experience level for this position.\n"
        "- **Overall Fit:** Synthesize your analysis of skills and experience to provide an overall match score.\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Resume:\n{resume_text}\n\n"
        "Based on your analysis, please provide a JSON object with the following structure:\n"
        "{\n"
        '  "match_score": (integer between 0 and 100 representing the overall fit),\n'
        '  "skill_match": (integer between 0 and 100 representing the degree of skill alignment),\n'
        '  "experience_match": (integer between 0 and 100 representing the alignment of experience level),\n'
        '  "matched_skills": ["list", "of", "core", "skills", "found", "in", "the", "resume", "that", "match", "the", "job", "description", "(e.g., React, Python, SQL)"],\n'
        '  "missing_skills": ["list", "of", "key", "core", "skills", "mentioned", "in", "the", "job", "description", "but", "not", "found", "in", "the", "resume", "(e.g., Docker, Kubernetes)"],\n'
        '  "suggestions": "(Provide 1-2 concise and actionable suggestions for the candidate to improve their resume or skills to better align with similar roles. Tailor the language of the suggestions to the job description or the candidate\'s background.)"\n'
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
