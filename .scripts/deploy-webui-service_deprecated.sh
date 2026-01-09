#!/bin/bash

# Redirect all output to a log file and also to the console
exec > >(tee -a logs/deploy-webui-service.log) 2>&1
# Script to checkout main, update it, and deploy the webui service

#set -euo pipefail # Exit on any error

# Suppress _omz_async_functions error
export ZSH_DISABLE_COMPFIX=true

# Function to check if a branch exists (local or remote)
branch_exists() {
  git show-ref --verify --quiet "refs/$1/$2"
}

# Get current branch
current_branch=$(git branch --show-current)

# Check if on main branch
if [[ "$current_branch" != "main" ]]; then
  echo "Not on the main branch. Switching to main..."
  git checkout main || exit 1
fi

echo "Pulling latest changes from origin main..."
git pull origin main || exit 1


# Deploy the webui service
cd ../services/webui_legacy || exit 1
ntl deploy --prod --dir src || exit 1

# Recreate dev branch from main
echo "Getting off the main branch"
git checkout dev || exit 1
