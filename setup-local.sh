#!/bin/bash

echo "🚀 Setting up local development environment..."

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local from template..."
    cp env.example .env.local
    echo "✅ .env.local created. Please edit it with your actual values."
else
    echo "✅ .env.local already exists."
fi

# Check if Supabase is installed
if ! command -v supabase &> /dev/null; then
    echo "📦 Installing Supabase CLI..."
    npm install -g supabase
else
    echo "✅ Supabase CLI already installed."
fi

# Check if Python dependencies are installed
if [ ! -f api/venv ]; then
    echo "🐍 Setting up Python virtual environment..."
    cd api
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo "✅ Python dependencies installed."
else
    echo "✅ Python virtual environment already exists."
fi

echo ""
echo "🎯 Next steps:"
echo "1. Edit .env.local with your actual environment variables"
echo "2. Start Supabase locally: npx supabase start"
echo "3. Apply database migrations: npx supabase db reset"
echo "4. Start development server: npm run dev"
echo ""
echo "🔗 For OAuth testing, update redirect URIs to:"
echo "   - Pipedrive: http://localhost:3000/api/oauth/pipedrive/callback"
echo "   - Azure: http://localhost:3000/api/oauth/azure/callback" 