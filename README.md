# Drafter - AI Content Creation Copilot for Social Media Creators

A production-quality MVP of an AI-powered **pre-production workspace** for
short-form creators. It takes a creator from a vague idea or a few keywords all
the way to a complete, structured, production-ready script:

> Enter a rough idea, refine its direction with AI, discover stronger related
> topics, select an angle, generate hooks, research and structure the story,
> generate the complete scene-by-scene script, and receive visual directions and
> discoverable image assets for every scene.

Each stage is independently represented, persisted, and regeneratable. It is a
focused creative workspace, not a chatbot.

Highlights:

- **Idea refinement loop** - your rough input is a seed, not the brief. The
  copilot proposes a sharper premise, explains its interpretation, and offers
  alternative directions and clarifying questions before you commit.
- **Ten narrative hook archetypes** - scored for suitability per story.
- **SSE progress streaming** on the heavier generation stages.
- **Script export** - copy or download as Markdown, plain text, or narration
  only. Hook, scenes, and CTA are all inline-editable.
- **Optimistic UI** for selection/edit actions; a collapsible workspace sidebar.

---

## Table of contents

- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Backend setup](#backend-setup)
- [Frontend setup](#frontend-setup)
- [Environment variables](#environment-variables)
- [Provider abstractions](#provider-abstractions)
- [Database & schema isolation](#database--schema-isolation)
- [API reference](#api-reference)
- [Pipeline stages](#pipeline-stages)
- [Testing](#testing)
- [Design principles honored](#design-principles-honored)

---

## Architecture

```
┌────────────────────────────┐        HTTP/JSON        ┌──────────────────────────────┐
│  Next.js frontend (App      │  ───────────────────▶   │  FastAPI backend               │
│  Router, TS, Tailwind,      │                         │                                │
│  React Query)               │  ◀───────────────────   │  API routers → services        │
│  Project workspace UI       │                         │       │                        │
└────────────────────────────┘                         │       ▼                        │
                                                        │  Provider abstractions         │
                                                        │   ├── LLMProvider  ──▶ NVIDIA   │
                                                        │   │                    NIM      │
                                                        │   ├── SearchProvider ─▶ Tavily/ │
                                                        │   │                    Brave/…  │
                                                        │   └── ImageSearchProvider ─▶    │
                                                        │           Wikimedia/Pexels/…    │
                                                        │       │                        │
                                                        │       ▼                        │
                                                        │  SQLAlchemy 2.x + Alembic       │
                                                        │       │                        │
                                                        └───────┼────────────────────────┘
                                                                ▼
                                                        PostgreSQL (NeonDB)
                                                        schema: `copilot`
```

Application **services depend only on the provider abstractions**, never on a
concrete API client. Adding OpenAI, Anthropic, Gemini, or a local model means
implementing `LLMProvider` and registering it in the factory - no service code
changes.

```
KeywordService  ─┐
AngleService     │
HookService      │
ResearchService  ├──▶ LLMProvider (+ SearchProvider / ImageSearchProvider)
StoryService     │
ScriptService    │
VisualService   ─┘
```

---

## Repository layout

```
/
├── frontend/                     # Next.js App Router app
│   ├── app/                      # routes: dashboard, projects, workspace
│   ├── components/               # ui primitives + workspace panels
│   ├── hooks/                    # React Query hooks (server state)
│   ├── lib/                      # typed api client, utils
│   └── types/                    # shared TS types
│
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI routers + dependency wiring
│   │   ├── core/                 # config, error types/handlers
│   │   ├── db/                   # engine, session, declarative base
│   │   ├── models/               # SQLAlchemy models + enums
│   │   ├── schemas/              # Pydantic: api DTOs + llm structured-output shapes
│   │   ├── services/             # one service per pipeline stage
│   │   ├── providers/
│   │   │   ├── llm/              # LLMProvider + NvidiaNIMProvider (+ lazy wrapper)
│   │   │   ├── search/          # SearchProvider + Tavily/Brave/Serper
│   │   │   └── images/          # ImageSearchProvider + Wikimedia/Pexels/Unsplash
│   │   └── prompts/              # one prompt module per stage
│   ├── alembic/                  # migrations (isolated `copilot` schema)
│   └── tests/                    # pytest suite
│
├── README.md
└── .gitignore
```

---

## Tech stack

**Frontend:** Next.js (App Router) · TypeScript · Tailwind CSS · shadcn/ui-style
local components · Lucide icons · TanStack Query.

**Backend:** Python · FastAPI · Pydantic v2 · SQLAlchemy 2.x · Alembic ·
PostgreSQL (NeonDB) · psycopg 3.

**AI:** NVIDIA NIM (OpenAI-compatible API) as the primary LLM inference
provider, behind an `LLMProvider` abstraction.

---

## Prerequisites

- Python 3.11+ (tested on 3.13)
- Node.js 18+
- A PostgreSQL database (NeonDB recommended). The app confines all its tables to
  a dedicated `copilot` schema, so it can safely share a database with other
  projects.

---

## Backend setup

```bash
cd backend

# 1. create a virtualenv and install deps
python -m venv .venv
# Windows (Git Bash):
./.venv/Scripts/pip install -r requirements.txt
# macOS/Linux:
# source .venv/bin/activate && pip install -r requirements.txt

# 2. configure environment
#   create backend/.env (see the "Environment variables" table below).
#   at minimum set DATABASE_URL and a strong JWT_SECRET
#   (python -c "import secrets; print(secrets.token_urlsafe(48))").
#   set NVIDIA_API_KEY to enable AI generation.

# 3. run migrations (creates the `copilot` schema + tables)
./.venv/Scripts/alembic upgrade head

# 4. run the API
./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health` reports whether the LLM,
research, and image providers are configured.

> **No NVIDIA key?** The app still runs. CRUD, keyword selection, research in
> non-researched mode, and image discovery all work. Endpoints that require the
> model return a controlled `503 { "error": { "code": "llm_not_configured" } }`
> instead of crashing.

`DATABASE_URL` may be a plain `postgresql://…` URL (as Neon provides) - it is
automatically normalized to the psycopg-3 driver.

---

## Frontend setup

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev                       # http://localhost:3000
```

---

## Environment variables

### Backend (`backend/.env`)

| Variable                | Purpose                                                        | Default                                   |
| ----------------------- | -------------------------------------------------------------- | ----------------------------------------- |
| `DATABASE_URL`          | PostgreSQL connection string (Neon)                            | local placeholder                         |
| `NVIDIA_API_KEY`        | NVIDIA NIM key (**never sent to the frontend**)                | *(empty → LLM disabled)*                  |
| `NVIDIA_BASE_URL`       | NIM OpenAI-compatible endpoint                                 | `https://integrate.api.nvidia.com/v1`     |
| `NVIDIA_MODEL`          | Model id                                                       | `meta/llama-3.1-70b-instruct`             |
| `SEARCH_PROVIDER`       | `none` \| `tavily` \| `brave` \| `serper`                      | `none` (→ non-researched mode)            |
| `TAVILY_API_KEY` etc.   | Search keys (enable research when set)                         | *(empty)*                                 |
| `IMAGE_SEARCH_PROVIDER` | `wikimedia` \| `pexels` \| `unsplash`                          | `wikimedia` (no key needed)               |
| `PEXELS_API_KEY` / `UNSPLASH_ACCESS_KEY` | Stock image keys                              | *(empty)*                                 |
| `FRONTEND_URL`          | Allowed CORS origin                                            | `http://localhost:3000`                   |
| `WORDS_PER_MINUTE`      | Narration duration estimate rate                               | `150`                                     |

### Frontend (`frontend/.env.local`)

| Variable              | Purpose             | Default                 |
| --------------------- | ------------------- | ----------------------- |
| `NEXT_PUBLIC_API_URL` | Backend base URL    | `http://localhost:8000` |

The NVIDIA key is only ever read server-side. **Secrets are never committed**:
all `.env*` files are git-ignored and must be created locally.

Minimal `backend/.env`:

```
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
JWT_SECRET=<a long random string>
NVIDIA_API_KEY=nvapi-...        # optional; users can also add keys in Settings
ALPHA_EMAILS=you@example.com    # emails that skip the password step
```

---

## Provider abstractions

| Abstraction           | Methods                                       | Implementations                              |
| --------------------- | --------------------------------------------- | -------------------------------------------- |
| `LLMProvider`         | `generate`, `generate_structured`, `stream`   | `NvidiaNIMProvider` (OpenAI-compatible)      |
| `SearchProvider`      | `search`, `fetch_content`                     | `TavilyProvider`, `BraveSearchProvider`, `SerperProvider` |
| `ImageSearchProvider` | `search_images`, `get_image_metadata`         | `WikimediaProvider` (default, free), `PexelsProvider`, `UnsplashProvider` |

**Structured output** is validated with Pydantic. On malformed JSON the provider
attempts lenient parsing, then retries **once** with a schema-correction
instruction, and finally raises a controlled `LLMOutputError` - it never
silently accepts malformed output.

---

## Database & schema isolation

All 13 tables live in a dedicated PostgreSQL schema (`copilot`, configurable via
`DB_SCHEMA`), including this app's own `alembic_version`. This means the target
database can be shared with unrelated projects without collision.

**Models:** `User`, `ContentProject`, `Keyword`, `KeywordRecommendation`,
`ContentAngle`, `Hook`, `ResearchSource`, `StoryOutline`, `Script`,
`ScriptScene`, `VisualRecommendation`, `VisualAsset`, `Revision`. UUID primary
keys, `created_at`/`updated_at` timestamps, JSONB only where genuinely
appropriate (analysis snapshots, outline sections, key facts, revision diffs).

Keyword interactions (original / recommended / selected / rejected / custom) and
a `Revision` audit trail are persisted to support future creator-personalization
without building an ML model now.

---

## API reference

All routes are under `/api`. Errors use a consistent shape:
`{ "error": { "code": string, "message": string } }`.

```
POST   /api/projects                         create a project
GET    /api/projects                         list projects
GET    /api/projects/{id}                    full project detail (aggregate)
PATCH  /api/projects/{id}                    update project meta
DELETE /api/projects/{id}                    delete project

POST   /api/projects/{id}/idea/refine        propose a refined idea (not committed)

POST   /api/projects/{id}/keywords/recommend generate keyword recommendations
POST   /api/projects/{id}/keywords/select    select/deselect a keyword
POST   /api/projects/{id}/keywords           add a custom keyword
DELETE /api/projects/{id}/keywords/{kwId}    remove a keyword

POST   /api/projects/{id}/angles/generate    generate 5 to 8 angles
POST   /api/projects/{id}/angles/{aId}/select

POST   /api/projects/{id}/hooks/generate     analyze archetypes + generate hooks
POST   /api/projects/{id}/hooks/{hId}/select
POST   /api/projects/{id}/hooks/{hId}/regenerate   (preserves archetype)

POST   /api/projects/{id}/research           run research (or non-researched mode)
POST   /api/projects/{id}/outline/generate   generate story outline
POST   /api/projects/{id}/script/generate    generate full scene-by-scene script

# SSE progress-streaming variants of the heavier stages:
POST   /api/projects/{id}/hooks/generate/stream
POST   /api/projects/{id}/outline/generate/stream
POST   /api/projects/{id}/script/generate/stream

PATCH  /api/scripts/{scriptId}               edit hook / CTA / title
POST   /api/scenes/{sceneId}/regenerate      regenerate narration / visual direction / all
PATCH  /api/scenes/{sceneId}                 inline edit a scene
POST   /api/scenes/{sceneId}/visuals/generate   per-scene visual recommendations
POST   /api/scenes/{sceneId}/assets/search      discover real image assets
```

ORM models are never exposed directly - every route uses explicit Pydantic
request/response schemas.

---

## Pipeline stages

1. **Idea** : title (optional), rough idea, initial keywords, platform, target
   duration, tone. Good defaults; only the idea is needed. **Refine with AI**
   proposes a sharper premise, states its interpretation, and offers alternative
   directions and clarifying questions; nothing is committed until you accept.
2. **Keywords** : recommendations in three categories (semantic / story /
   discovery) with reason + relevance score; select/deselect/add/remove/regenerate.
3. **Angles** : 5 to 8 distinct angles (investigative, mystery, conflict, and
   more); choose one.
4. **Hooks** : ten narrative archetypes (mystery/curiosity, threat, cold-open,
   contrarian, problem, striking statistic, story open, direct question,
   comparison, pattern interrupt). The model scores each archetype's *suitability*
   for the story, generates hooks only where they genuinely fit, and recommends
   one. Regenerate preserves the archetype unless explicitly changed.
5. **Research** : external search + LLM synthesis with **source traceability**
   (a synthesized source is dropped unless its URL was actually retrieved). If
   synthesis fails, the retrieved raw sources are kept rather than wasting the
   search. With no search key configured, runs in clearly-marked **non-researched
   mode** and never fabricates sources.
6. **Story** : a structured outline; the model picks a fitting narrative
   structure rather than forcing a fixed template.
7. **Script** : a complete structured, timed, scene-by-scene script (hook,
   scenes, CTA). Duration is estimated from narration at a configurable WPM,
   reconciled with the scene timeline. Hook, every scene, and the CTA are
   inline-editable, and the whole script exports to Markdown, plain text, or
   narration only.
8. **Visuals** : per-scene visual *recommendations* with highly specific search
   queries, plus *discovered* image assets (with provider + license). The UI and
   data model keep a **strict distinction** between an AI recommendation and a
   real discovered asset.

Every major object is independently regeneratable with optional natural-language
refinement instructions; regenerating one scene does not regenerate the script.
All generated content is em-dash-free (enforced by prompt rules and a sanitizer).

---

## Testing

```bash
cd backend
./.venv/Scripts/python -m pytest
```

Coverage includes: the NVIDIA provider with a mocked OpenAI-compatible client
(including the parse → retry → fail path), lenient JSON extraction, structured
output validation, keyword/angle/hook generation, hook-archetype preservation on
regenerate, script duration estimation, scene regeneration (single-field), the
Wikimedia provider parsing (mocked HTTP), provider factories, and critical API
endpoints (CRUD, 404s, error shape, keyword recommendation with an overridden
LLM). Service/endpoint tests run inside a rolled-back transaction so no test data
persists.

---

## Design principles honored

- Provider boundaries are the only abstractions; no over-engineering beyond them.
- AI prompts live in dedicated modules, separate from business logic.
- All LLM structured output is validated; malformed output is never silently accepted.
- The NVIDIA key is never exposed to the frontend.
- Research sources are never invented; visual recommendations are never presented
  as discovered assets.
- A working vertical slice (idea → script → visuals) over many half-features.
```
