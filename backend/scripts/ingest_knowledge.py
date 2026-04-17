import asyncio
import os
import sys

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.vector_service import vector_service

KNOWLEDGE_DATA = [
    {
        "id": "gd_01",
        "text": "The 'Game Loop' is the fundamental cycle of interaction that happens many times per minute. For an Action RPG, this typically follows: Encounter -> Combat -> Reward -> Selection. Effective loops provide immediate feedback (VFX/SFX) and clear progression markers.",
        "metadata": {"source": "Game Design Theory 101", "category": "Core Loops"}
    },
    {
        "id": "gd_02",
        "text": "Character silhouettes must be unique enough to be identified in less than 200ms of visual exposure. This is known as the 'Fast Recognition' principle. Proportions, posture, and secondary motion (capes, weapons) are key to silhouette distinctness.",
        "metadata": {"source": "Art Direction Guidelines", "category": "Visual Readability"}
    },
    {
        "id": "gd_03",
        "text": "Narrative Ludonarrative Consistency: The character's abilities must reflect their backstory. If a warrior is known for their discipline, their move set should be measured and precise rather than chaotic and erratic.",
        "metadata": {"source": "Narrative Design Principles", "category": "Consistency"}
    },
    {
        "id": "gd_04",
        "text": "The 'Rule of Three' in character design suggests using three primary colors or materials to maintain visual balance. 70% should be a base color, 20% a secondary, and 10% an accent color to guide the eye.",
        "metadata": {"source": "Style Guide V1", "category": "Color Theory"}
    },
    {
        "id": "gd_05",
        "text": "Interview Tip: When asked about balancing a 'Tank', focus on Area Denial (making zones unsafe for enemies) and survivability tradeoffs. A tank that deals too much damage breaks the 'Rogue-Mage-Warrior' triangle.",
        "metadata": {"source": "Interview Prep", "category": "Career"}
    },
    {
        "id": "gd_06",
        "text": "Combat Pacing: Every attack should have three phases: Anticipation (telegraphing), Action (damage frame), and Recovery (punishment window). Balancing these frames is the difference between 'clunky' and 'fluid' combat.",
        "metadata": {"source": "Combat System Guide", "category": "Pacing"}
    }
]

async def run_ingestion():
    print("Ingesting technical game design knowledge into ChromaDB...")
    
    ids = [item["id"] for item in KNOWLEDGE_DATA]
    texts = [item["text"] for item in KNOWLEDGE_DATA]
    metadatas = [item["metadata"] for item in KNOWLEDGE_DATA]
    
    await vector_service.add_documents(texts, metadatas, ids)
    print(f"Successfully ingested {len(KNOWLEDGE_DATA)} knowledge fragments.")

if __name__ == "__main__":
    asyncio.run(run_ingestion())
