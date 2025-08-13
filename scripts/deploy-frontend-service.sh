#!/bin/bash

# Redirect all output to a log file and also to the console
exec > >(tee -a logs/deploy-frontend-service.log) 2>&1
# Script to checkout main, update it, and deploy the frontend service

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


# Deploy the frontend service
cd ../services/frontend || exit 1


echo "🚀 Starting deployment process..."

# Check if netlify-cli is installed
if ! command -v netlify &> /dev/null; then
    echo "❌ netlify-cli is not installed. Installing globally..."
    npm install -g netlify-cli
fi

# Check if user is logged into Netlify
if ! netlify status &> /dev/null; then
    echo "❌ Not logged into Netlify. Please log in..."
    netlify login
fi

# Clean up build directories
echo "🧹 Cleaning up build directories..."
if [ -d ".next" ]; then
    echo "Removing .next directory..."
    rm -rf .next
fi

if [ -d "out" ]; then
    echo "Removing out directory..."
    rm -rf out
fi

# Clear npm cache if it exists
echo "🧹 Cleaning npm cache..."
npm cache clean --force

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Run type checking
echo "✅ Running type check..."
npx tsc --noEmit

# Run linting
echo "🔍 Running linter..."
npm run lint

# Build the application
echo "🏗️  Building the application..."
npm run build

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please fix the errors and try again."
    exit 1
fi

# Deploy to Netlify
echo "🚀 Deploying to Netlify..."
netlify deploy --prod

echo "✨ Deployment process completed!"


# Recreate dev branch from main
echo "🏃🏽‍♂️💨 Getting off the main branch"
git checkout dev || exit 1
