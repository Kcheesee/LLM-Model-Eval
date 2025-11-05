# Docker Setup - EASIEST Way to Run Model Eval Studio

Using Docker is the **fastest and most reliable** way to run Model Eval Studio. Everything is containerized - no need to install Python, Node.js, or PostgreSQL manually!

## Prerequisites

- **Docker Desktop** installed ([Download](https://www.docker.com/products/docker-desktop))
- At least ONE API key (Anthropic, OpenAI, or Google)

## Quick Start (3 Steps!)

### Step 1: Set Up API Keys (1 minute)

```bash
# Copy the environment template
cp .env.docker .env

# Edit .env and add your API key(s)
nano .env  # or use any text editor
```

Add at least one API key:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-google-key-here
```

### Step 2: Start Everything (1 minute)

```bash
# Build and start all services (backend, frontend, database)
docker-compose up --build
```

**Wait for these messages:**
```
✅ backend  | INFO:     Application startup complete.
✅ frontend | ready - started server on 0.0.0.0:3000
✅ db       | database system is ready to accept connections
```

### Step 3: Access the App

Open your browser to: **http://localhost:3000**

That's it! Everything is running. 🎉

---

## What Just Happened?

Docker Compose started 3 containers:

1. **PostgreSQL Database** (port 5432)
   - Fully configured and ready
   - Data persists in Docker volume

2. **Backend API** (port 8000)
   - FastAPI server with all dependencies
   - Connected to database
   - API docs at: http://localhost:8000/docs

3. **Frontend** (port 3000)
   - Next.js development server
   - Connected to backend
   - Live reload enabled

---

## Common Commands

### Stop the application:
```bash
docker-compose down
```

### Stop AND delete all data:
```bash
docker-compose down -v
```

### View logs:
```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend
docker-compose logs -f frontend
```

### Restart a specific service:
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild after code changes:
```bash
docker-compose up --build
```

---

## Troubleshooting

### "Port already in use" errors

**Problem**: Another service is using port 3000, 5432, or 8000

**Solution**: Stop the conflicting service or change ports in `docker-compose.yml`

```yaml
# Example: Change frontend port to 3001
frontend:
  ports:
    - "3001:3000"  # Change the first number
```

### "Cannot connect to backend" errors

**Check backend is healthy:**
```bash
curl http://localhost:8000
# Should return: {"status":"healthy",...}
```

**View backend logs:**
```bash
docker-compose logs backend
```

### API key errors

**Verify keys are loaded:**
```bash
docker-compose exec backend env | grep API_KEY
```

**If empty, check your `.env` file** and restart:
```bash
docker-compose down
docker-compose up
```

### Database connection errors

**Reset database:**
```bash
docker-compose down -v  # Deletes volumes
docker-compose up --build
```

---

## Development Workflow with Docker

### Making Backend Changes

1. Edit files in `backend/` directory
2. Backend auto-reloads (thanks to `--reload` flag)
3. Changes take effect immediately (no restart needed)

### Making Frontend Changes

1. Edit files in `frontend/src/` directory
2. Frontend auto-reloads (Next.js Fast Refresh)
3. Changes appear in browser immediately

### Installing New Dependencies

**Backend (Python):**
```bash
# Add to backend/requirements.txt, then:
docker-compose down
docker-compose up --build
```

**Frontend (Node.js):**
```bash
# Add to frontend/package.json, then:
docker-compose down
docker-compose up --build
```

---

## For Demo/Presentation

### Before Demo Starts:

```bash
# Start everything
docker-compose up -d  # -d runs in background

# Verify everything is healthy
docker-compose ps

# Open browser to http://localhost:3000
```

### During Demo:

Everything runs smoothly - no need to manage multiple terminals!

### After Demo:

```bash
# Stop everything
docker-compose down
```

---

## Production Deployment

For production use, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) which covers:
- Building production images
- Using managed PostgreSQL
- Environment variable security
- SSL/HTTPS setup
- Container orchestration (Kubernetes, ECS, etc.)

---

## Why Docker Is Better for Demos

**Without Docker:**
- ❌ Install Python, Node.js, PostgreSQL
- ❌ Create virtual environments
- ❌ Manage 2-3 terminal windows
- ❌ Debug environment issues
- ❌ "Works on my machine" problems

**With Docker:**
- ✅ One command: `docker-compose up`
- ✅ Consistent environment everywhere
- ✅ Easy cleanup: `docker-compose down`
- ✅ No global dependencies
- ✅ Guaranteed to work same way every time

---

## Docker Compose Architecture

```
┌─────────────────────────────────────────────┐
│           Docker Compose Network            │
│                                             │
│  ┌────────────┐      ┌─────────────┐      │
│  │  Frontend  │─────▶│   Backend   │      │
│  │  (Next.js) │      │  (FastAPI)  │      │
│  │  Port 3000 │      │  Port 8000  │      │
│  └────────────┘      └──────┬──────┘      │
│                              │              │
│                              ▼              │
│                      ┌───────────────┐     │
│                      │  PostgreSQL   │     │
│                      │  Port 5432    │     │
│                      └───────────────┘     │
│                                             │
└─────────────────────────────────────────────┘
```

All containers can communicate with each other by service name!

---

## Next Steps

Once running, try:
1. **Quick Eval**: http://localhost:3000/quick-eval
2. **API Docs**: http://localhost:8000/docs (interactive API explorer)
3. **Health Check**: http://localhost:8000 (backend status)

Happy evaluating! 🚀
