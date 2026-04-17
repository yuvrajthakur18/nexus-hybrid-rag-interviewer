from app.db.repositories.domain_repository import DomainRepository
from app.core.gemini_client import gemini_client

class SQLAgent:
    def __init__(self, repo: DomainRepository) -> None:
        self.repo = repo

    async def answer(self, query: str) -> dict:
        genres = self.repo.get_genres()
        archetypes = self.repo.get_archetypes()
        constraints = self.repo.get_constraints()
        skill_trees = self.repo.get_skill_trees()
        stat_systems = self.repo.get_stat_systems()
        
        # Prepare data context for Gemini
        data_context = "Relational Data Summary:\n"
        if genres:
            data_context += "- Available Genres: " + ", ".join(g.name for g in genres) + "\n"
        if archetypes:
            data_context += "- Character Archetypes: " + ", ".join(a.name for a in archetypes) + "\n"
        if skill_trees:
            data_context += "- Mechanical Skill Trees:\n"
            for st in skill_trees:
                data_context += f"  * {st.name}: Nodes include {st.nodes}\n"
        if stat_systems:
            data_context += "- Stat Systems:\n"
            for ss in stat_systems:
                data_context += f"  * {ss.system_name}: Stats: {ss.primary_stats}\n"
        if constraints:
            c = constraints[0]
            data_context += f"- Active Production Constraints: {c.platform}, Memory: {c.memory_budget_mb}MB, Timeline: {c.timeline_weeks}w, Polycount: {c.max_asset_polycount}\n"
        
        system_prompt = (
            "You are a factual data agent for a Video Game Character Designer Interviewer. "
            "Your job is to provide structured information based on the relational database content. "
            "Be precise and factual. Do not speculate beyond the provided data."
        )
        
        prompt = (
            f"Database Context:\n{data_context}\n\n"
            f"User Query: {query}\n\n"
            "Provide a factual summary or data point from the context that helps answer the query."
        )
        
        answer = await gemini_client.generate_text(prompt, system_instruction=system_prompt)
        
        return {
            "answer": answer,
            "confidence": 0.85
        }
