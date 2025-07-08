#!/bin/bash

# Test Token Refresh Functionality with curl
# This script tests the token refresh mechanisms for both Pipedrive and Microsoft.

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
USER_ID="${TEST_USER_ID:-your-user-id-here}"

echo "🔄 Testing Token Refresh Functionality"
echo "=================================================="

if [ "$USER_ID" = "your-user-id-here" ]; then
    echo "❌ Please set TEST_USER_ID environment variable with a valid user ID"
    echo "   Example: export TEST_USER_ID='your-actual-user-id'"
    exit 1
fi

echo "👤 Testing with user ID: $USER_ID"
echo "🌐 Backend URL: $BACKEND_URL"
echo ""

# Test token refresh endpoint
echo "🔍 Testing token refresh endpoint..."
response=$(curl -s -w "\n%{http_code}" -X POST \
    "$BACKEND_URL/api/ai/test-token-refresh/$USER_ID" \
    -H "Content-Type: application/json" \
    --max-time 30)

# Extract status code and body
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

echo "📊 Response Status: $http_code"
echo ""

if [ "$http_code" -eq 200 ]; then
    echo "✅ Token refresh test completed successfully!"
    echo ""
    
    # Parse and display results using jq if available
    if command -v jq &> /dev/null; then
        echo "📋 Summary:"
        echo "$body" | jq -r '.summary | "   Pipedrive Status: \(.pipedrive_status)"'
        echo "$body" | jq -r '.summary | "   Microsoft Status: \(.microsoft_status)"'
        echo "$body" | jq -r '.summary | "   Pipedrive Token Valid: \(.pipedrive_token_valid)"'
        echo "$body" | jq -r '.summary | "   Microsoft Token Valid: \(.microsoft_token_valid)"'
        echo ""
        
        echo "📊 Detailed Results:"
        echo "$body" | jq -r '.results[]? | "   \(.provider | ascii_upcase): \(if .success then "✅ \(.message // "Success")" else "❌ \(.error // "Failed")" end)"'
        
        # Show user info for successful results
        echo ""
        echo "👤 User Information:"
        echo "$body" | jq -r '.results[]? | select(.success) | "   \(.provider | ascii_upcase): \(.user_info | to_entries | map("\(.key)=\(.value)") | join(", "))"'
        
    else
        echo "📋 Raw Response:"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    fi
    
else
    echo "❌ Token refresh test failed!"
    echo "   HTTP Status: $http_code"
    echo "   Response: $body"
fi

echo ""
echo "🔍 Testing Individual Provider Endpoints"
echo "=================================================="

# Test Pipedrive connection endpoint
echo "📊 Testing Pipedrive connection endpoint..."
pipedrive_response=$(curl -s -w "\n%{http_code}" -X POST \
    "$BACKEND_URL/api/oauth/pipedrive/test" \
    -H "Content-Type: application/json" \
    --max-time 10)

pipedrive_code=$(echo "$pipedrive_response" | tail -n1)
echo "   Status: $pipedrive_code"
if [ "$pipedrive_code" -eq 200 ]; then
    echo "   ✅ Pipedrive connection test endpoint available"
elif [ "$pipedrive_code" -eq 401 ]; then
    echo "   ⚠️  Pipedrive test requires authentication (expected)"
else
    echo "   ⚠️  Pipedrive test returned: $pipedrive_code"
fi

# Test Microsoft connection endpoint
echo "📧 Testing Microsoft connection endpoint..."
microsoft_response=$(curl -s -w "\n%{http_code}" -X POST \
    "$BACKEND_URL/api/oauth/microsoft/test" \
    -H "Content-Type: application/json" \
    --max-time 10)

microsoft_code=$(echo "$microsoft_response" | tail -n1)
echo "   Status: $microsoft_code"
if [ "$microsoft_code" -eq 200 ]; then
    echo "   ✅ Microsoft connection test endpoint available"
elif [ "$microsoft_code" -eq 401 ]; then
    echo "   ⚠️  Microsoft test requires authentication (expected)"
else
    echo "   ⚠️  Microsoft test returned: $microsoft_code"
fi

echo ""
echo "=================================================="
echo "🏁 Token refresh tests completed!"

# Usage instructions
echo ""
echo "📖 Usage Instructions:"
echo "   1. Set your user ID: export TEST_USER_ID='your-actual-user-id'"
echo "   2. Set backend URL: export BACKEND_URL='https://your-backend.railway.app'"
echo "   3. Run this script: ./test_token_refresh_curl.sh"
echo ""
echo "🔧 For production testing:"
echo "   BACKEND_URL=https://your-backend.railway.app TEST_USER_ID=your-user-id ./test_token_refresh_curl.sh" 