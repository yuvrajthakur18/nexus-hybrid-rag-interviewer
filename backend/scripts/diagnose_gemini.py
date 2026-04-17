import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LLM_API_KEY")
model_name = os.getenv("LLM_MODEL")

print(f"Testing Gemini Connectivity...")
print(f"Model: {model_name}")
print(f"API Key start: {api_key[:5]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say 'Hello Production'")
    print(f"SUCCESS: Response received!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"FAILURE: An error occurred.")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
