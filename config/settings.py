from dotenv import load_dotenv
import google.generativeai as genai
import os


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# Set up Gemini API
def setup_gemini(api_key=None):
    api_key = api_key or GEMINI_API_KEY
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-002"
    )
    
    return model
