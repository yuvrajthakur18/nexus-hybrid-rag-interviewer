# Nexus Core: Intelligent Hybrid RAG Interviewer

Nexus Core is a production-grade, multi-agent AI system designed to interview video game character designers. It leverages a Hybrid RAG architecture to reason over both structured technical constraints (Postgres) and unstructured design theory (Vector DB).

## 🚀 Key Features
- **Biometric Identity Verification**: Real-time webcam face authentication using InsightFace.
- **Hybrid RAG Engine**: Combines Neon PostgreSQL data with Semantic Search across design documents.
- **Multi-Agent Orchestration**: Independent SQL, RAG, and Evaluator agents operating in parallel.
- **SSE Reasoning Stream**: GPT-style "Reasoning" logs showing real-time agent coordination.
- **Sub-5s Performance**: High-speed synthesis using Google Gemini 1.5 Flash.

---

## 🛠️ Setup Instructions

### Backend (FastAPI)
1. **Environment**: Python 3.11+
2. **Install Dependencies**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
3. **Configure Environment**:
   Create a `.env` file in the `backend/` directory (see [.env.example](.env.example)):
   ```env
   LLM_API_KEY="your-google-api-key"
   DATABASE_URL="postgresql+psycopg://..."
   ```
4. **Run Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend (React + Vite)
1. **Environment**: Node.js 18+
2. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```
3. **Run App**:
   ```bash
   npm run dev
   ```

---

## 📁 Project Structure

```text
├── backend
│   ├── app
│   │   ├── agents           # SQLAgent, RAGAgent, EvaluatorAgent
│   │   ├── api              # FastAPI Endpoints (Auth, Chat)
│   │   ├── core             # Global Config, API Clients
│   │   ├── db               # Database Schemas & Session
│   │   ├── orchestration    # Agentic Coordination Logic
│   │   └── services         # FaceAuth, Retrieval, Prompting
│   ├── pyproject.toml       # Dependency Manifest
│   └── ARCHITECTURE.md      # Technical Design Deep-Dive
└── frontend
    ├── src
    │   ├── components      # Chat UI, Accordion, Citations
    │   ├── hooks           # useChat (Streaming Logic)
    │   └── services        # API Clients
```

## 🧠 Architectural Decisions
For a detailed explanation of the Multi-Agent flow, Face Authentication security, and Token Optimization, please refer to the **[ARCHITECTURE.md](./ARCHITECTURE.md)** file.

---

## ⚖️ License
This project was developed for the Intelligent Hybrid RAG-Based Interview Chatbot Assignment (Tier-2).
