#!/bin/bash
# Copyright 2025 Loïc Muhirwa
#
# Full deployment script: merge dev→main, deploy AI + Frontend, recreate dev
# Usage: ./deploy-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/deploy-all.log"

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
echo "  Full Deploy: merge dev→main · AI · Frontend"
echo "=================================================="
echo -e "${NC}"

log_info "Log file: $LOG_FILE"

# ------------------------------------------------------------------
# Step 1: Merge dev → main
# ------------------------------------------------------------------
log_info "Step 1: Merging dev → main..."
cd "$PROJECT_ROOT"

current_branch=$(git branch --show-current)
if [[ "$current_branch" != "dev" ]]; then
  log_error "You must be on the dev branch to deploy. Current branch: $current_branch"
  exit 1
fi

# Ensure working tree is clean
if ! git diff --quiet || ! git diff --cached --quiet; then
  log_error "Working tree is dirty. Commit or stash changes before deploying."
  exit 1
fi

git checkout main
git pull origin main
git merge --no-ff dev -m "Merge dev into main for deployment"
git push origin main
log_info "main updated and pushed."

# ------------------------------------------------------------------
# Step 2: Start AI service with ngrok (static domain)
# ------------------------------------------------------------------
log_info "Step 2: Starting AI service with ngrok..."
cd "$PROJECT_ROOT/services/ai"
make prod

# Step 3: Wait for server + ngrok to initialize
log_info "Step 3: Waiting for services to initialize..."
sleep 8

NGROK_DOMAIN="elenor-sleekiest-funereally.ngrok-free.dev"
NGROK_URL="https://$NGROK_DOMAIN"
log_info "Using static ngrok domain: $NGROK_URL"

# ------------------------------------------------------------------
# Step 4: Deploy frontend (netlify.toml already has the static URL)
# ------------------------------------------------------------------
log_info "Step 4: Deploying frontend to Netlify..."
cd "$SCRIPT_DIR"
chmod +x deploy-frontend-service.sh
./deploy-frontend-service.sh

# ------------------------------------------------------------------
# Step 5: Recreate dev from main
# ------------------------------------------------------------------
log_info "Step 5: Recreating dev branch from main..."
cd "$PROJECT_ROOT"
git checkout main
git branch -D dev 2>/dev/null || true
git push origin --delete dev 2>/dev/null || true
git checkout -b dev
git push --set-upstream origin dev
log_info "dev branch recreated from main."

echo ""
log_info "🎉 Full deployment complete!"
echo -e "  • AI Service: ${GREEN}$NGROK_URL${NC}"
echo -e "  • Frontend:   ${GREEN}Deployed to Netlify${NC}"
echo -e "  • Branch:     ${GREEN}dev (fresh from main)${NC}"

echo ""
echo "========================================"
echo "Deployment finished at: $(date)"
echo "========================================"
