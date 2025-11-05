# 🤖 Model Eval Studio

> **A practical AI evaluation platform that helps enterprises compare LLMs side-by-side before making procurement decisions.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)

[Live Demo](#) | [Documentation](./ARCHITECTURE.md) | [Quick Start](#-quick-start)

---

## 🎯 The Problem

Enterprise AI buyers face a critical challenge: **How do you objectively compare Claude, GPT-4, and Gemini on your specific use cases before committing to a 6-7 figure contract?**

Manual evaluation means:
- ❌ Copy-pasting prompts across 3+ different interfaces
- ❌ No systematic tracking of response time, cost, or token usage
- ❌ Lost evaluation data after each session
- ❌ Difficult to justify decisions to stakeholders

---

## ✨ The Solution

Model Eval Studio automates LLM evaluation with:

- ✅ **Side-by-side comparison** of Claude, GPT-4, and Gemini
- ✅ **Parallel execution** - evaluate 3 models in the time of 1
- ✅ **Comprehensive metrics** - latency, tokens, cost per request
- ✅ **Persistent storage** - build a library of test cases
- ✅ **Enterprise-ready UI** - built for business decision-makers

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/model-eval-studio.git
cd model-eval-studio

# 2. Set up API keys
cp .env.docker .env
# Edit .env and add your API keys

# 3. Start everything
./start-docker.sh

# Open http://localhost:3000 🎉
```

### Option 2: Manual Setup

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed instructions.

---

## 📸 Screenshots

### Quick Evaluation
![Quick Eval Screenshot](./docs/screenshots/quick-eval.png)
*Compare multiple models on a single prompt in seconds*

### Side-by-Side Comparison
![Comparison Screenshot](./docs/screenshots/comparison.png)
*Detailed metrics for response time, token usage, and cost*

### Evaluation History
![History Screenshot](./docs/screenshots/history.png)
*Track and review past evaluations*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│              TypeScript + React + Tailwind CSS              │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────▼──────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                  Async Evaluation Engine                     │
└────────┬──────────────┬──────────────┬──────────────────────┘
         │              │              │
    ┌────▼────┐    ┌────▼────┐   ┌────▼────┐
    │ Claude  │    │  GPT-4  │   │ Gemini  │
    │   API   │    │   API   │   │   API   │
    └─────────┘    └─────────┘   └─────────┘
```

**Key Technical Features:**
- **Async Python** with FastAPI for concurrent API calls
- **Provider abstraction** pattern for easy extensibility
- **PostgreSQL** for evaluation history and analytics
- **Type-safe** with Pydantic (backend) and TypeScript (frontend)

[Full Architecture Details →](./ARCHITECTURE.md)

---

## 💻 Tech Stack

| Category | Technology |
|----------|-----------|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.0 |
| **Database** | PostgreSQL 14 |
| **LLM APIs** | Anthropic Claude, OpenAI GPT-4, Google Gemini |
| **Deployment** | Docker, Docker Compose |
| **Testing** | pytest, Jest, React Testing Library |

---

## 📊 Use Cases

### 1. Enterprise Procurement
Before signing a $200K annual AI contract, run your actual use cases through all providers. Make data-driven decisions backed by real metrics.

### 2. Use-Case Optimization
Discover that Claude Haiku handles 60% of your tasks at 1/10th the cost of GPT-4. Optimize spending without sacrificing quality.

### 3. Migration Planning
Moving from OpenAI to Anthropic? Validate output quality on your specific prompts before switching.

### 4. Sales Engineering
Anthropic/OpenAI sales teams can demo head-to-head comparisons using customer's own data. Faster sales cycles, higher conversion.

---

## 🎓 What's Impressive Here

### For Engineering Roles:
- **Clean architecture** - Provider abstraction pattern, dependency injection
- **Async mastery** - Parallel API execution with asyncio.gather
- **Type safety** - Full type coverage (Pydantic + TypeScript)
- **Production-ready** - Docker, environment config, error handling

### For Customer Success/Solutions Engineering:
- **Product thinking** - Solves real business pain point
- **Enterprise focus** - Built for decision-makers, not just developers
- **Demo-ready** - Professional UI suitable for stakeholder presentations
- **Metrics-driven** - Shows cost/latency data that CFOs care about

### For AI/ML Roles:
- **Multi-LLM orchestration** - Practical integration patterns
- **Evaluation framework** - Foundation for bias/safety checks
- **Cost awareness** - Real-time token tracking and pricing
- **Responsible AI** - Designed with evaluation rigor in mind

---

## 🔮 Roadmap

### Phase 2: Advanced Evaluation (Q2 2025)
- [ ] Custom evaluation metrics (accuracy scoring, semantic similarity)
- [ ] Bias detection across demographic categories
- [ ] Safety/toxicity filtering
- [ ] Batch evaluation from CSV uploads

### Phase 3: Team Collaboration (Q3 2025)
- [ ] User authentication and authorization
- [ ] Organizations and team workspaces
- [ ] Shared evaluation libraries
- [ ] Role-based access control

### Phase 4: Analytics (Q4 2025)
- [ ] Cost tracking dashboards over time
- [ ] Performance trend analysis
- [ ] PDF/CSV report exports
- [ ] API for third-party integrations

---

## 📚 Documentation

- [Quick Start Guide](./QUICK_START.md) - Get running in 5 minutes
- [Setup Guide](./SETUP_GUIDE.md) - Detailed installation instructions
- [Docker Setup](./DOCKER_SETUP.md) - Container-based deployment
- [Architecture](./ARCHITECTURE.md) - Technical deep dive
- [Demo Script](./DEMO_SCRIPT.md) - How to present this project
- [Project Summary](./PROJECT_SUMMARY.md) - Complete project overview

---

## 🤝 Contributing

This is primarily a portfolio/demo project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 About the Author

**Kareem (Jack) Almac**

I built Model Eval Studio to showcase:
- Full-stack engineering expertise (Python, TypeScript, React)
- Product thinking that solves real business problems
- Understanding of enterprise AI adoption challenges
- Ability to build tools that accelerate sales and customer success

**Connect with me:**
- LinkedIn: [Your LinkedIn URL]
- Portfolio: [Your Portfolio URL]
- Email: [Your Email]

---

## 🙏 Acknowledgments

- **Anthropic, OpenAI, Google** - For building amazing LLMs
- **FastAPI & Next.js communities** - For excellent frameworks
- **Enterprise AI buyers** - For inspiring this solution

---

## ⭐ Star this repo if you find it helpful!

Built with ❤️ and ☕ by [Jack Almac](https://github.com/yourusername)

---

<div align="center">

**[⬆ Back to Top](#-model-eval-studio)**

</div>
