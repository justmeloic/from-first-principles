#!/bin/bash

# Redirect all output to a log file and also to the console
exec > >(tee -a logs/reset-dev-branch.log) 2>&1

# Script to merge dev into main, then delete and recreate dev

#set -euo pipefail # Exit on any error

# Suppress _omz_async_functions error
export ZSH_DISABLE_COMPFIX=true

# Check if git is installed
if ! command -v git &> /dev/null; then
  echo "Error: git is not installed. Please install git and try again."
  exit 1
fi

# Check if the current directory is a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
  echo "❌ Error: Not a git repository. Please run this script from the root of your git repository."
  exit 1
fi

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

# Check if dev branch exists locally
if branch_exists heads dev; then
    echo "Checking out dev branch"
    git checkout dev || exit 1
    echo "Pulling latest changes from origin dev..."
    git pull origin dev || exit 1
    echo "Checking out main branch"
    git checkout main || exit 1
    echo "Merging dev into main..."
    git merge --no-ff dev -m "Merge dev into main" || exit 1 # --no-ff creates a merge commit
    echo "Pushing main to origin..."
    git push origin main || exit 1
fi

# Delete local dev branch (if it exists)
if branch_exists heads dev; then
  echo "Deleting local dev branch..."
  git branch -D dev || exit 1
fi

# Delete remote dev branch (if it exists)
if branch_exists remotes origin/dev; then
  echo "Deleting remote dev branch..."
  git push origin --delete dev || exit 1
fi

# Recreate dev branch from main
echo "Creating new dev branch from main..."
echo "🏃🏽‍♂️💨 Getting off the main branch"

git checkout -b dev || exit 1
git push --set-upstream origin dev || exit 1

echo "✅ Dev branch successfully reset and pushed."
