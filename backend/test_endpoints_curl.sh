#!/bin/bash

# Test Production Backend Endpoints with curl
# Usage: ./test_endpoints_curl.sh [PRODUCTION_URL]
# Example: ./test_endpoints_curl.sh https://your-backend.railway.app

set -e

# Default to localhost if no URL provided
PRODUCTION_URL=${1:-"http://localhost:8000"}

echo "🚀 Testing Production Backend Endpoints"
echo "🎯 URL: $PRODUCTION_URL"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    
    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$PRODUCTION_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" \
            -d "$data" "$PRODUCTION_URL$endpoint")
    fi
    
    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Extract response body (all but last line)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" = "200" ]; then
        echo -e "${GREEN}✓ SUCCESS (200)${NC}"
        echo "Response: $body" | head -c 200
        [ ${#body} -gt 200 ] && echo "..."
    else
        echo -e "${RED}✗ FAILED ($status_code)${NC}"
        echo "Response: $body"
    fi
}

# Test health endpoints
echo -e "\n${YELLOW}🏥 Testing Health Endpoints${NC}"
test_endpoint "GET" "/" "Root endpoint"
test_endpoint "GET" "/api/health" "Main health check"
test_endpoint "GET" "/api/ai/health" "AI service health check"
test_endpoint "GET" "/api/monitoring/test" "Monitoring test endpoint"

# Test OAuth infrastructure
echo -e "\n${YELLOW}🔐 Testing OAuth Infrastructure${NC}"
test_endpoint "GET" "/api/oauth/test" "OAuth infrastructure test"

# Test AI endpoints
echo -e "\n${YELLOW}🤖 Testing AI Endpoints${NC}"
test_message='{"message": "Hello, this is a test message from production testing.", "model": "openai/gpt-3.5-turbo"}'
test_endpoint "POST" "/api/ai/test" "OpenRouter connectivity test" "$test_message"

echo -e "\n${YELLOW}📧 Testing Production AI Agents (this may take a while)${NC}"
test_endpoint "POST" "/api/ai/test-production-agents" "Production AI agents test with sample emails"

# Test ngrok endpoint
echo -e "\n${YELLOW}🌐 Testing Ngrok Endpoint${NC}"
test_endpoint "GET" "/api/ngrok/url" "Get ngrok URL for webhook testing"

echo -e "\n${GREEN}✨ Testing complete!${NC}"
echo "==================================================" 