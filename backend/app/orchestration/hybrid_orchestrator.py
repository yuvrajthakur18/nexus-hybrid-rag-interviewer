import asyncio
from time import perf_counter

from sqlalchemy.orm import Session

from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.rag_agent import RAGAgent
from app.agents.sql_agent import SQLAgent
from app.db.repositories.domain_repository import DomainRepository
from app.services.prompt_builder import PromptBuilder
from app.services.query_router import QueryRouter
from app.services.retrieval_service import RetrievalService
from app.services.response_cache import ResponseCache


class HybridOrchestrator:
    cache = ResponseCache(ttl_seconds=90)

    def __init__(self, db: Session) -> None:
        self.router = QueryRouter()
        self.retrieval = RetrievalService()
        self.rag_agent = RAGAgent()
        self.sql_agent = SQLAgent(DomainRepository(db))
        self.evaluator = EvaluatorAgent()
        self.prompt_builder = PromptBuilder()

    async def run(self, query: str) -> dict:
        started = perf_counter()
        cached = self.cache.get(query.strip().lower())
        if cached:
            return {**cached, "latency_ms": round((perf_counter() - started) * 1000, 2)}

        strategy = self.router.route(query)
        limit = 3 if strategy == "structured" else 5
        
        try:
            # 1. Selective Retrieval
            if strategy == "structured":
                chunks = []
                rag_result = {"answer": "", "used_chunks": []}
            else:
                chunks, _ = await self.retrieval.semantic_search(query, limit=limit)
            
            # 2. Selective Agent Execution
            if strategy == "structured":
                sql_result = await asyncio.wait_for(self.sql_agent.answer(query), timeout=10.0)
                selected = {"answer": sql_result["answer"], "strategy": "sql"}
                rag_result = {"used_chunks": []}
            elif strategy == "unstructured":
                rag_result = await asyncio.wait_for(self.rag_agent.answer(query, chunks), timeout=10.0)
                selected = {"answer": rag_result["answer"], "strategy": "rag"}
            else:
                # Hybrid requires both
                rag_task = asyncio.create_task(self.rag_agent.answer(query, chunks))
                sql_task = asyncio.create_task(self.sql_agent.answer(query))
                rag_result, sql_result = await asyncio.gather(rag_task, sql_task)
                selected = await asyncio.wait_for(self.evaluator.evaluate(strategy, rag_result, sql_result, query), timeout=10.0)

        except Exception as e:
            selected = {"answer": f"Error in orchestration: {str(e)}", "strategy": "error"}
            rag_result = {"used_chunks": []}

        citations = self.prompt_builder.citations_from_chunks(rag_result.get("used_chunks", []))
        result = {
            "answer": selected["answer"],
            "strategy": selected.get("strategy", strategy),
            "citations": citations,
            "latency_ms": round((perf_counter() - started) * 1000, 2),
        }
        self.cache.set(query.strip().lower(), result)
        return result

    async def run_stream(self, query: str):
        started = perf_counter()
        strategy = self.router.route(query)
        
        # 1. Instant Greeting Path (Zero Latency)
        if strategy == "greeting":
            intro = "Hello! I am Nexus, your Intelligent Hybrid RAG Interviewer. I bridge the gap between creative game design theory and technical production constraints. How can I assist with your character design process today?"
            yield {"type": "metadata", "strategy": "greeting", "citations": []}
            for word in intro.split():
                 yield {"type": "content", "answer": word + " "}
                 await asyncio.sleep(0.02) 
            yield {"type": "final", "latency_ms": round((perf_counter() - started) * 1000, 2)}
            return

        # 1.5 Out-of-Scope Guardrail
        if strategy == "out_of_scope":
            refusal = "I am specialized as an Intelligent Interviewer for Video Game Character Design. I cannot assist with general programming, mathematics, or non-gaming topics. Feel free to ask me about archetypes, mechanics, or character design theory!"
            yield {"type": "metadata", "strategy": "out_of_scope", "citations": []}
            yield {"type": "thought", "message": "QueryRouter: Detected out-of-scope request. Redirecting to domain guide.", "agent": "QueryRouter"}
            for word in refusal.split():
                 yield {"type": "content", "answer": word + " "}
                 await asyncio.sleep(0.01)
            yield {"type": "final", "latency_ms": round((perf_counter() - started) * 1000, 2)}
            return

        # 2. Strategy Thought
        yield {"type": "thought", "message": f"Strategy determined: {strategy.upper()} MODE", "agent": "QueryRouter"}
        
        limit = 3 if strategy == "structured" else 5
        
        # 3. Optimized Retrieval
        if strategy != "structured":
            chunks, _ = await self.retrieval.semantic_search(query, limit=limit)
            results_msg = f"RAGAgent: Found {len(chunks)} relevant design document snippets." if chunks else "RAGAgent: No matching design documentation found. Using general knowledge."
            yield {"type": "thought", "message": results_msg, "agent": "RAGAgent"}
            
            citations_models = self.prompt_builder.citations_from_chunks(chunks)
            citations = [c.model_dump() for c in citations_models]
        else:
            chunks = []
            citations = []

        # Yield metadata early so UI can show citations/strategy
        yield {"type": "metadata", "strategy": strategy, "citations": citations}
        
        if strategy == "structured" or strategy == "hybrid":
             genres = DomainRepository(self.sql_agent.repo.db).get_genres()
             yield {"type": "thought", "message": f"SQLAgent: Retrieved {len(genres)} genres and production constraints from Neon DB.", "agent": "SQLAgent"}

        # 3. Context-Augmented Streaming Fast Path
        if strategy == "structured":
            genres = DomainRepository(self.sql_agent.repo.db).get_genres()
            archetypes = DomainRepository(self.sql_agent.repo.db).get_archetypes()
            constraints = DomainRepository(self.sql_agent.repo.db).get_constraints()
            
            context = f"Genres: {[g.name for g in genres]}, Archetypes: {[a.name for a in archetypes]}, Constraints: {constraints[0].platform if constraints else 'N/A'}"
            final_prompt = f"Based on this technical database context: {context}, answer the user: {query}"
            system_prompt = "You are a Technical Lead. Provide a precise, factual answer word by word."
        elif strategy == "unstructured":
            context = "\n".join([c["text"] for c in chunks])
            final_prompt = f"Using these design guidelines:\n{context}\n\nQuestion: {query}"
            system_prompt = "You are a Creative Director. Provide an insightful, narrative-driven answer word by word."
        else:
            genres = DomainRepository(self.sql_agent.repo.db).get_genres()
            db_context = f"Genres: {[g.name for g in genres]}"
            rag_context = "\n".join([c["text"] for c in chunks])
            final_prompt = f"DB Context: {db_context}\nRAG Guidelines: {rag_context}\n\nCombine these to answer: {query}"
            system_prompt = "You are a Principal Game Designer. Balance technical constraints with creative vision word by word."

        # 4. Stream the tokens
        full_answer = ""
        from app.core.gemini_client import gemini_client
        async for token in gemini_client.stream_generate_text(final_prompt, system_instruction=system_prompt):
            full_answer += token
            yield {"type": "content", "answer": token}

        # 5. Finalize
        yield {"type": "final", "latency_ms": round((perf_counter() - started) * 1000, 2)}
