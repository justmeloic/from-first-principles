#!/bin/bash
# Copyright 2025 Loïc Muhirwa
#
# Full deployment script: AI service + Frontend
# Usage: ./deploy-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/deploy-all.log"
NETLIFY_TOML="$PROJECT_ROOT/services/frontend/netlify.toml"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Redirect all output to log file AND console
exec > >(tee -a "$LOG_FILE") 2>&1

# Log timestamp
echo ""
echo "========================================"
echo "Deployment started at: $(date)"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${BLUE}"
echo "=================================================="
echo "    Full Deployment: AI Service + Frontend"
echo "=================================================="
echo -e "${NC}"

log_info "Log file: $LOG_FILE"

# Step 1: Start AI service with ngrok
log_info "Step 1: Starting AI service with ngrok..."
cd "$PROJECT_ROOT/services/ai"
make prod

# Step 2: Wait for ngrok to initialize
log_info "Step 2: Waiting for ngrok to initialize..."
sleep 5

# Step 3: Get ngrok URL
log_info "Step 3: Fetching ngrok URL..."
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tunnel in data.get('tunnels', []):
        url = tunnel.get('public_url', '')
        if 'https' in url:
            print(url)
            break
except:
    pass
" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    log_error "Failed to get ngrok URL. Check if ngrok is running."
    log_warn "You can check ngrok dashboard at: http://localhost:4040"
    exit 1
fi

log_info "Got ngrok URL: $NGROK_URL"

# Step 4: Update netlify.toml
log_info "Step 4: Updating netlify.toml with new API URL..."
sed -i '' "s|NEXT_PUBLIC_API_BASE_URL = \".*\"|NEXT_PUBLIC_API_BASE_URL = \"$NGROK_URL\"|" "$NETLIFY_TOML"
log_info "Updated $NETLIFY_TOML"

# Step 5: Deploy frontend
log_info "Step 5: Deploying frontend to Netlify..."
cd "$SCRIPT_DIR"
chmod +x deploy-frontend-service.sh
./deploy-frontend-service.sh

echo ""
log_info "🎉 Full deployment complete!"
echo -e "  • AI Service: ${GREEN}$NGROK_URL${NC}"
echo -e "  • Frontend: ${GREEN}Deployed to Netlify${NC}"

echo ""
echo "========================================"
echo "Deployment finished at: $(date)"
echo "========================================"
