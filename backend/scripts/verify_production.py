import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.orchestration.hybrid_orchestrator import HybridOrchestrator
from app.db.session import SessionLocal

async def benchmark():
    print("--- REAL-WORLD PRODUCTION BENCHMARK ---")
    db = SessionLocal()
    orchestrator = HybridOrchestrator(db)
    
    test_queries = [
        "What are the available game genres and character archetypes?",
        "How do I ensure visual readability for a rogue character in a chaotic match?",
        "Propose a Tank ability that protects the team without using a shield, and tell me which genres this fits best.",
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n[Test {i+1}] Query: {query}")
        start_time = time.time()
        
        try:
            result = await orchestrator.run(query)
            end_time = time.time()
            latency = (end_time - start_time)
            
            print(f"Status: SUCCESS")
            print(f"Latency: {latency:.2f}s (Requirement: <5s)")
            print(f"Strategy: {result['strategy']}")
            print(f"Answer Sample: {result['answer'][:150]}...")
            
            if latency > 5:
                print("WARNING: Latency exceeded 5 seconds!")
            else:
                print("PASSED: Latency within limits.")
                
        except Exception as e:
            print(f"Status: FAILED")
            print(f"Error: {str(e)}")
            
    db.close()

if __name__ == "__main__":
    if not os.getenv("LLM_API_KEY"):
        print("ERROR: LLM_API_KEY not found in environment. Please set it to run real benchmarks.")
        sys.exit(1)
    asyncio.run(benchmark())
