from app.core.gemini_client import gemini_client

class RAGAgent:
    async def answer(self, query: str, chunks: list[dict]) -> dict:
        if not chunks:
            return {"answer": "I don't have enough specific creative guidelines to answer that fully.", "confidence": 0.0, "used_chunks": []}
        
        context = "\n".join([f"- {c['text']}" for c in chunks])
        system_prompt = (
            "You are a Senior Video Game Character Designer Interviewer. "
            "Your goal is to evaluate the candidate's creative reasoning based on established design principles. "
            "Use the provided context to ground your answer, but maintain a professional, interrogative tone."
        )
        
        prompt = (
            f"Context from design guidelines:\n{context}\n\n"
            f"Candidate Question/Statement: {query}\n\n"
            "Generate a response that uses the context to provide an insightful design-focused answer or follow-up question."
        )
        
        answer = await gemini_client.generate_text(prompt, system_instruction=system_prompt)
        
        return {
            "answer": answer,
            "confidence": 0.9,
            "used_chunks": chunks
        }
