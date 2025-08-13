#!/bin/bash
# Copyright 2025 Loïc Muhirwa
#
# Script to switch between local and ngrok API configurations
# Usage: ./switch-api-config.sh [local|ngrok]

set -e

ENV_FILE="/home/justloic/companies/from-first-principles/codebase/services/frontend/.env.local"
LOCAL_URL="http://localhost:8081"
NGROK_URL_PLACEHOLDER="NGROK_URL_HERE"

# Get current ngrok URL
get_ngrok_url() {
    curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tunnel in data.get('tunnels', []):
        if 'localhost:8080' in tunnel.get('config', {}).get('addr', ''):
            print(tunnel['public_url'])
            break
except:
    pass
" || echo ""
}

update_env_file() {
    local new_url="$1"
    local comment="$2"

    # Create a temporary file with the updated content
    sed "s|^NEXT_PUBLIC_API_BASE_URL=.*|# $comment\nNEXT_PUBLIC_API_BASE_URL=$new_url|" "$ENV_FILE" > "$ENV_FILE.tmp"
    mv "$ENV_FILE.tmp" "$ENV_FILE"

    echo "✅ Updated API base URL to: $new_url"
}

case "${1:-}" in
    "local")
        update_env_file "$LOCAL_URL" "API Configuration - Using local AI service"
        echo "🏠 Switched to local development mode"
        echo "   Make sure your AI service is running on $LOCAL_URL"
        ;;
    "ngrok")
        CURRENT_NGROK_URL=$(get_ngrok_url)
        if [ -z "$CURRENT_NGROK_URL" ]; then
            echo "❌ No ngrok tunnel found running on port 8080"
            echo "   Start ngrok first: ngrok http 8080"
            exit 1
        fi
        update_env_file "$CURRENT_NGROK_URL" "API Configuration - Using ngrok tunnel"
        echo "🌐 Switched to ngrok mode"
        echo "   Public URL: $CURRENT_NGROK_URL"
        echo "   Monitor at: http://127.0.0.1:4040"
        ;;
    *)
        echo "Usage: $0 [local|ngrok]"
        echo ""
        echo "Commands:"
        echo "  local  - Switch to local development (http://localhost:8081)"
        echo "  ngrok  - Switch to ngrok tunnel (auto-detects current URL)"
        echo ""
        echo "Current configuration:"
        grep "NEXT_PUBLIC_API_BASE_URL=" "$ENV_FILE" | head -1
        exit 1
        ;;
esac

echo ""
echo "💡 Remember to restart your Next.js development server to apply changes!"
echo "   cd /home/justloic/companies/from-first-principles/codebase/services/frontend"
echo "   npm run dev"
