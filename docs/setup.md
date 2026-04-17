# Setup Guide: Nexus: Character Design Architect

This guide provides step-by-step instructions for setting up the Intelligent Hybrid RAG system on MacOS, Linux, and Windows.

## 📋 Prerequisites

Before starting, ensure you have the following installed:
- **Python 3.10+**: [Download here](https://www.python.org/downloads/)
- **Node.js 18+**: [Download here](https://nodejs.org/)
- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/) (Required for local Vector DB and Redis)

---

## 🛠️ 1. Infrastructure (Docker)

This project uses Docker to manage the local **Vector Store (Qdrant)** and **Cache (Redis)**.

```bash
cd infra
docker compose up -d
```
*Verify success by visiting `http://localhost:6333/dashboard` for the Qdrant UI.*

---

## 🐍 2. Backend Setup

### Environment Configuration
1. Navigate to the backend folder: `cd backend`
2. Create your environment file: `cp .env.example .env`
3. Open `.env` and provide your `LLM_API_KEY` (Gemini) and `DATABASE_URL` (Neon Postgres).

### Virtual Environment & Installation

#### **MacOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

#### **Windows (PowerShell/CMD)**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .
```

### Initializing the Knowledge Base
To seed the system with the initial design documentation and technical constraints:
```bash
# Ensure your .venv is active
python scripts/init_db.py
python scripts/ingest_knowledge.py
```

### Starting the Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 💻 3. Frontend Setup

1. Open a new terminal and navigate to the frontend folder: `cd frontend`
2. Install dependencies:
```bash
npm install
```
3. Start the development server:
```bash
npm run dev
```
*Access the UI at `http://localhost:5173`*

---

## ❓ Troubleshooting

### Windows "Library Not Found" (insightface/opencv)
If you encounter errors related to `cv2` or `onnxruntime`:
1. Ensure you have the **Visual C++ Redistributable** installed.
2. If using Python 3.12+, you may need to install `setuptools` manually: `pip install setuptools`.

### MacOS "Permission Denied"
If Python cannot create the `.venv`, use:
```bash
sudo chown -R $USER .
python3 -m venv .venv
```

### Gemini API 404/Authentication
Ensure your `LLM_MODEL` in `.env` is set exactly to `gemini-1.5-flash` or `gemini-1.5-pro`.
