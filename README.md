# MentorOS — AI Student Growth Platform with Persistent Memory

> **Qwen Global AI Hackathon 2026 — Track 1 (MemoryAgent) Submission**

MentorOS is a full-stack AI mentor that **remembers** every student's learning journey and continuously generates personalized career recommendations, skill-gap analysis, project ideas, and learning roadmaps — powered by long-term semantic memory.

| Name                   | Role                                              |
| ---------------------- | ------------------------------------------------- |
| Muhammad Bilal Hussain | Team Lead · Backend · AI · Memory Engine       |
| Noor Fatima            | Presentation · UI/UX · Documentation · Testing |

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Step-by-Step Setup](#step-by-step-setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
- [Environment Variables Reference](#environment-variables-reference)
- [API Reference](#api-reference)
- [How the Memory Engine Works](#how-the-memory-engine-works)
- [Deployment to Vercel](#deployment-to-vercel)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Not Yet Built](#not-yet-built)

---

## Features

### Backend

| Feature                      | Description                                                                                                                                                                                                                                                                                                                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Auth**               | Register, login (JWT),`GET /auth/me`, `POST /auth/refresh` (silent session renewal). Login triggers a memory decay pass.                                                                                                                                                                                                                                                                     |
| **Student Data**       | Profile, Skills, Projects, Certificates, Career Goals — full CRUD, scoped per user. New Career Goals automatically**supersede** the previous one (preserved, not deleted).                                                                                                                                                                                                                |
| **Resume Upload**      | PDF /`.txt` → Qwen structured extraction → automatically populates domain tables + memory. Zero disk writes — fully in-memory processing.                                                                                                                                                                                                                                                   |
| **Memory Engine**      | Every fact is embedded, stored in a vector DB, and tracked in SQL with an importance score. Retrieval uses cosine similarity re-ranked by importance. Two forgetting mechanics:**supersession** (contradiction) and **decay** (time-based archival on login). Gracefully degrades if the embedding API is unavailable — memory is saved in SQL and retrieval returns empty results. |
| **AI Recommendations** | Roadmap, skill-gap analysis, and project ideas — all grounded in retrieved memory via Qwen, and written back into memory.                                                                                                                                                                                                                                                                       |

### Frontend

| Feature                | Description                                                                                                                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Pages**        | Login, Register, Dashboard, Profile, Resume Upload & Analysis, Skills, Projects, Certificates, Memory Timeline, AI Recommendations, Career Goals, Settings.                                                  |
| **Dashboard**    | Summary cards (skills/projects/certificates/goal counts), memory statistics pie chart, skill-level bar chart, resume status, AI recommendation panel, recent-activity timeline, quick-action buttons.        |
| **Auth**         | JWT stored client-side, Axios request interceptor attaches token automatically. Two-layer refresh: proactive (silent refresh ~2 min before expiry) + reactive (Axios interceptor catches 401, retries once). |
| **Dark / Light** | Theme toggle via`next-themes`.                                                                                                                                                                             |
| **Responsive**   | Collapsible sidebar, mobile-friendly layout.                                                                                                                                                                 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Frontend (Next.js 15)                     │
│  App Router · TypeScript · Tailwind · TanStack Query · Axios    │
│  12 protected pages · JWT auth · Dark/Light theme               │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│ │  Routers   │→│   Services    │→│  Repositories (SQLAlchemy) │ │
│ │ (HTTP thin)│  │ (business)   │  │  (all direct DB access)   │ │
│ └──────────┘  └──────┬───────┘  └───────────────────────────┘ │
│                       │                                         │
│                       ▼                                         │
│              ┌────────────────┐                                 │
│              │ Memory Engine  │                                 │
│              │ writer         │  → embeds via Qwen API          │
│              │ retriever      │  → cosine similarity search     │
│              │ importance     │  → scoring + decay              │
│              └───────┬────────┘                                 │
│                      │                                          │
│          ┌───────────┴───────────┐                              │
│          ▼                       ▼                              │
│  ┌──────────────┐      ┌───────────────────┐                   │
│  │  PostgreSQL   │      │  Vector Store      │                   │
│  │  + pgvector   │      │  (auto-selected)   │                   │
│  │  (production) │      │  pgvector OR        │                   │
│  └──────────────┘      │  ChromaDB (local)   │                   │
│                         └───────────────────┘                   │
│                                                                  │
│  ┌──────────────────────────────────────────┐                   │
│  │  Alibaba Cloud Qwen (OpenAI-compatible)   │                   │
│  │  qwen3.7-plus · text-embedding-v4 (1024d)│                   │
│  └──────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer                  | Technology                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| **Backend**      | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic Settings                                   |
| **Database**     | SQLite (local dev) / PostgreSQL (production)                                               |
| **Vector Store** | ChromaDB (local) / pgvector extension (production)                                         |
| **AI / LLM**     | Alibaba Cloud Qwen (`qwen3.7-plus` for generation, `text-embedding-v4` for embeddings) |
| **Auth**         | JWT (PyJWT + bcrypt), 12-hour token expiry                                                 |
| **Frontend**     | Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui-style components              |
| **State**        | TanStack Query (server state), React Context (auth)                                        |
| **Charts**       | Recharts                                                                                   |
| **Deployment**   | Vercel (frontend + backend serverless)                                                     |

---

## Project Structure

```
mentoros/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point, CORS, routers
│   │   ├── core/
│   │   │   ├── config.py           # All env-driven settings (pydantic-settings)
│   │   │   └── deps.py             # Dependency injection (get_current_user)
│   │   ├── db/
│   │   │   ├── session.py          # SQLAlchemy engine, Base, get_db()
│   │   │   └── base.py             # Imports all models for metadata discovery
│   │   ├── models/                 # SQLAlchemy ORM models (9 models)
│   │   │   ├── user.py, profile.py, skill.py, project.py
│   │   │   ├── certificate.py, career_goal.py, resume.py
│   │   │   └── memory.py, ai_insight.py
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── repositories/           # All direct database access (4 files)
│   │   ├── routers/                # Thin HTTP handlers (9 routers)
│   │   │   ├── auth.py, profile.py, skills.py, projects.py
│   │   │   ├── certificates.py, career_goals.py
│   │   │   ├── resume.py, memory.py, recommendations.py
│   │   ├── services/               # Business logic (6 files)
│   │   │   ├── auth_service.py     # Register, authenticate, issue token
│   │   │   ├── student_data_service.py  # CRUD + memory writes for all entities
│   │   │   ├── resume_service.py   # Upload → extract → apply (in-memory)
│   │   │   ├── recommendation_service.py  # AI recommendation generation
│   │   │   ├── memory_service.py   # Timeline, delete, login decay
│   │   │   └── memory_writer_service.py  # Coordinates all memory writes
│   │   ├── memory_engine/          # Persistent memory system
│   │   │   ├── vector_store.py     # Unified interface (auto-selects backend)
│   │   │   ├── pgvector_backend.py # Production: pgvector + embeddings table
│   │   │   ├── chroma_backend.py   # Local dev: ChromaDB file-based storage
│   │   │   ├── writer.py           # Writes facts to memory (SQL + vector)
│   │   │   ├── retriever.py        # Cosine similarity + importance re-ranking
│   │   │   ├── importance.py       # Scoring math (initial, decay, boost, composite)
│   │   │   └── decay.py            # Login-triggered decay/archival pass
│   │   └── ai/
│   │       ├── llm_provider.py     # Abstract LLM interface
│   │       ├── qwen_client.py      # Qwen API implementation
│   │       ├── prompts.py          # System prompts for extraction
│   │       └── reasoning_prompts.py # Prompts for AI recommendations
│   ├── requirements.txt            # Python dependencies
│   ├── vercel.json                 # Vercel deployment config
│   ├── .env.example                # Documented env template (18 settings)
│   └── tests/
│       └── test_api.py             # Comprehensive test suite
├── frontend/
│   ├── app/
│   │   ├── layout.tsx              # Root layout (ErrorBoundary + Providers)
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── (app)/                  # Protected route group (auth guard)
│   │       ├── layout.tsx          # Sidebar + Topbar shell
│   │       ├── dashboard/page.tsx
│   │       ├── profile/page.tsx
│   │       ├── skills/page.tsx
│   │       ├── projects/page.tsx
│   │       ├── certificates/page.tsx
│   │       ├── career-goals/page.tsx
│   │       ├── resume/page.tsx
│   │       ├── memory/page.tsx
│   │       ├── recommendations/page.tsx
│   │       └── settings/page.tsx
│   ├── components/
│   │   ├── ui/                     # shadcn-style primitives
│   │   ├── layout/                 # Sidebar, Topbar
│   │   ├── dashboard/, skills/, memory/, ...
│   │   └── common/error-boundary.tsx
│   ├── hooks/                      # TanStack Query hooks (one per domain)
│   ├── lib/
│   │   ├── api/                    # Axios service modules (1:1 with backend)
│   │   │   ├── client.ts           # Axios instance + token interceptor
│   │   │   ├── auth.ts, profile.ts, skills.ts, projects.ts
│   │   │   ├── certificates.ts, careerGoals.ts, resume.ts
│   │   │   ├── memory.ts, recommendations.ts
│   │   └── auth-context.tsx        # Auth state + proactive token refresh
│   ├── types/index.ts              # TypeScript types (mirrors Pydantic schemas)
│   ├── package.json
│   ├── next.config.mjs             # API proxy rewrites, image patterns
│   ├── tailwind.config.ts
│   └── .env.local.example
└── README.md
```

---

## Prerequisites

- **Python 3.11+** and **pip**
- **Node.js 18+** and **npm**
- An **Alibaba Cloud Qwen API key** ([get one here](https://dashscope.console.aliyun.com/))
- **(Optional)** A PostgreSQL database for production — [Neon](https://neon.tech) free tier works great

---

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/mentoros.git
cd mentoros
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
```

**Activate the virtual environment:**

```bash
# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (cmd)
venv\Scripts\activate.bat
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Create your `.env` file:**

```bash
cp .env.example .env
```

**Edit `.env` — minimum required settings:**

```ini
# Required: your Qwen API key
QWEN_API_KEY=sk-your-qwen-api-key

# Required: change this to a random secret (any long string works)
JWT_SECRET_KEY=any-random-string-at-least-32-chars

# Required on Vercel, optional locally:
FRONTEND_URL=http://localhost:3000
```

Everything else has sensible defaults. See [Environment Variables Reference](#environment-variables-reference) for the full list.

**Start the backend:**

```bash
uvicorn app.main:app --reload
```

The backend runs at **`http://localhost:8000`**.

- API docs (Swagger): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

> The first startup creates `mentoros.db` (SQLite) automatically. No database setup required for local dev.

---

### 3. Frontend Setup

Open a **new terminal** (keep the backend running):

```bash
cd frontend
npm install
```

**Create your `.env.local` file:**

```bash
cp .env.local.example .env.local
```

By default it points to `http://localhost:8000` — no changes needed for local dev.

**Start the frontend:**

```bash
npm run dev
```

The frontend runs at **`http://localhost:3000`**.

1. Open `http://localhost:3000` in your browser
2. Register a new account
3. Log in — you'll land on the Dashboard
4. Fill out your profile, add skills/projects, upload a resume
5. Visit the Memory Timeline to see persistent memory in action
6. Click "Generate" in Recommendations to get AI-powered guidance

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable                        | Default                                                    | Description                                                        |
| ------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------ |
| `ENV`                         | `development`                                            | `development` or `production`                                  |
| `DEBUG`                       | `true`                                                   | Enable debug mode                                                  |
| `FRONTEND_URL`                | `http://localhost:3000`                                  | Frontend origin for CORS                                           |
| `DATABASE_URL`                | `sqlite:///./mentoros.db`                                | Database connection string                                         |
| `JWT_SECRET_KEY`              | `CHANGE_ME_IN_ENV`                                       | **Required.** Secret for signing JWTs.                       |
| `JWT_ALGORITHM`               | `HS256`                                                  | JWT signing algorithm                                              |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `720`                                                    | Token lifetime (12 hours)                                          |
| `QWEN_API_KEY`                | `""`                                                     | **Required.** Your Alibaba Cloud Qwen API key.               |
| `QWEN_BASE_URL`               | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | Qwen API endpoint (use`dashscope.aliyuncs.com` for China region) |
| `QWEN_MODEL`                  | `qwen3.7-plus`                                           | Model for chat generation                                          |
| `QWEN_EMBEDDING_MODEL`        | `text-embedding-v4`                                      | Model for text embeddings                                          |
| `QWEN_EMBEDDING_DIMENSIONS`   | `1024`                                                   | Embedding vector dimensions                                        |
| `VECTOR_BACKEND`              | `auto`                                                   | `auto` / `pgvector` / `chroma`                               |
| `CHROMA_PERSIST_DIR`          | `./chroma_store`                                         | ChromaDB storage path (local only)                                 |
| `CHROMA_COLLECTION_NAME`      | `mentoros_memories`                                      | ChromaDB collection name                                           |
| `MEMORY_DECAY_RATE`           | `0.05`                                                   | Importance lost per idle week                                      |
| `MEMORY_ARCHIVE_THRESHOLD`    | `0.15`                                                   | Below this → memory is archived                                   |
| `MEMORY_RETRIEVAL_TOP_K`      | `8`                                                      | Max memories retrieved per query                                   |

**How `VECTOR_BACKEND=auto` works:**

- `DATABASE_URL` starts with `postgresql` → uses **pgvector**
- Otherwise → uses **ChromaDB** (local file-based)

**International vs China endpoint:**

| Region        | `QWEN_BASE_URL`                                          |
| ------------- | ---------------------------------------------------------- |
| International | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| China         | `https://dashscope.aliyuncs.com/compatible-mode/v1`      |

Make sure your API key matches the endpoint region. An international key won't work with the China endpoint and vice versa.

### Frontend (`frontend/.env.local`)

| Variable                | Default                   | Description          |
| ----------------------- | ------------------------- | -------------------- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## API Reference

All endpoints below require a JWT token via `Authorization: Bearer <token>` header, except register and login.

### Auth (`/auth`)

| Method   | Endpoint           | Body                        | Description          |
| -------- | ------------------ | --------------------------- | -------------------- |
| `POST` | `/auth/register` | `{ "email", "password" }` | Create account       |
| `POST` | `/auth/login`    | `{ "email", "password" }` | Get JWT token        |
| `GET`  | `/auth/me`       | —                          | Current user info    |
| `POST` | `/auth/refresh`  | —                          | Extend current token |

### Profile (`/profile`)

| Method  | Endpoint        | Body                                            | Description           |
| ------- | --------------- | ----------------------------------------------- | --------------------- |
| `GET` | `/profile/me` | —                                              | Get or create profile |
| `PUT` | `/profile/me` | `{ "full_name"?, "bio"?, "education"?, ... }` | Update profile        |

### Skills (`/skills`)

| Method     | Endpoint         | Body                    | Description     |
| ---------- | ---------------- | ----------------------- | --------------- |
| `GET`    | `/skills`      | —                      | List all skills |
| `POST`   | `/skills`      | `{ "name", "level" }` | Add a skill     |
| `DELETE` | `/skills/{id}` | —                      | Remove a skill  |

### Projects (`/projects`)

| Method     | Endpoint           | Body                                         | Description       |
| ---------- | ------------------ | -------------------------------------------- | ----------------- |
| `GET`    | `/projects`      | —                                           | List all projects |
| `POST`   | `/projects`      | `{ "title", "description"?, "url"?, ... }` | Add a project     |
| `DELETE` | `/projects/{id}` | —                                           | Remove a project  |

### Certificates (`/certificates`)

| Method     | Endpoint               | Body                                    | Description           |
| ---------- | ---------------------- | --------------------------------------- | --------------------- |
| `GET`    | `/certificates`      | —                                      | List all certificates |
| `POST`   | `/certificates`      | `{ "name", "issuer"?, "date"?, ... }` | Add a certificate     |
| `DELETE` | `/certificates/{id}` | —                                      | Remove a certificate  |

### Career Goals (`/career-goals`)

| Method   | Endpoint          | Body                            | Description                           |
| -------- | ----------------- | ------------------------------- | ------------------------------------- |
| `GET`  | `/career-goals` | —                              | List all goals (active + superseded)  |
| `POST` | `/career-goals` | `{ "title", "description"? }` | Add goal (supersedes previous active) |

### Resume (`/resume`)

| Method   | Endpoint           | Body                                 | Description                                               |
| -------- | ------------------ | ------------------------------------ | --------------------------------------------------------- |
| `GET`  | `/resume`        | —                                   | List uploaded resumes                                     |
| `POST` | `/resume/upload` | `multipart/form-data` (PDF or TXT) | Upload → AI extraction → auto-populate profile + memory |

### Memory (`/memory`)

| Method     | Endpoint             | Description                                                 |
| ---------- | -------------------- | ----------------------------------------------------------- |
| `GET`    | `/memory/timeline` | All memories (active / superseded / archived), newest first |
| `DELETE` | `/memory/{id}`     | Delete a memory (SQL row + vector)                          |

### AI Recommendations (`/recommendations`)

| Method   | Endpoint                       | Description                   |
| -------- | ------------------------------ | ----------------------------- |
| `POST` | `/recommendations/roadmap`   | Personalized learning roadmap |
| `POST` | `/recommendations/skill-gap` | Skill gap analysis            |
| `POST` | `/recommendations/projects`  | Project ideas                 |

> **Note:** If the embedding API is unavailable, recommendations still work but without memory context (the AI generates generic advice based on the student's profile). The system degrades gracefully — no 500 errors.

### Health Check (unauthenticated)

| Method  | Endpoint    | Description                                          |
| ------- | ----------- | ---------------------------------------------------- |
| `GET` | `/health` | Returns app name, env, database type, vector backend |

---

## How the Memory Engine Works

The memory engine is the core of the MemoryAgent track. Here's how it works:

### Writing Memory

Every time a student adds a skill, project, certificate, career goal, resume entry, or generates an AI recommendation, the system:

1. Generates a natural-language "fact" string (e.g., `"User added Python at level Advanced to their skills."`)
2. Creates a SQL row (`memory` table) with importance score and metadata
3. Generates a 1024-dimensional embedding via `text-embedding-v4`
4. Stores the embedding in the vector backend (pgvector or ChromaDB)

If the embedding API fails, the SQL row is still saved — the memory is just not searchable by similarity until a retry.

### Retrieval (for AI Recommendations)

When generating a recommendation, the system:

1. Embeds the current student context (recent facts, skills, goals)
2. Queries the vector store for the top-K most similar memories (cosine similarity)
3. Re-ranks results by **composite score** = `importance × cosine_similarity`
4. Injects retrieved memories as context into the Qwen prompt

If embedding or vector search fails, retrieval returns an empty list and the recommendation is generated without memory context.

### Forgetting (Two Mechanisms)

| Mechanism              | Trigger                                          | What happens                                                                                                              |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| **Supersession** | Contradictory data added (e.g., new career goal) | Old memory status →`superseded`, linked to its replacement                                                             |
| **Decay**        | Student logs in                                  | Memories lose`MEMORY_DECAY_RATE` importance per idle week. Below `MEMORY_ARCHIVE_THRESHOLD` → status → `archived` |

This gives the system realistic memory evolution — memories fade naturally unless reinforced.

### Vector Backend Abstraction

```
vector_store.py (unified interface)
    ├── pgvector_backend.py  ← auto-selected when DATABASE_URL = postgresql
    │   (stores embeddings in a PostgreSQL table via pgvector extension)
    └── chroma_backend.py    ← auto-selected when DATABASE_URL = sqlite
        (stores embeddings in a local ChromaDB directory)
```

---

## Deployment to Vercel

### Backend

1. Push `backend/` to a Git repository (or deploy as a subdirectory)
2. Connect to [Vercel](https://vercel.com) — it auto-detects `@vercel/python` via `vercel.json`
3. Set environment variables in Vercel Dashboard (same as `.env` — see [reference](#environment-variables-reference))
4. Key production settings:
   - `DATABASE_URL` → PostgreSQL connection string (e.g., Neon, Supabase, or RDS)
   - `ENV=production`
   - `FRONTEND_URL` → your Vercel frontend URL (e.g., `https://mentor-os.vercel.app`)
   - `JWT_SECRET_KEY` → a secure random string
   - `QWEN_BASE_URL` → use the international endpoint unless your server is in China
5. Deploy — `vercel.json` already has `maxDuration: 30` for slower cold starts

### Frontend

1. Connect `frontend/` to Vercel
2. Set `NEXT_PUBLIC_API_URL` to your backend's Vercel URL
3. Deploy

### CORS

The backend automatically:

- Allows `localhost:3000` and `localhost:3001` for local dev
- Allows `FRONTEND_URL` from env
- Allows `https://*.vercel.app` via regex pattern
- Accepts additional origins via `CORS_ORIGINS` env var (comma-separated)

---

## Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

The test suite (`tests/test_api.py`) covers:

- **Auth flow** — register, login, `/auth/me`, `/auth/refresh`
- **CRUD for all entities** — skills, projects, certificates, career goals, profile
- **Memory engine** — write, retrieve (cosine similarity + importance ranking), supersession, decay/archival, cross-user isolation
- **Resume upload** — PDF extraction, in-memory processing, auto-population
- **CORS** — preflight headers, origin validation
- **Edge cases** — unauthorized access, empty fields, career goal supersession

Also includes a standalone memory-engine test harness using a deterministic fake embedding provider — 18 assertions covering write, retrieval ranking, supersession, decay, and isolation.

### Frontend Tests

```bash
cd frontend
npm run build    # catches TypeScript errors
npm run lint     # catches lint issues
```

All 14 routes build with zero TypeScript errors. Every type in `types/index.ts` is verified field-by-field against the corresponding backend Pydantic schema.

---

## Troubleshooting

### Backend won't start

| Problem                                      | Solution                                                                                                                |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'X'` | Run`pip install -r requirements.txt` again. Make sure your venv is activated.                                         |
| `pydantic_settings.errors.ValidationError` | Missing required`.env` values. Copy `.env.example` to `.env` and fill in `QWEN_API_KEY` and `JWT_SECRET_KEY`. |
| `sqlite3.OperationalError: no such table`  | Normal on first run — tables are created automatically on startup. If it persists, delete`mentoros.db` and restart.  |

### Frontend won't start

| Problem                             | Solution                                                                                                                |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `Module not found` errors         | Run`npm install` again.                                                                                               |
| API calls fail with CORS error      | Make sure backend is running on port 8000. Check`FRONTEND_URL` in `backend/.env` matches `http://localhost:3000`. |
| `NEXT_PUBLIC_API_URL` not working | It must be set as`NEXT_PUBLIC_API_URL` (not just `API_URL`). Restart the dev server after changing it.              |

### AI features not working

| Problem                              | Solution                                                                                                                                                                                                                                                              |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AccessDenied` error on embeddings | Your API key doesn't have access to`text-embedding-v4`. Check the [Alibaba Cloud Model Studio console](https://dashscope.console.aliyun.com/) to enable the embedding model. Also verify you're using the correct endpoint for your region (international vs China). |
| "AI generation failed: 502"          | Check your`QWEN_API_KEY` is valid and has quota. Check `QWEN_BASE_URL` matches your region.                                                                                                                                                                       |
| Recommendations are empty/generic    | This usually means no memories exist yet (or the embedding API is unavailable). Add skills, projects, and career goals first — the AI uses these as context. Even without memory context, the AI still generates advice based on the student's profile.              |
| Resume upload fails                  | Only PDF and TXT files are supported. Make sure the file isn't empty.                                                                                                                                                                                                 |
| Vector write warnings in logs        | `Vector write failed for memory_id=X — memory saved in SQL only.` This is normal if the embedding API is temporarily unavailable. The memory is saved in SQL and will be searchable once embeddings succeed.                                                       |

### Vercel deployment issues

| Problem                      | Solution                                                                                                                                             |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Backend 502 on Vercel        | Check Vercel function logs. Common causes: missing env vars,`QWEN_API_KEY` not set, cold start timeout. `maxDuration: 30` is already configured. |
| Frontend can't reach backend | Verify`NEXT_PUBLIC_API_URL` in Vercel env vars points to the correct backend URL.                                                                  |
| Data disappears on Vercel    | Expected — Vercel functions use ephemeral storage. You**must** use PostgreSQL (Neon, Supabase, etc.) for data to persist.                     |

---

## Not Yet Built

- Exportable reports / analytics beyond dashboard charts
- Background task scheduler (decay runs on login by design — see `backend/app/memory_engine/decay.py`)
- Multi-user collaboration / sharing
- Mobile app
