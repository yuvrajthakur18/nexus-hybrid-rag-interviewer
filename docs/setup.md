# Setup Instructions

## Infrastructure
```bash
cd infra
docker compose up -d
```

## Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Frontend
```bash
cd frontend
npm install
npm run dev
```
