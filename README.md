# ProcureFlow – Milestone 1

A guided starter for a portfolio S2P application. This first vertical slice includes:
- FastAPI backend
- SQLite database for local development (easy to switch to PostgreSQL later)
- Sourcing project create/list APIs
- Next.js frontend starter with a sourcing workspace

## Prerequisites
- Python 3.11+
- Node.js 20+
- npm
- Git (recommended)

## 1. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to test the API.

## 2. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## What works in this milestone
- View sourcing projects
- Create a sourcing project
- Persist projects in a local SQLite database
- View automatically generated API documentation

## Next milestone
Add suppliers, RFQs, RFQ line items, supplier invitations, quotation submissions and a comparison engine.

## Important
This is a learning/portfolio starter, not production-ready procurement software. Authentication, authorization, audit logging, secure document storage, validation hardening, tests and deployment controls will be added in later milestones.
