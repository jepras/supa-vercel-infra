#!/bin/bash

# Build script for Railway deployment optimization

echo "🚀 Building optimized Docker image..."

# Build with cache optimization
docker build \
  --cache-from python:3.11-slim \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  -t supa-vercel-infra-backend:latest \
  .

echo "✅ Build complete!"
echo "📦 Image size:"
docker images supa-vercel-infra-backend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo "🧪 Testing container..."
docker run --rm -p 8000:8000 supa-vercel-infra-backend:latest &
CONTAINER_PID=$!

# Wait for container to start
sleep 5

# Test health endpoint
curl -f http://localhost:8000/health || echo "❌ Health check failed"

# Stop container
kill $CONTAINER_PID

echo "✅ Local testing complete!" 