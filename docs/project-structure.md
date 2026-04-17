# Project Structure

- `backend/app/api`: HTTP endpoints
- `backend/app/agents`: parallel answer-generating and evaluator agents
- `backend/app/orchestration`: query routing and multi-agent execution
- `backend/app/db`: SQLAlchemy models, repositories, seeding, migrations
- `backend/app/vector`: PDF chunking/indexing/retrieval
- `backend/app/services`: auth, prompts, routing, caching
- `frontend/src/pages`: login and chat screens
- `frontend/src/components`: UI components for webcam and chat
- `infra`: docker-compose for postgres/redis/qdrant
- `docs`: architecture, setup, decisions, structure
