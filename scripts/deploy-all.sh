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

# Step 1: Start AI service with ngrok (static domain)
log_info "Step 1: Starting AI service with ngrok..."
cd "$PROJECT_ROOT/services/ai"
make prod

# Step 2: Wait for server + ngrok to initialize
log_info "Step 2: Waiting for services to initialize..."
sleep 8

NGROK_DOMAIN="elenor-sleekiest-funereally.ngrok-free.dev"
NGROK_URL="https://$NGROK_DOMAIN"
log_info "Using static ngrok domain: $NGROK_URL"

# Step 3: Deploy frontend (netlify.toml already has the static domain)
log_info "Step 3: Deploying frontend to Netlify..."
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
