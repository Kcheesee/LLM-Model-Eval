# Model Eval Studio - Project Structure

Complete file tree and description of all components.

---

## 📁 Project Tree

```
Model Eval/
│
├── 📄 README.md                    # Main project documentation
├── 📄 README_GITHUB.md             # Optimized README for GitHub showcase
├── 📄 PROJECT_SUMMARY.md           # Executive summary and talking points
├── 📄 ARCHITECTURE.md              # Technical architecture deep dive
├── 📄 SETUP_GUIDE.md               # Detailed installation instructions
├── 📄 QUICK_START.md               # 5-minute quick start guide
├── 📄 DOCKER_SETUP.md              # Docker deployment guide
├── 📄 DEMO_SCRIPT.md               # Presentation guide
├── 📄 DEMO_CHECKLIST.md            # Pre-demo checklist
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 🐳 docker-compose.yml           # Docker orchestration config
├── 📄 .env.docker                  # Docker environment template
│
├── 🔧 start-docker.sh              # One-command Docker startup
├── 🔧 start-all.sh                 # Start backend + frontend (macOS)
├── 🔧 start-backend.sh             # Start backend only
├── 🔧 start-frontend.sh            # Start frontend only
│
├── 📁 backend/                     # FastAPI Backend
│   ├── 📄 Dockerfile               # Backend container config
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 .env.example             # Environment variables template
│   ├── 📄 .gitignore               # Git ignore rules
│   │
│   └── 📁 app/                     # Main application code
│       ├── 📄 __init__.py          # Package initialization
│       ├── 📄 main.py              # FastAPI app + routes
│       ├── 📄 config.py            # Configuration management
│       ├── 📄 database.py          # Database connection setup
│       ├── 📄 models.py            # SQLAlchemy database models
│       ├── 📄 schemas.py           # Pydantic request/response schemas
│       ├── 📄 evaluation_engine.py # Core evaluation orchestration
│       │
│       └── 📁 providers/           # LLM provider integrations
│           ├── 📄 __init__.py      # Provider exports
│           ├── 📄 base.py          # Abstract base provider class
│           ├── 📄 anthropic_provider.py  # Anthropic Claude integration
│           ├── 📄 openai_provider.py     # OpenAI GPT integration
│           └── 📄 google_provider.py     # Google Gemini integration
│
└── 📁 frontend/                    # Next.js Frontend
    ├── 📄 Dockerfile               # Frontend container config
    ├── 📄 package.json             # Node.js dependencies
    ├── 📄 tsconfig.json            # TypeScript configuration
    ├── 📄 next.config.js           # Next.js configuration
    ├── 📄 tailwind.config.js       # Tailwind CSS configuration
    ├── 📄 postcss.config.js        # PostCSS configuration
    ├── 📄 .env.example             # Environment variables template
    ├── 📄 .gitignore               # Git ignore rules
    │
    └── 📁 src/                     # Source code
        ├── 📁 pages/               # Next.js pages (routes)
        │   ├── 📄 _app.tsx         # App wrapper component
        │   ├── 📄 index.tsx        # Homepage/Dashboard
        │   ├── 📄 quick-eval.tsx   # Quick evaluation interface
        │   └── 📁 evaluations/     # Evaluation history routes
        │       ├── 📄 index.tsx    # Evaluation list page
        │       └── 📄 [id].tsx     # Individual evaluation detail
        │
        ├── 📁 lib/                 # Shared libraries
        │   └── 📄 api.ts           # API client (axios wrapper)
        │
        ├── 📁 types/               # TypeScript type definitions
        │   └── 📄 index.ts         # Shared types
        │
        └── 📁 styles/              # Global styles
            └── 📄 globals.css      # Tailwind CSS + global styles
```

---

## 📋 File Descriptions

### Documentation Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `README.md` | Main project overview | First file users see |
| `README_GITHUB.md` | GitHub showcase version | Copy to README when publishing |
| `PROJECT_SUMMARY.md` | Executive summary | Sending to recruiters/stakeholders |
| `ARCHITECTURE.md` | Technical deep dive | Technical interviews, code reviews |
| `SETUP_GUIDE.md` | Detailed setup | First-time installation |
| `QUICK_START.md` | 5-minute quickstart | Quick demos, testing |
| `DOCKER_SETUP.md` | Docker deployment | Production/demo setup |
| `DEMO_SCRIPT.md` | Presentation guide | Before demos/interviews |
| `DEMO_CHECKLIST.md` | Pre-demo checklist | Day-of demo prep |

### Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Orchestrates 3 containers (frontend, backend, database) |
| `.env.docker` | Environment variable template for Docker |
| `backend/.env.example` | Backend environment template |
| `frontend/.env.example` | Frontend environment template |

### Scripts

| Script | Purpose |
|--------|---------|
| `start-docker.sh` | One-command Docker startup with health checks |
| `start-all.sh` | Start backend + frontend in separate terminals (macOS) |
| `start-backend.sh` | Start backend only (manual setup) |
| `start-frontend.sh` | Start frontend only (manual setup) |

---

## 🔧 Backend Structure

### Core Files

**`app/main.py`** (265 lines)
- FastAPI application setup
- API route definitions
- CORS middleware configuration
- Background task management
- Endpoints:
  - `GET /` - Health check
  - `GET /api/models` - List available models
  - `POST /api/evaluations` - Create evaluation
  - `GET /api/evaluations` - List evaluations
  - `GET /api/evaluations/{id}` - Get evaluation details
  - `DELETE /api/evaluations/{id}` - Delete evaluation
  - `POST /api/quick-eval` - Quick one-off evaluation

**`app/evaluation_engine.py`** (185 lines)
- Core orchestration logic
- Parallel model execution with `asyncio.gather`
- Metrics collection (time, tokens, cost)
- Database persistence
- Summary statistics generation

**`app/models.py`** (95 lines)
- SQLAlchemy ORM models:
  - `EvaluationRun` - Top-level evaluation session
  - `TestCase` - Individual test prompts
  - `ModelResponse` - Model outputs with metrics
  - `ModelConfig` - Saved model configurations

**`app/schemas.py`** (80 lines)
- Pydantic models for API validation
- Request/response schemas
- Type-safe data transfer objects

**`app/config.py`** (60 lines)
- Environment variable management
- API key storage
- Cost pricing configuration
- Settings singleton pattern

**`app/database.py`** (40 lines)
- Database connection setup
- Session management
- Dependency injection for FastAPI

### Provider Implementations

**`app/providers/base.py`** (75 lines)
- Abstract base class for all providers
- Standardized interface:
  - `async generate()` - Main API call method
  - `calculate_cost()` - Cost estimation
  - `get_available_models()` - Model listing
- Common response format

**`app/providers/anthropic_provider.py`** (95 lines)
- Anthropic Claude integration
- Supports: Claude Sonnet 4, Opus, Haiku
- Token counting and cost calculation
- Error handling

**`app/providers/openai_provider.py`** (95 lines)
- OpenAI GPT integration
- Supports: GPT-4 Turbo, GPT-4, GPT-3.5
- Token counting and cost calculation
- Error handling

**`app/providers/google_provider.py`** (100 lines)
- Google Gemini integration
- Supports: Gemini Pro, 1.5 Pro, 1.5 Flash
- Approximate token counting (Gemini doesn't expose exact counts)
- Error handling

---

## 🎨 Frontend Structure

### Pages

**`src/pages/index.tsx`** (210 lines)
- Homepage/Dashboard
- Features overview
- Recent evaluations list
- Navigation to main features

**`src/pages/quick-eval.tsx`** (265 lines)
- Quick evaluation interface
- Model selection (checkboxes)
- Parameter controls (temperature, max tokens)
- Single prompt input
- Side-by-side results display
- Real-time loading states

**`src/pages/evaluations/index.tsx`** (145 lines)
- Evaluation history list
- Delete functionality
- Status badges (pending/running/completed/failed)
- Navigation to detail pages

**`src/pages/evaluations/[id].tsx`** (240 lines)
- Individual evaluation detail page
- Summary statistics by model
- Test case selector (if multiple)
- Side-by-side response comparison
- Metrics display (time, tokens, cost)

### Supporting Files

**`src/lib/api.ts`** (90 lines)
- Centralized API client using axios
- Type-safe API methods
- Base URL configuration
- Error handling

**`src/types/index.ts`** (75 lines)
- TypeScript type definitions
- Matches backend Pydantic schemas
- Ensures type safety across frontend

**`src/styles/globals.css`** (30 lines)
- Tailwind CSS imports
- Global CSS variables
- Dark mode support

---

## 📊 Statistics

### Lines of Code

| Category | Files | Lines (approx) |
|----------|-------|----------------|
| **Backend Python** | 12 | ~1,200 |
| **Frontend TypeScript** | 9 | ~1,500 |
| **Documentation** | 9 | ~3,500 |
| **Config/Scripts** | 10 | ~500 |
| **TOTAL** | 40 | **~6,700** |

### Technology Breakdown

| Technology | Usage |
|------------|-------|
| Python | 18% |
| TypeScript/React | 22% |
| Markdown (Docs) | 52% |
| Config (YAML, JSON, Shell) | 8% |

---

## 🔍 Key Features by File

### Parallel Execution
- Implemented in: `backend/app/evaluation_engine.py`
- Lines: 135-155
- Uses: `asyncio.gather()` for concurrent API calls

### Provider Abstraction
- Base class: `backend/app/providers/base.py`
- Implementations: `anthropic_provider.py`, `openai_provider.py`, `google_provider.py`
- Pattern: Abstract Base Class with async methods

### Cost Calculation
- Implemented in: Each provider's `calculate_cost()` method
- Pricing data: `backend/app/config.py` (lines 30-36)
- Real-time display: `frontend/src/pages/quick-eval.tsx` (lines 180-190)

### Database Persistence
- Models: `backend/app/models.py`
- Connection: `backend/app/database.py`
- Queries: Embedded in `main.py` route handlers

### Type Safety
- Backend: Pydantic models in `schemas.py`
- Frontend: TypeScript types in `src/types/index.ts`
- Ensures end-to-end type checking

---

## 🚀 Running the Project

### Option 1: Docker (Easiest)
```bash
./start-docker.sh
```
Starts all 3 services in containers.

### Option 2: Manual
**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📦 Dependencies

### Backend (27 packages)
- **Core**: fastapi, uvicorn, sqlalchemy, pydantic
- **LLM APIs**: anthropic, openai, google-generativeai
- **Database**: psycopg2-binary (PostgreSQL driver)
- **Async**: httpx, python-multipart
- **Testing**: pytest, pytest-asyncio

### Frontend (15 packages)
- **Core**: react, next, typescript
- **UI**: tailwindcss, lucide-react (icons)
- **API**: axios
- **Markdown**: react-markdown
- **Utils**: clsx

---

## 🎯 What Makes This Impressive

### Architecture Choices
1. **Provider abstraction** - Easy to add new LLMs
2. **Async everywhere** - Maximum performance
3. **Type safety** - Catches bugs at compile time
4. **Docker-ready** - One command deployment
5. **Clean separation** - Backend/Frontend fully decoupled

### Code Quality
- Consistent naming conventions
- Comprehensive docstrings
- Error handling at every layer
- Environment-based configuration
- No hardcoded values

### Documentation
- 9 comprehensive markdown files
- 3,500+ lines of documentation
- Setup guides for multiple skill levels
- Architecture diagrams and explanations

---

**This project demonstrates professional-grade software engineering, not just a quick prototype.**
