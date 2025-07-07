#!/bin/bash

# Start ngrok tunnel for Microsoft Graph webhook testing
echo "🌐 Starting ngrok tunnel for webhook testing..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Please run ./setup-ngrok.sh first"
    exit 1
fi

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  Backend not running on localhost:8000"
    echo "   Please start your FastAPI backend first:"
    echo "   cd backend && uvicorn app.main:app --reload --port 8000"
    echo ""
    echo "   Then run this script again."
    exit 1
fi

echo "✅ Backend is running on localhost:8000"
echo "🚀 Starting ngrok tunnel..."

# Start ngrok tunnel to localhost:8000
# Use HTTP tunnel for webhook testing
ngrok http 8000 --log=stdout 