# Makefile for deploying services

.PHONY: deploy deploy-ai deploy-frontend reset-dev add-license help clean

# Default target
help:
	@echo "Available targets:"
	@echo "  deploy          - Deploy AI service + Frontend together"
	@echo "  deploy-ai       - Deploy AI service on Pi with ngrok"
	@echo "  deploy-frontend - Deploy frontend to Netlify"
	@echo "  reset-dev       - Merge dev→main, recreate dev, deploy frontend"
	@echo "  add-license     - Add license headers to source files"
	@echo "  clean           - Clean build artifacts and logs"
	@echo "  help            - Show this help message"

# Deploy both AI service + Frontend
deploy:
	@echo "🚀 Starting full deployment (AI + Frontend)..."
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

# Merge dev→main, recreate dev branch, deploy frontend
reset-dev:
	@echo "🔄 Resetting dev branch and deploying..."
	@original_dir="$$PWD"; \
	trap 'cd "$$original_dir" 2>/dev/null || exit; printf "\nReturned to original directory: %s\n" "$$original_dir"' EXIT; \
	cd scripts && \
	chmod +x reset-dev-branch.sh deploy-frontend-service.sh && \
	echo "🔄 Running reset-dev-branch.sh..." && \
	./reset-dev-branch.sh && \
	echo "🌐 Running deploy-frontend-service.sh..." && \
	./deploy-frontend-service.sh

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
