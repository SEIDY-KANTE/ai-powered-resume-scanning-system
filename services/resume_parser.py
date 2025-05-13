import docx2txt
import pdfplumber
import re
import io
from .job_service import get_all_skills


SKILLS = get_all_skills()


def extract_text(file):
    if file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        return docx2txt.process(file)
    else:
        return ""

def extract_skills(text):
    words = set(re.findall(r'\b\w+\b', text))
    found_skills = [skill for skill in SKILLS if skill.lower() in [w.lower() for w in words]]
    return list(set(found_skills))

def extract_experience(text):
    # Look for patterns like "X years of experience" or similar
    patterns = [
        r"(\d+)\+?\s+years? of experience",
        r"experience\s+of\s+(\d+)\s+years",
        r"worked\s+for\s+(\d+)\s+years"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0

def parse_resume(resume_file):
    text = extract_text(resume_file)

    return {
        "raw_text": text,
        "skills": extract_skills(text),
        "years_experience": extract_experience(text),
    }

