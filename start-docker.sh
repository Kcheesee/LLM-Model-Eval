#!/bin/bash
# One-command Docker startup for Model Eval Studio

echo "🚀 Model Eval Studio - Docker Quick Start"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "Creating .env from template..."
    cp .env.docker .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys before continuing!"
    echo ""
    echo "Run this command to edit:"
    echo "  nano .env"
    echo ""
    echo "Add at least one API key, then run this script again."
    exit 1
fi

# Check if at least one API key is set
if ! grep -q "ANTHROPIC_API_KEY=sk-" .env && \
   ! grep -q "OPENAI_API_KEY=sk-" .env && \
   ! grep -q "GOOGLE_API_KEY=.\\+" .env; then
    echo "⚠️  No API keys found in .env file!"
    echo ""
    echo "Please edit .env and add at least one API key:"
    echo "  nano .env"
    echo ""
    exit 1
fi

echo "✅ Docker is running"
echo "✅ .env file found"
echo "✅ API keys configured"
echo ""

# Ask if user wants to rebuild
read -p "Rebuild containers? (recommended first time) [y/N]: " rebuild

if [[ $rebuild =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔨 Building containers (this may take 2-3 minutes first time)..."
    docker-compose up --build -d
else
    echo ""
    echo "🚀 Starting containers..."
    docker-compose up -d
fi

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check backend health
echo "Checking backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Backend taking longer than expected. Check logs:"
        echo "  docker-compose logs backend"
    fi
    sleep 1
done

# Check frontend
echo "Checking frontend..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Frontend taking longer than expected. Check logs:"
        echo "  docker-compose logs frontend"
    fi
    sleep 1
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Model Eval Studio is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Frontend:  http://localhost:3000"
echo "🔧 Backend:   http://localhost:8000"
echo "📖 API Docs:  http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f        # View logs"
echo "  docker-compose down           # Stop everything"
echo "  docker-compose restart backend # Restart backend"
echo ""
echo "Opening frontend in browser..."
sleep 2

# Open browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:3000
# Open browser (Linux)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:3000
    fi
# Windows (WSL)
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    start http://localhost:3000
fi

echo ""
echo "Press Ctrl+C to exit (containers will keep running)"
echo "To stop everything: docker-compose down"
echo ""

# Follow logs
docker-compose logs -f
