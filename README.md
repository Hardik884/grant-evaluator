# Grant Evaluator

AI-assisted platform for reviewing grant proposals end to end. Applicants upload a PDF or DOCX, the system runs an agent-driven evaluation pipeline, and reviewers receive live progress updates, structured scoring, critique summaries, and a polished PDF report.

## Features
- **Gemini 2.0 Flash reasoning stack** with supporting retrieval agents for contextual grounding.
- **Live evaluation telemetry** streamed over WebSockets to the React dashboard.
- **Comprehensive scoring** with automated strengths, weaknesses, and budget analysis.
- **One-click PDF exports** that mirror the UI and highlight decisions on a 10-point scale.
- **Plagiarism inspection** and domain-aware critique via specialized agents.

## Tech Stack
- **Frontend:** React (Vite, TypeScript, Tailwind CSS)
- **Backend:** FastAPI, MongoDB Atlas, WebSockets
- **AI & Agents:** Gemini 2.0 Flash, custom retrieval, evaluation, and plagiarism agents
- **Reporting:** ReportLab for PDF generation

## Project Structure
```
backend/      FastAPI service, evaluation orchestration, database models
frontend/     Vite + React SPA for uploads, status, and results
src/          Shared AI pipeline, agents, embeddings, and utilities
```

## Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB database (Atlas or self-hosted)
- Gemini API access

## Configuration
1. Create a backend environment file:
   ```bash
   cp backend/.ENV backend/.env
   ```
2. Populate `backend/.env` with your credentials:
   ```dotenv
   MONGODB_URL="<your-mongodb-connection-string>"
   DATABASE_NAME="<database-name>"
   GOOGLE_API_KEY="<gemini-or-maps-api-key>"
   ```
3. Ensure `.env` files are ignored by Git (already configured in `.gitignore`).

> **Note:** The repository currently ships with `backend/.ENV` checked in for local development. Replace its contents with safe placeholders (or delete it) before publishing your repository.

## Backend Setup
```bash
# From the project root
python -m venv .venv
.\.venv\Scripts\activate    # (On macOS/Linux use: source .venv/bin/activate)
pip install -r requirements.txt
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```
The API is exposed at `http://localhost:8000` with endpoints under `/api/*` and a health check on `/`.

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The Vite dev server runs on `http://localhost:5173`. Configure `VITE_API_BASE_URL` in `frontend/.env` if you proxy to a different backend URL.

## Generated Reports
- Scorecards render as `/10` with contextual descriptions.
- File sizes are displayed in kilobytes across PDF and UI surfaces.
- Executive summaries, strengths, and weaknesses fall back to informative defaults when source data is sparse.

## Deployment Checklist
- Confirm the FastAPI app can reach your MongoDB cluster from the target environment.
- Set production-ready CORS origins in `backend/main.py`.
- Build the SPA with `npm run build` and serve the `frontend/dist` folder behind your preferred static host.
- Configure process managers (e.g., `uvicorn` + `systemd`, or Docker) and rotate all API keys before launch.

## License
MIT
