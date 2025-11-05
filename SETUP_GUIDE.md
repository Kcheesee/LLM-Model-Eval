# Model Eval Studio - Complete Setup Guide

This guide will walk you through setting up Model Eval Studio from scratch.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** installed ([Download](https://www.python.org/downloads/))
- **Node.js 18+** installed ([Download](https://nodejs.org/))
- **PostgreSQL 14+** installed ([Download](https://www.postgresql.org/download/))
- **Git** installed
- API keys for at least one LLM provider (see below)

## Step 1: Get API Keys

You'll need API keys from the providers you want to evaluate:

### Anthropic Claude
1. Visit: https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy it (starts with `sk-ant-...`)

### OpenAI
1. Visit: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy it (starts with `sk-...`)

### Google Gemini
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy it

**Note**: You only need ONE API key to get started, but having multiple allows for better comparisons.

---

## Step 2: Set Up PostgreSQL Database

### Option A: Local PostgreSQL (Recommended for Development)

1. **Start PostgreSQL** (if not already running):
   ```bash
   # macOS (with Homebrew)
   brew services start postgresql@14

   # Linux
   sudo systemctl start postgresql

   # Windows
   # Start from Services or pg_ctl
   ```

2. **Create the database**:
   ```bash
   # Access PostgreSQL shell
   psql postgres

   # Create database and user
   CREATE DATABASE model_eval_db;
   CREATE USER model_eval_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE model_eval_db TO model_eval_user;
   \q
   ```

3. **Test connection**:
   ```bash
   psql -U model_eval_user -d model_eval_db -h localhost
   # Enter password when prompted
   # If successful, type \q to exit
   ```

### Option B: Using SQLite (Quick Start, No PostgreSQL Required)

If you want to skip PostgreSQL setup for quick testing:

1. Edit `backend/app/config.py` and change the DATABASE_URL default to:
   ```python
   DATABASE_URL: str = "sqlite:///./model_eval.db"
   ```

2. Install SQLite support:
   ```bash
   cd backend
   pip install aiosqlite
   ```

---

## Step 3: Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create Python virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate virtual environment**:
   ```bash
   # macOS/Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

6. **Edit `.env` file** with your API keys and database credentials:
   ```bash
   # Use your favorite editor (nano, vim, VS Code, etc.)
   nano .env
   ```

   Update these values:
   ```env
   # Database (adjust if you changed the password)
   DATABASE_URL=postgresql://model_eval_user:your_secure_password@localhost:5432/model_eval_db

   # Add your API keys (at least one)
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   OPENAI_API_KEY=sk-your-key-here
   GOOGLE_API_KEY=your-google-key-here

   # These can stay as defaults
   APP_ENV=development
   DEBUG=True
   SECRET_KEY=dev-secret-key-change-in-production
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

7. **Initialize the database**:
   ```bash
   # The tables will be created automatically on first run
   # You can test the backend now:
   uvicorn app.main:app --reload --port 8000
   ```

8. **Verify backend is running**:
   - Open browser to: http://localhost:8000
   - You should see: `{"status":"healthy","service":"Model Eval Studio API","version":"0.1.0"}`
   - Press `Ctrl+C` to stop (we'll start it again later)

---

## Step 4: Frontend Setup

1. **Open a NEW terminal** (keep backend terminal separate)

2. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Create environment file**:
   ```bash
   cp .env.example .env.local
   ```

5. **Edit `.env.local`** (usually the default is fine):
   ```bash
   nano .env.local
   ```

   Content should be:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

6. **Start the development server**:
   ```bash
   npm run dev
   ```

7. **Verify frontend is running**:
   - Open browser to: http://localhost:3000
   - You should see the Model Eval Studio homepage

---

## Step 5: Running the Complete Application

You need **TWO terminal windows** running simultaneously:

### Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Access the Application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated docs)

---

## Step 6: Test the Application

1. **Quick Evaluation Test**:
   - Go to http://localhost:3000/quick-eval
   - Select at least one model
   - Enter a prompt like: "Write a haiku about programming"
   - Click "Run Evaluation"
   - You should see responses from the selected models side-by-side

2. **Check for Errors**:
   - If you see errors, check both terminal windows for error messages
   - Common issues:
     - **"Provider not available"**: API key not set or invalid
     - **"Database connection failed"**: Check PostgreSQL is running and credentials are correct
     - **"CORS error"**: Make sure both servers are running on correct ports

---

## Troubleshooting

### Backend Issues

**Database connection errors**:
```bash
# Check PostgreSQL is running
psql postgres -c "SELECT version();"

# Verify database exists
psql postgres -c "\l" | grep model_eval_db
```

**API key errors**:
- Verify keys are correct in `backend/.env`
- Make sure there are no extra spaces or quotes
- Test API keys directly with provider's documentation

**Module not found errors**:
```bash
# Make sure venv is activated
which python  # Should show path to venv

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Cannot connect to backend**:
- Verify backend is running on port 8000
- Check `frontend/.env.local` has correct API URL
- Try accessing http://localhost:8000 directly

**Module not found errors**:
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Next Steps

Now that everything is set up:

1. **Try Quick Eval**: Test different prompts and models
2. **Create Saved Evaluations**: Build comprehensive test suites
3. **Compare Performance**: Analyze metrics across models
4. **Customize**: Add your own models or evaluation criteria

---

## Production Deployment

For deploying to production, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) (coming soon).

Key considerations:
- Use proper PostgreSQL database (not SQLite)
- Set strong `SECRET_KEY` in backend
- Use environment-specific API keys
- Enable HTTPS
- Set `DEBUG=False` in production

---

## Need Help?

- Check the main [README.md](./README.md) for architecture overview
- Review the API documentation at http://localhost:8000/docs
- Check both terminal windows for error messages

---

**Happy Evaluating! 🚀**
