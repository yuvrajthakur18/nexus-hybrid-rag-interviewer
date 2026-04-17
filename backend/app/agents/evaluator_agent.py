from app.core.gemini_client import gemini_client

class EvaluatorAgent:
    async def evaluate(self, strategy: str, rag_result: dict, sql_result: dict, query: str) -> dict:
        system_prompt = (
            "You are the Principal Lead Evaluator for an Intelligent Hybrid RAG Interviewer. "
            "Your objective is to coordinate a Factual/Structured Agent (SQL) and a Creative/Unstructured Agent (RAG). "
            "\n\nCRITICAL EVALUATION RULES:\n"
            "1. CONFLICT DETECTION: If the Creative Agent suggests something that contradicts the Technical constraints from the Factual Agent (e.g., polycount, memory), you MUST prioritize the Factual constraints.\n"
            "2. DATA SELECTION: Select only the most relevant snippets from each agent. Do not repeat raw data if it doesn't aid the design process.\n"
            "3. NO FORCED METAPHORS: Strictly avoid forcing game design metaphors or 'roleplay' analogies into factual or out-of-scope answers. Be direct and professional.\n"
            "4. SYNTHESIS: Merge the 'What' (Technical Data) with the 'How' (Design Theory) into a cohesive response that feels like a professional Senior Lead Designer providing factual, grounded advice."
        )
        
        prompt = (
            f"Candidate Query: {query}\n\n"
            f"AGENT 1 [Factual/SQL]: {sql_result.get('answer', 'No technical context available')}\n"
            f"AGENT 2 [Creative/RAG]: {rag_result.get('answer', 'No creative guidelines available')}\n\n"
            "Task: Evaluate both inputs. Identify the superior data points, resolve any contradictions, and produce a final, production-grade interview response."
        )
        
        final_answer = await gemini_client.generate_text(prompt, system_instruction=system_prompt)
        
        return {
            "answer": final_answer,
            "strategy": strategy
        }
