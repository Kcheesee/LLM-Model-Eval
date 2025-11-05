# 🎯 Demo Day Checklist

Use this checklist before presenting Model Eval Studio to ensure a smooth demo.

---

## 📋 Pre-Demo Setup (Do This 1 Hour Before)

### ✅ Environment Check
- [ ] Docker Desktop is running
- [ ] All API keys are valid and working
  - Test at: https://console.anthropic.com/, https://platform.openai.com/, etc.
- [ ] `.env` file has at least 2 API keys configured
- [ ] No conflicting services on ports 3000, 5432, or 8000

### ✅ Start the Application
```bash
./start-docker.sh
# Wait for "Frontend is ready!" and "Backend is ready!"
```

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend responds at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs

### ✅ Verify Core Features
- [ ] Homepage loads correctly
- [ ] "Quick Compare" button works
- [ ] Model selection shows at least 2 models
- [ ] Test with simple prompt: "Write a haiku about programming"
- [ ] Results display side-by-side with metrics

### ✅ Prepare Demo Content

**Have these ready:**

1. **Opening prompt** (use this for impact):
```
Write a professional email to a customer explaining a 2-hour service outage.
The email should be empathetic, clear, and include what we're doing to prevent future issues.
```

2. **Backup prompts** (if audience wants more):
```
- Summarize the following customer support ticket in 2-3 sentences: [paste sample ticket]
- Write Python code to find the 10th Fibonacci number using recursion
- Translate this technical documentation into simple language for non-engineers: [paste sample]
```

3. **Talking points document** - Have [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) open in another window

---

## 🖥️ During Demo Setup (Do This 10 Minutes Before)

### ✅ Browser Preparation
- [ ] Open Chrome/Firefox in a clean profile (no distracting bookmarks/extensions)
- [ ] Open these tabs:
  1. http://localhost:3000 (Homepage)
  2. http://localhost:3000/quick-eval (Quick Eval ready to go)
  3. http://localhost:8000/docs (Backend API docs - optional)
- [ ] Zoom browser to 125-150% for better visibility on projector
- [ ] Close all other tabs
- [ ] Turn off notifications (Do Not Disturb mode)

### ✅ Code Editor Preparation (If Showing Code)
- [ ] Open VS Code with the project
- [ ] Have these files ready to show:
  - `backend/app/providers/base.py` (Provider abstraction)
  - `backend/app/evaluation_engine.py` (Parallel execution)
  - `docker-compose.yml` (Easy deployment)
- [ ] Set font size to 16-18pt for visibility

### ✅ Terminal Preparation
- [ ] One terminal showing: `docker-compose logs -f` (live logs)
- [ ] Font size 14-16pt
- [ ] Optional: Show Docker Desktop dashboard with running containers

---

## 🎤 Demo Flow Checklist

### Part 1: The Problem (30 seconds)
- [ ] "Enterprises spend millions on AI without good comparison tools"
- [ ] "Manual evaluation is time-consuming and error-prone"
- [ ] "No way to track metrics like cost and latency systematically"

### Part 2: The Solution (1 minute)
- [ ] Show homepage - point out clean, professional UI
- [ ] Click "Quick Compare"
- [ ] Show model selection - "Supports Claude, GPT-4, Gemini"
- [ ] Mention: "Built for enterprise decision-makers, not just developers"

### Part 3: Live Demo (2-3 minutes)
- [ ] Paste prepared prompt
- [ ] Select 2-3 models (Claude Sonnet, GPT-4, Gemini)
- [ ] Click "Run Evaluation"
- [ ] **While it's running**, explain parallel execution
- [ ] When results appear:
  - [ ] Point out side-by-side layout
  - [ ] Highlight response time differences
  - [ ] Show token counts
  - [ ] **Emphasize cost per request** - "This is what CFOs care about"

### Part 4: Technical Deep Dive (1-2 minutes, if time)
- [ ] Switch to VS Code
- [ ] Show `providers/base.py` - "Clean abstraction pattern"
- [ ] Show `docker-compose.yml` - "One command deployment"
- [ ] Mention: "Async architecture means 3 models evaluated in same time as 1"

### Part 5: Business Value (1 minute)
- [ ] Use cases: Procurement, optimization, migration
- [ ] "This tool could save enterprises 30-50% on AI costs"
- [ ] "Directly applicable to customer success and sales engineering"

### Part 6: Q&A Prep
- [ ] Be ready to answer:
  - "How long did this take to build?" → ~8 hours
  - "Could this be a real product?" → Absolutely, clear market need
  - "What about bias/safety?" → Phase 2 roadmap, leveraging TrustChain patterns
  - "How does it scale?" → Async architecture, can handle 100+ concurrent evals

---

## 🚨 Troubleshooting During Demo

### If models don't load:
**Likely cause**: API keys not set
**Fix**: Check `.env` file, restart containers
**Backup**: Show screenshots from `docs/screenshots/` folder

### If responses are slow:
**Likely cause**: Model API latency (normal)
**Response**: "This is real-world latency - one of the metrics we're evaluating!"

### If Docker crashes:
**Backup plan**: Have screenshots ready
**Prevention**: Test everything 1 hour before demo

### If audience asks about a feature you haven't built:
**Response**: "That's a great idea! That's actually on the Phase 2 roadmap. Right now I focused on the core evaluation workflow, but [feature] would be a natural extension."

---

## 📸 Backup Screenshots

**If live demo fails, have these ready:**

Create a `docs/screenshots/` folder with:
1. `homepage.png` - Main dashboard
2. `quick-eval-setup.png` - Model selection screen
3. `quick-eval-results.png` - Side-by-side comparison with metrics
4. `architecture-diagram.png` - System architecture
5. `code-providers.png` - Screenshot of provider abstraction code

---

## 🎯 Success Metrics

After the demo, you want to hear:
- ✅ "This solves a real problem we have"
- ✅ "The architecture is clean and scalable"
- ✅ "I can see this being used by our sales team"
- ✅ "You clearly understand enterprise needs"

---

## ⏰ Time Allocation

**5-Minute Version:**
- Problem: 30 seconds
- Solution overview: 30 seconds
- Live demo: 2-3 minutes
- Business value: 1 minute
- Q&A: 1 minute

**10-Minute Version:**
- Problem: 1 minute
- Solution overview: 1 minute
- Live demo: 3-4 minutes
- Technical architecture: 2-3 minutes
- Business value: 2 minutes
- Q&A: 2 minutes

---

## 📝 Post-Demo Follow-Up

After a successful demo:
- [ ] Send link to GitHub repo
- [ ] Offer to deploy a demo instance they can try
- [ ] Share the [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) document
- [ ] Connect on LinkedIn

---

## 💡 Pro Tips

1. **Energy matters** - Be enthusiastic about the problem you're solving
2. **Business first** - Lead with value, not just technology
3. **Know your audience** - Engineers want code, execs want ROI
4. **Handle failures gracefully** - "Here's what I'd do to debug this..."
5. **Time-box technical depth** - Don't get lost in the weeds unless asked

---

## 🧘 Mindset Going In

Remember:
- ✅ You built a production-ready application in hours
- ✅ You solved a real business problem
- ✅ You can explain both the tech AND the business value
- ✅ Even if something breaks, your code and docs speak for themselves

**You've got this! 🚀**

---

## ✅ Final Check (5 Minutes Before)

- [ ] Application is running and tested
- [ ] Browser tabs are ready
- [ ] Demo prompts are prepared
- [ ] Notifications are off
- [ ] Water nearby (stay hydrated!)
- [ ] Deep breath - you're ready!

**Now go impress them!** 💪
