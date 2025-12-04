# Model Eval Studio

A practical AI evaluation platform that helps companies evaluate and compare LLM performance on their specific use cases before committing to a model.

## 🎯 Purpose

Model Eval Studio solves a critical pain point for enterprise AI buyers: **How do you choose the right LLM for your specific use case?**

This tool enables:
- **Side-by-side model comparison** (Claude, GPT-4, Gemini, etc.)
- **Custom evaluation metrics** (accuracy, cost, latency, safety)
- **Bias and safety checks** (responsible AI evaluation)
- **Exportable reports** for stakeholder decision-making

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- Multi-provider LLM orchestration (Anthropic Claude, OpenAI, Google Gemini)
- Parallel evaluation execution
- Custom metrics engine
- PostgreSQL for evaluation run storage

### Frontend (React + TypeScript + Next.js)
- Intuitive test case input interface
- Real-time side-by-side comparison view
- Interactive metrics visualization
- PDF/CSV export for reports

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- API keys for: Anthropic Claude, OpenAI, Google Gemini (optional)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database credentials

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your backend API URL

# Start development server
npm run dev
```

Visit `http://localhost:3000` to access the application.

## 📊 Features

### Current (MVP)
- ✅ Multi-model support (Claude Sonnet, GPT-4, Gemini Pro)
- ✅ Parallel evaluation execution
- ✅ Comprehensive metrics: response time, token count, cost estimation
- ✅ Side-by-side comparison UI
- ✅ Evaluation history storage
- ✅ **Constitutional AI Evaluation** - Ethical assessment across 5 principles
- ✅ Quick evaluation mode for rapid testing
- ✅ Interactive Constitutional AI info modal

### Planned (Phase 2)
- 🔄 Custom evaluation criteria
- 🔄 Batch evaluation from CSV
- 🔄 Advanced visualizations (trend analysis, comparison charts)
- 🔄 PDF/CSV export
- 🔄 Team collaboration features
- 🔄 API rate limiting and authentication

## 🔑 API Keys

You'll need API keys from:
- **Anthropic**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Google AI Studio**: https://makersuite.google.com/app/apikey

## 📖 Use Cases

1. **Enterprise Procurement**: Compare models before signing contracts
2. **Use-Case Optimization**: Find the best model for specific tasks
3. **Cost Analysis**: Balance performance vs. API costs
4. **Safety Evaluation**: Test for bias and harmful outputs
5. **Migration Planning**: Evaluate alternatives when switching providers

## 🛡️ Responsible AI

Model Eval Studio includes built-in **Constitutional AI evaluation** powered by Anthropic's framework:
- **5 Ethical Principles**: Helpfulness, Harmlessness, Honesty, Respect, Clarity
- **Weighted Scoring**: 0-10 per principle with detailed explanations
- **Pass/Fail Thresholds**: Automatic quality gates at 7.0/10
- **Violation Tracking**: Detailed reasoning for any ethical concerns
- **Model Comparison**: See which models align best with your values
- **Transparency**: Full visibility into evaluation methodology

## 🤝 Contributing

Contributions welcome! Please fork the repository and submit a pull request.

## 📄 License

MIT License - see LICENSE file for details.
