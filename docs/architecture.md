# Hybrid RAG Interviewer: Architectural Documentation

## 1. System Overview
The Intelligent Hybrid RAG Interviewer is a production-grade multi-agent system designed to evaluate candidates for Video Game Character Designer roles. It leverages a combination of structured relational data and unstructured creative knowledge to provide comprehensive interview feedback.

## 2. Multi-Agent Architecture
The core "brain" of the system is the **Hybrid Orchestrator**, which manages three specialized AI agents (powered by Google Gemini 1.5 Flash):

### Agents
- **SQL Agent**: Connects to the **Neon PostgreSQL** database. It queries structured tables for genres, archetypes, and production constraints.
- **RAG Agent**: Searches a persistent **ChromaDB** vector store. It retrieves unstructured creative knowledge from design theory documents.
- **Evaluator Agent**: Synthesizes the outputs from the internal agents into a single, polished response, ensuring narrative coherence and maintaining the Senior Interviewer persona.

### Execution Flow
1. **Routing**: The `QueryRouter` analyzes the user's intent to determine if the question is factual, creative, or hybrid.
2. **Parallel Retrieval**: Both SQL and RAG agents are triggered in parallel with a **4-second maximum timeout** via `asyncio`.
3. **Synthesis**: The Evaluator merges the results, respecting the original routing strategy.

## 3. Biometric Security & Authentication
- **Enrolment**: Users capture a biometric sequence (15 frames) which is converted into a 512-dimensional embedding using `sentence-transformers`.
- **Verification**: A liveness challenge (e.g., "Blink", "Turn Left") is issued. The system validates both the liveness property and the embedding similarity (Cosine Similarity).
- **Persistence**: Embeddings are stored in the PostgreSQL `face_identities` table.

## 4. Production Standards
- **Cloud Infrastructure**: Migrated from SQLite to Neon PostgreSQL for horizontal scalability and reliability.
- **Modular Design**: Separated into `api`, `agents`, `db`, `services`, and `core` packages for clear separation of concerns.
- **Performance**: Token-optimized prompts and parallel execution ensure responses are consistently under **5 seconds**.
- **Security**: All API endpoints (except login/register) are protected by Bearer JWT tokens.

## 5. Setup Instructions
1. **Environment**: Copy `.env.example` to `.env` and fill in `LLM_API_KEY` (Gemini) and `DATABASE_URL` (Neon).
2. **Backend**: Run `.venv/bin/pip install -r requirements.txt` and `python scripts/init_db.py`.
3. **Frontend**: Run `npm install` and `npm run dev`.
4. **Data**: Use `python scripts/ingest_knowledge.py` to seed the Vector DB with design theory.
