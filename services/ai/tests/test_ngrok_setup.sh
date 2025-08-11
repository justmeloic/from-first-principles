#!/bin/bash
# Test script for ngrok setup
# This demonstrates that your AI service is now accessible from the internet

set -e

echo "🧪 Testing ngrok setup for AI service..."
echo "================================================"

# Get the current ngrok URL
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tunnel in data.get('tunnels', []):
        if tunnel.get('config', {}).get('addr') == 'http://localhost:8080':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null || echo "https://7201b4690fc5.ngrok-free.app")

echo "🌐 Public URL: $NGROK_URL"
echo "🏠 Local URL: http://localhost:8080"
echo

# Test local service
echo "📍 Testing local service..."
if curl -s http://localhost:8080/docs > /dev/null; then
    echo "✅ Local service is responding"
else
    echo "❌ Local service is not responding"
    exit 1
fi

# Test ngrok tunnel
echo "🌍 Testing public access via ngrok..."
if curl -s "$NGROK_URL/docs" -H "ngrok-skip-browser-warning: true" > /dev/null; then
    echo "✅ Public access via ngrok is working"
else
    echo "❌ Public access via ngrok failed"
    exit 1
fi

echo
echo "🎉 Setup successful! Your AI service is now accessible from:"
echo "   Local:  http://localhost:8080"
echo "   Public: $NGROK_URL"
echo
echo "💡 Next steps:"
echo "   1. Update your frontend to use: $NGROK_URL/agent/"
echo "   2. Test POST requests from https://fromfirstprinciple.com/agent/"
echo "   3. Monitor ngrok connections at: http://127.0.0.1:4040"
