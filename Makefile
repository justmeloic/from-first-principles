# Makefile for deploying services

.PHONY: deploy deploy-ai deploy-frontend add-license help clean

# Default target
help:
	@echo "Available targets:"
	@echo "  deploy          - Merge dev→main, deploy AI + Frontend, recreate dev"
	@echo "  deploy-ai       - Deploy AI service on Pi with ngrok (no git ops)"
	@echo "  deploy-frontend - Deploy frontend to Netlify (no git ops)"
	@echo "  add-license     - Add license headers to source files"
	@echo "  clean           - Clean build artifacts and logs"
	@echo "  help            - Show this help message"

# Full release: merge dev→main, deploy everything, recreate dev
deploy:
	@echo "🚀 Starting full deployment (merge + AI + Frontend)..."
	@chmod +x scripts/deploy-all.sh
	@cd scripts && ./deploy-all.sh

# Deploy AI service only (Pi + ngrok)
deploy-ai:
	@echo "🚀 Starting AI service deployment..."
	@cd services/ai && make prod

# Deploy frontend only (Netlify)
deploy-frontend:
	@echo "🚀 Starting frontend deployment..."
	@chmod +x scripts/deploy-frontend-service.sh
	@cd scripts && ./deploy-frontend-service.sh

# Add license headers to source files
add-license:
	@echo "📄 Adding license headers to source files..."
	@chmod +x scripts/add-license.sh
	@cd scripts && ./add-license.sh

# Clean build artifacts and logs
clean:
	@echo "🧹 Cleaning build artifacts and logs..."
	@rm -rf services/frontend/.next
	@rm -rf services/frontend/out
	@rm -rf services/frontend/node_modules/.cache
	@rm -f scripts/logs/*.log
	@echo "✨ Clean completed!"
