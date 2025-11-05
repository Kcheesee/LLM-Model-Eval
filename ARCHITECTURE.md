# Model Eval Studio - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Homepage    │  │  Quick Eval  │  │  Evaluation Detail  │  │
│  │  Dashboard   │  │  Interface   │  │  Side-by-Side View  │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
│                            │                                     │
│                    ┌───────▼────────┐                          │
│                    │   API Client   │                          │
│                    │   (axios)      │                          │
│                    └───────┬────────┘                          │
└────────────────────────────┼─────────────────────────────────┘
                             │ HTTP/REST
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                    Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   API Routes                          │   │
│  │  /api/evaluations  /api/models  /api/quick-eval     │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                       │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │              Evaluation Engine                        │   │
│  │  • Orchestrates parallel model execution             │   │
│  │  • Captures metrics (time, tokens, cost)             │   │
│  │  • Manages async task execution                      │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                       │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │           Provider Abstraction Layer                  │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌─────────────┐  │   │
│  │  │  Anthropic   │ │   OpenAI     │ │   Google    │  │   │
│  │  │  Provider    │ │   Provider   │ │   Provider  │  │   │
│  │  └──────────────┘ └──────────────┘ └─────────────┘  │   │
│  └───────────────────────────┬──────────────────────────┘   │
│                               │                               │
│  ┌────────────────────────────▼─────────────────────────┐   │
│  │                  Database Layer                       │   │
│  │  • SQLAlchemy ORM                                     │   │
│  │  • Models: EvaluationRun, TestCase, ModelResponse    │   │
│  └───────────────────────────────────────────────────────┘   │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                    PostgreSQL Database                        │
│  Tables: evaluation_runs, test_cases, model_responses,       │
│          model_configs                                        │
└───────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Quick Evaluation Flow

```
User Input → Frontend Form → API Request → Evaluation Engine
                                                │
                        ┌───────────────────────┴───────────────────────┐
                        │                       │                       │
                        ▼                       ▼                       ▼
                 Anthropic Provider      OpenAI Provider        Google Provider
                        │                       │                       │
                        │ (Parallel Async)      │                       │
                        ▼                       ▼                       ▼
                  Claude API             OpenAI API            Gemini API
                        │                       │                       │
                        └───────────────────────┴───────────────────────┘
                                                │
                                                ▼
                                    Aggregate Results + Metrics
                                                │
                                                ▼
                                    Return to Frontend (JSON)
                                                │
                                                ▼
                                    Display Side-by-Side
```

### 2. Saved Evaluation Flow

```
User Creates Evaluation → Save to Database (pending status)
                                │
                                ▼
                    Trigger Background Task
                                │
                                ▼
                    For Each Test Case:
                      For Each Model:
                        - Execute API call
                        - Capture metrics
                        - Save ModelResponse to DB
                                │
                                ▼
                    Update EvaluationRun (completed status)
                                │
                                ▼
                    Frontend Fetches Results
                                │
                                ▼
                    Display with Summary Statistics
```

---

## Key Design Patterns

### 1. Provider Abstraction (Strategy Pattern)

**Purpose**: Decouple evaluation logic from specific LLM APIs

```python
# Base interface
class BaseProvider(ABC):
    @abstractmethod
    async def generate(prompt, model, **kwargs) -> ModelResponse

    @abstractmethod
    def calculate_cost(input_tokens, output_tokens) -> float

# Implementations
class AnthropicProvider(BaseProvider): ...
class OpenAIProvider(BaseProvider): ...
class GoogleProvider(BaseProvider): ...
```

**Benefits**:
- Add new providers without changing evaluation engine
- Consistent response format across all models
- Easy to test and mock

### 2. Async Parallel Execution

**Purpose**: Maximize throughput when evaluating multiple models

```python
# Gather multiple API calls
tasks = [provider.generate(...) for provider in providers]
results = await asyncio.gather(*tasks, return_exceptions=True)
```

**Benefits**:
- 3 models evaluated in ~same time as 1
- Non-blocking I/O during network requests
- Better resource utilization

### 3. Database-Backed Persistence

**Purpose**: Store evaluation history for analysis and reporting

```
EvaluationRun (1) ──┬──> (M) TestCase
                    │
                    └──> (M) ModelResponse

TestCase (1) ──> (M) ModelResponse
```

**Benefits**:
- Historical data for trend analysis
- Survives application restarts
- Enables reporting and exports

### 4. API Client Abstraction (Frontend)

**Purpose**: Centralized API communication with type safety

```typescript
// Typed API client
export const api = {
  async getAvailableModels(): Promise<AvailableModels>
  async createEvaluation(params): Promise<EvaluationRun>
  async quickEvaluation(params): Promise<QuickEvalResult[]>
}
```

**Benefits**:
- Type safety with TypeScript
- Single source of truth for API calls
- Easy to add caching or retry logic

---

## Technology Stack Rationale

### Backend: FastAPI
**Why?**
- Native async/await support (critical for parallel API calls)
- Automatic API documentation (Swagger/OpenAPI)
- Type hints with Pydantic (catches bugs early)
- High performance (comparable to Node.js/Go)

### Frontend: Next.js + React
**Why?**
- React ecosystem maturity
- TypeScript integration
- Server-side rendering capability (future: SEO)
- File-based routing (intuitive structure)

### Database: PostgreSQL
**Why?**
- ACID compliance (data integrity)
- Rich query capabilities (JSON support, aggregations)
- Production-proven at scale
- Better than SQLite for multi-user scenarios

### Styling: Tailwind CSS
**Why?**
- Rapid prototyping
- Consistent design system
- No CSS file management
- Easy to customize

---

## Scalability Considerations

### Current Limitations (MVP)
- Single-server deployment
- In-process background tasks
- No rate limiting per provider
- Limited to ~100 concurrent evaluations

### Scale-Up Path (Phase 2)
1. **Separate task queue** (Celery + Redis)
   - Move evaluation tasks off main API server
   - Better fault tolerance
   - Scale workers independently

2. **Caching layer** (Redis)
   - Cache identical prompts + model configs
   - Reduce redundant API calls
   - Lower costs

3. **Load balancer** (nginx)
   - Horizontal scaling of API servers
   - Better availability
   - SSL termination

4. **Rate limiting** (per-provider)
   - Respect API quotas
   - Prevent runaway costs
   - Queue management

---

## Security Considerations

### Current Implementation
- ✅ API keys stored in environment variables (not in code)
- ✅ CORS configured (prevents unauthorized origins)
- ✅ Database connection pooling (prevents exhaustion)
- ✅ No API keys exposed to frontend

### Production Hardening Needed
- [ ] Rate limiting on API endpoints
- [ ] User authentication (JWT tokens)
- [ ] API key encryption at rest
- [ ] Input sanitization (prevent injection)
- [ ] HTTPS enforcement
- [ ] Audit logging

---

## Future Architecture Enhancements

### Phase 2: Advanced Evaluation
```
┌─────────────────────────────────────┐
│      Custom Evaluation Metrics      │
│  ┌────────────┐  ┌───────────────┐ │
│  │ Bias Check │  │ Safety Score  │ │
│  └────────────┘  └───────────────┘ │
│  ┌────────────┐  ┌───────────────┐ │
│  │ Similarity │  │ Factual Check │ │
│  └────────────┘  └───────────────┘ │
└─────────────────────────────────────┘
```

### Phase 3: Team Collaboration
```
┌─────────────────────────────────────┐
│         User Management             │
│  • Organizations                    │
│  • Teams                            │
│  • Shared evaluations               │
│  • Role-based access                │
└─────────────────────────────────────┘
```

### Phase 4: Analytics & Reporting
```
┌─────────────────────────────────────┐
│      Analytics Dashboard            │
│  • Cost tracking over time          │
│  • Model performance trends         │
│  • Custom reports                   │
│  • Export to PDF/CSV                │
└─────────────────────────────────────┘
```

---

## Code Organization

```
Model Eval/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app + routes
│   │   ├── config.py            # Environment config
│   │   ├── database.py          # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── evaluation_engine.py # Core evaluation logic
│   │   └── providers/           # LLM provider integrations
│   │       ├── __init__.py
│   │       ├── base.py          # Abstract base class
│   │       ├── anthropic_provider.py
│   │       ├── openai_provider.py
│   │       └── google_provider.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # Next.js pages
│   │   │   ├── index.tsx        # Homepage
│   │   │   ├── quick-eval.tsx   # Quick evaluation
│   │   │   └── evaluations/     # Evaluation history
│   │   ├── components/          # Reusable components
│   │   ├── lib/
│   │   │   └── api.ts           # API client
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript types
│   │   └── styles/
│   │       └── globals.css      # Global styles
│   ├── package.json
│   └── .env.local
│
├── README.md
├── SETUP_GUIDE.md
├── QUICK_START.md
├── DEMO_SCRIPT.md
└── ARCHITECTURE.md (this file)
```

---

## Performance Characteristics

### API Response Times (Typical)
- Health check: ~5ms
- Get available models: ~10ms
- Create evaluation (DB write): ~50ms
- Quick evaluation (3 models): ~2-5 seconds (depends on model latency)
- Fetch evaluation results: ~100-500ms (depends on test case count)

### Resource Usage (Development)
- Backend: ~100MB RAM
- Frontend: ~200MB RAM (Next.js dev server)
- PostgreSQL: ~50MB RAM (minimal data)

### API Call Efficiency
- Parallel execution: 3 models = 1x slowest model time (not 3x)
- Token counting: Accurate from provider APIs
- Cost calculation: Real-time based on actual usage

---

## Testing Strategy

### Backend Tests (pytest)
- Unit tests: Provider implementations
- Integration tests: Evaluation engine
- API tests: Endpoint responses
- Database tests: Model relationships

### Frontend Tests (Jest + React Testing Library)
- Component tests: UI rendering
- Integration tests: API client
- E2E tests (future): Full user flows

---

## Monitoring & Observability (Production)

### Metrics to Track
- API latency (p50, p95, p99)
- Provider API success rate
- Token usage per provider
- Cost per evaluation
- Database query performance
- Error rates by endpoint

### Logging
- Structured JSON logs
- Provider API errors
- User actions (audit trail)
- Performance anomalies

---

**This architecture is designed to be:**
- ✅ **Extensible**: Easy to add providers, metrics, features
- ✅ **Testable**: Clear separation of concerns
- ✅ **Scalable**: Async-first, can grow horizontally
- ✅ **Maintainable**: Type-safe, well-documented, consistent patterns
