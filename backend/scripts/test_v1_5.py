import os
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio

load_dotenv()
api_key = os.getenv("LLM_API_KEY")

async def test_v1_5():
    print("Testing Gemini 1.5 Flash (Legacy Stable)...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Run in a thread to handle potential SDK hangs
        response = await asyncio.to_thread(model.generate_content, "Say 'Hello Stable'")
        print(f"SUCCESS: {response.text}")
    except Exception as e:
        print(f"FAILURE: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_v1_5())
