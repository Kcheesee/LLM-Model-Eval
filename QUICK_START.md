# Quick Start - Get Running in 5 Minutes

The fastest way to get Model Eval Studio up and running.

## Prerequisites Checklist
- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] At least ONE API key (Anthropic, OpenAI, or Google)

## Step 1: Clone & Install (2 minutes)

```bash
# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (open new terminal)
cd frontend
npm install
```

## Step 2: Configure (1 minute)

```bash
# Backend - create .env file
cd backend
cp .env.example .env
# Edit .env and add your API key(s)

# Frontend - create .env.local
cd frontend
cp .env.example .env.local
# Default values are fine for local development
```

### Using SQLite (Skip PostgreSQL)

For quickest start, edit `backend/.env`:

```env
DATABASE_URL=sqlite:///./model_eval.db
ANTHROPIC_API_KEY=your-key-here
```

Then install SQLite support:
```bash
cd backend
pip install aiosqlite
```

## Step 3: Run (2 minutes)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step 4: Test

Visit http://localhost:3000

Click "Quick Compare", enter a prompt, and select models!

---

## Troubleshooting

**Backend won't start?**
- Check you added at least one API key to `backend/.env`
- Verify virtual environment is activated (`which python` should show venv path)

**Frontend won't start?**
- Run `npm install` again
- Check Node.js version: `node --version` (should be 18+)

**Models not working?**
- Verify API keys are correct (no extra spaces)
- Test keys at provider's website first

---

**Full setup guide**: See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for PostgreSQL and detailed instructions.
