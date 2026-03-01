#!/bin/bash
# Copyright 2025 Loïc Muhirwa
#
# Script to switch between local and ngrok API configurations
# Usage: ./switch-api-config.sh [local|ngrok]

set -e

ENV_FILE="/home/justloic/companies/from-first-principles/codebase/services/frontend/.env.local"
LOCAL_URL="http://localhost:8081"
NGROK_URL="https://elenor-sleekiest-funereally.ngrok-free.dev"

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
        update_env_file "$NGROK_URL" "API Configuration - Using ngrok tunnel (static domain)"
        echo "🌐 Switched to ngrok mode"
        echo "   Public URL: $NGROK_URL"
        ;;
    *)
        echo "Usage: $0 [local|ngrok]"
        echo ""
        echo "Commands:"
        echo "  local  - Switch to local development (http://localhost:8081)"
        echo "  ngrok  - Switch to ngrok static domain ($NGROK_URL)"
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
