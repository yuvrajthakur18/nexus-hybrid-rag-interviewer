import httpx
from app.core.config import settings

class GeminiClient:
    def __init__(self):
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is not set in environment or config")
        self.api_key = settings.llm_api_key
        self.model_name = settings.llm_model or "gemini-1.5-flash"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    async def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}?key={self.api_key}",
                    json=payload
                )
                
                if response.status_code != 200:
                    return f"Error from Gemini API ({response.status_code}): {response.text}"
                
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    parts = data["candidates"][0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                
                return f"Unexpected response format from Gemini: {str(data)}"
                
        except Exception as e:
            return f"Exception in GeminiClient: {str(e)}"

    async def generate_structured(self, prompt: str, system_instruction: str = None) -> str:
        # For production-grade structured output, we use the prompt to enforce JSON
        if system_instruction:
             system_instruction += "\nOutput your answer strictly in valid JSON format."
        else:
             system_instruction = "Output your answer strictly in valid JSON format."
        return await self.generate_text(prompt, system_instruction)

    async def stream_generate_text(self, prompt: str, system_instruction: str = None):
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.2, "topK": 40, "topP": 0.95, "maxOutputTokens": 1024}
            }
            
            # SSE streaming mode
            stream_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:streamGenerateContent?alt=sse&key={self.api_key}"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", stream_url, json=payload) as response:
                    if response.status_code != 200:
                        yield f"Error ({response.status_code}): {await response.aread()}"
                        return

                    import json
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if "candidates" in data and data["candidates"]:
                                    chunk = data["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                    if chunk:
                                        yield chunk
                            except Exception:
                                continue
        except Exception as e:
            yield f"Stream Exception: {str(e)}"

gemini_client = GeminiClient()
