#!/bin/bash
# Start both backend and frontend in separate terminal windows (macOS)

echo "🚀 Starting Model Eval Studio..."
echo ""

# Get the directory of this script
DIR="$(cd "$(dirname "$0")" && pwd)"

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use Terminal.app
    echo "Opening backend in new terminal..."
    osascript -e "tell app \"Terminal\" to do script \"cd '$DIR' && bash start-backend.sh\""

    sleep 2

    echo "Opening frontend in new terminal..."
    osascript -e "tell app \"Terminal\" to do script \"cd '$DIR' && bash start-frontend.sh\""

    echo ""
    echo "✅ Both servers starting in separate terminal windows"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"

else
    # Linux or other - print instructions
    echo "⚠️  Automated terminal opening only works on macOS"
    echo ""
    echo "Please open two terminal windows manually:"
    echo ""
    echo "Terminal 1:"
    echo "  cd '$DIR' && bash start-backend.sh"
    echo ""
    echo "Terminal 2:"
    echo "  cd '$DIR' && bash start-frontend.sh"
fi
