import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"API Key exists: {bool(api_key)}")
if api_key:
    # Use only the first 10 chars to avoid leaking
    print(f"Key starts with: {api_key[:10]}...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    print("Sending test request...")
    response = model.generate_content("Say 'Hello Bhavani!'")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
