class QueryRouter:
    structured_keywords = {"genre", "archetype", "constraint", "timeline", "memory", "polycount", "stat", "budget"}
    creative_keywords = {"propose", "design", "mechanic", "optimize", "balance", "improve", "create", "how to", "narrative", "creative", "style", "lore", "visual"}

    greeting_keywords = {"hi", "hello", "hey", "greetings", "morning", "afternoon", "evening", "who are you"}
    off_topic_keywords = {"sort", "binary search", "linked list", "sql query", "array", "python code", "javascript", "history of", "medical", "legal", "mathematics"}
    gaming_allow_list = {"unity", "unreal", "game engine", "godot", "c#", "c++"}

    def route(self, query: str) -> str:
        lowered = query.lower().strip().replace("?", "").replace("!", "")
        
        # Immediate greeting detection
        if lowered in self.greeting_keywords or any(lowered == k for k in self.greeting_keywords):
             return "greeting"

        # Out-of-scope guardrail
        # Check if it has off-topic keywords AND doesn't mention game-specific tech
        is_off_topic = any(word in lowered for word in self.off_topic_keywords)
        has_gaming_context = any(word in lowered for word in self.gaming_allow_list)
        
        if is_off_topic and not has_gaming_context:
            return "out_of_scope"
        has_structured = any(word in lowered for word in self.structured_keywords)
        has_creative = any(word in lowered for word in self.creative_keywords)
        
        if has_structured and has_creative:
            return "hybrid"
        if has_structured:
            return "structured"
        if has_creative:
            return "unstructured"
        return "hybrid"
