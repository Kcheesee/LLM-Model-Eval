#!/bin/bash
# Start the Model Eval Studio frontend

echo "🚀 Starting Model Eval Studio Frontend..."
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local not found, copying from example..."
    cp .env.example .env.local
fi

# Start the server
echo "✅ Starting Next.js development server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
