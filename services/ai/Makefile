# Makefile for FastAPI AgentChat Service
# Copyright 2025 Loïc Muhirwa

.PHONY: help install dev prod start stop restart status clean test lint format check logs setup env-check

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
UV := uv
VENV_PATH := .venv
SCRIPTS_DIR := scripts
PID_FILE := uvicorn.pid
LOG_DIR := logs

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)FastAPI AgentChat Service - Available Commands$(NC)"
	@echo "=================================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make setup         # Initial project setup"
	@echo "  make dev           # Start development server"
	@echo "  make prod          # Start production server"
	@echo "  make test          # Run tests"
	@echo "  make logs          # View server logs"
	@echo "  make index-test    # Test indexing pipeline"
	@echo "  make index-all     # Index all content"
	@echo "  make index-search  # Run example search"

# Setup and Installation
setup: ## Complete project setup (environment + dependencies)
	@echo "$(BLUE)🚀 Setting up FastAPI AgentChat project...$(NC)"
	@$(MAKE) install
	@$(MAKE) env-check
	@echo "$(GREEN)✅ Setup complete! Use 'make dev' to start development server$(NC)"

install: ## Install dependencies and setup virtual environment
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "$(YELLOW)Creating virtual environment...$(NC)"; \
		$(UV) venv; \
	fi
	@$(UV) sync
	@$(UV) pip install -e .
	@echo "$(GREEN)✅ Dependencies installed and package installed in editable mode$(NC)"

env-check: ## Check if .env file exists and validate configuration
	@echo "$(BLUE)🔍 Checking environment configuration...$(NC)"
	@if [ ! -f ".env" ]; then \
		echo "$(RED)❌ .env file not found$(NC)"; \
		echo "$(YELLOW)Please copy .env.example to .env and configure it$(NC)"; \
		exit 1; \
	fi
	@. $(VENV_PATH)/bin/activate && $(PYTHON) -c "from src.app.core.config import settings; print('✅ Environment configuration valid')" || (echo "$(RED)❌ Environment configuration invalid$(NC)" && exit 1)

# Development
dev: install env-check ## Start development server with auto-reload
	@echo "$(BLUE)🚀 Starting development server...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/dev-server.sh
	@./$(SCRIPTS_DIR)/dev-server.sh

dev-bg: install env-check ## Start development server in background
	@echo "$(BLUE)🚀 Starting development server in background...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/deploy-server.sh
	@./$(SCRIPTS_DIR)/deploy-server.sh start --dev

# Production
prod: install env-check ## Start production server
	@echo "$(BLUE)🚀 Starting production server...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/deploy-server.sh
	@./$(SCRIPTS_DIR)/deploy-server.sh start

prod-workers: install env-check ## Start production server with custom worker count (usage: make prod-workers WORKERS=8)
	@echo "$(BLUE)🚀 Starting production server with $(or $(WORKERS),4) workers...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/deploy-server.sh
	@./$(SCRIPTS_DIR)/deploy-server.sh start --workers $(or $(WORKERS),4)

# Server Management
start: prod ## Alias for prod - start production server

stop: ## Stop the server
	@echo "$(BLUE)🛑 Stopping server...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/deploy-server.sh
	@./$(SCRIPTS_DIR)/deploy-server.sh stop

restart: ## Restart the server
	@echo "$(BLUE)🔄 Restarting server...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/deploy-server.sh
	@./$(SCRIPTS_DIR)/deploy-server.sh restart --port 8080

status: ## Check server status
	@chmod +x $(SCRIPTS_DIR)/deploy-server.sh
	@./$(SCRIPTS_DIR)/deploy-server.sh status

# Logging
logs: ## View server logs (access logs)
	@if [ -f "$(LOG_DIR)/access.log" ]; then \
		echo "$(BLUE)📋 Viewing access logs (Ctrl+C to exit)...$(NC)"; \
		tail -f $(LOG_DIR)/access.log; \
	else \
		echo "$(YELLOW)⚠️  Access log file not found. Server may not be running.$(NC)"; \
	fi

logs-error: ## View error logs
	@if [ -f "$(LOG_DIR)/error.log" ]; then \
		echo "$(BLUE)📋 Viewing error logs (Ctrl+C to exit)...$(NC)"; \
		tail -f $(LOG_DIR)/error.log; \
	else \
		echo "$(YELLOW)⚠️  Error log file not found. Server may not be running.$(NC)"; \
	fi

logs-all: ## View all logs (both access and error)
	@if [ -f "$(LOG_DIR)/access.log" ] && [ -f "$(LOG_DIR)/error.log" ]; then \
		echo "$(BLUE)📋 Viewing all logs (Ctrl+C to exit)...$(NC)"; \
		tail -f $(LOG_DIR)/access.log $(LOG_DIR)/error.log; \
	else \
		echo "$(YELLOW)⚠️  Log files not found. Server may not be running.$(NC)"; \
	fi

# Testing and Code Quality
test: install ## Run tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@. $(VENV_PATH)/bin/activate && $(PYTHON) -m pytest

test-cov: install ## Run tests with coverage report
	@echo "$(BLUE)🧪 Running tests with coverage...$(NC)"
	@. $(VENV_PATH)/bin/activate && $(PYTHON) -m pytest --cov=src --cov-report=term-missing --cov-report=html

lint: install ## Run linting with ruff
	@echo "$(BLUE)🔍 Running linter...$(NC)"
	@. $(VENV_PATH)/bin/activate && $(PYTHON) -m ruff check src/

format: install ## Format code with ruff
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	@. $(VENV_PATH)/bin/activate && $(PYTHON) -m ruff format src/

check: lint test ## Run all checks (lint + test)
	@echo "$(GREEN)✅ All checks completed$(NC)"

# Content Indexing
index-test: install ## Test the indexing pipeline configuration
	@echo "$(BLUE)🧪 Testing indexing pipeline...$(NC)"
	@index-cli test

index-all: install ## Index all blog content
	@echo "$(BLUE)📚 Indexing all content...$(NC)"
	@index-cli index

index-blog: install ## Index only blog category content
	@echo "$(BLUE)📝 Indexing blog content...$(NC)"
	@index-cli index --category blog

index-engineering: install ## Index only engineering category content
	@echo "$(BLUE)⚙️ Indexing engineering content...$(NC)"
	@index-cli index --category engineering

index-stats: install ## Show indexing statistics
	@echo "$(BLUE)📊 Showing indexing statistics...$(NC)"
	@index-cli stats

index-search: install ## Run example semantic search
	@echo "$(BLUE)🔍 Example semantic search...$(NC)"
	@index-cli search "machine learning" --limit 3

index-search-keyword: install ## Run example keyword search
	@echo "$(BLUE)🔤 Example keyword search...$(NC)"
	@index-cli search "python" --mode keyword --limit 3

index-clear: install ## Clear the search index (with confirmation)
	@echo "$(BLUE)🗑️ Clearing search index...$(NC)"
	@index-cli clear

index-browse: install ## Browse indexed data
	@echo "$(BLUE)👀 Browsing indexed data...$(NC)"
	@index-cli browse --limit 10

index-sample: install ## Show random data samples
	@echo "$(BLUE)🎲 Showing random samples...$(NC)"
	@index-cli sample --count 3

index-inspect: install ## Inspect specific post (usage: make index-inspect POST=my-post-slug)
	@echo "$(BLUE)🔍 Inspecting post: $(POST)...$(NC)"
	@if [ -z "$(POST)" ]; then \
		echo "$(RED)❌ Please specify POST=your-post-slug$(NC)"; \
		echo "$(YELLOW)Example: make index-inspect POST=my-blog-post$(NC)"; \
		exit 1; \
	fi
	@index-cli inspect "$(POST)"

index-help: install ## Show indexing CLI help
	@index-cli --help

# Maintenance
clean: ## Clean up temporary files and caches
	@echo "$(BLUE)🧹 Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache/ 2>/dev/null || true
	@rm -rf htmlcov/ 2>/dev/null || true
	@rm -f .coverage 2>/dev/null || true
	@if [ -f "$(PID_FILE)" ]; then rm -f $(PID_FILE); fi
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

clean-logs: ## Clean log files
	@echo "$(BLUE)🧹 Cleaning log files...$(NC)"
	@if [ -d "$(LOG_DIR)" ]; then \
		rm -f $(LOG_DIR)/*.log; \
		echo "$(GREEN)✅ Log files cleaned$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  No log directory found$(NC)"; \
	fi

reset: clean stop ## Reset project (stop server, clean files)
	@echo "$(GREEN)✅ Project reset completed$(NC)"

# Docker support (optional - for future use)
docker-build: ## Build Docker image (if Dockerfile exists)
	@if [ -f "Dockerfile" ]; then \
		echo "$(BLUE)🐳 Building Docker image...$(NC)"; \
		docker build -t agentchat-api .; \
	else \
		echo "$(YELLOW)⚠️  Dockerfile not found$(NC)"; \
	fi

# Development utilities
shell: install ## Start interactive Python shell with project context
	@echo "$(BLUE)🐚 Starting Python shell...$(NC)"
	@. $(VENV_PATH)/bin/activate && $(PYTHON) -c "from src.app.core.config import settings; print(f'AgentChat API Shell - Environment: {settings.ENVIRONMENT}')" && $(PYTHON)

docs: ## Generate and serve documentation (if available)
	@echo "$(BLUE)📚 Opening API documentation...$(NC)"
	@echo "$(GREEN)API Docs available at: http://localhost:8081/docs$(NC)"
	@echo "$(GREEN)ReDoc available at: http://localhost:8081/redoc$(NC)"

# Quick commands
quick-start: setup dev ## Complete setup and start development server
	@echo "$(GREEN)🎉 Quick start completed!$(NC)"

# Health check
health: ## Check if server is responding
	@echo "$(BLUE)🏥 Checking server health...$(NC)"
	@curl -s -o /dev/null -w "HTTP Status: %{http_code}\nResponse Time: %{time_total}s\n" http://localhost:8081/docs || echo "$(RED)❌ Server not responding$(NC)"
