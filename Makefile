# Makefile for deploying services

.PHONY: deploy-react reset-dev add-license help clean

# Default target
help:
	@echo "Available targets:"
	@echo "  deploy-react    - Deploy the React web UI service"
	@echo "  reset-dev       - Reset dev branch from main"
	@echo "  add-license     - Add license headers to source files"
	@echo "  clean          - Clean build artifacts and logs"
	@echo "  help           - Show this help message"

# Deploy the React web UI service
deploy-react:
	@echo "🚀 Starting React service deployment..."
	@chmod +x scripts/deploy-webui_react-service.sh
	@cd scripts && ./deploy-webui_react-service.sh

# Reset dev branch from main
reset-dev:
	@echo "🔄 Resetting dev branch from main..."
	@chmod +x scripts/reset-dev-branch.sh
	@cd scripts && ./reset-dev-branch.sh

# Add license headers to source files
add-license:
	@echo "📄 Adding license headers to source files..."
	@chmod +x scripts/add-license.sh
	@cd scripts && ./add-license.sh

# Clean build artifacts and logs
clean:
	@echo "🧹 Cleaning build artifacts and logs..."
	@rm -rf services/webui_react/.next
	@rm -rf services/webui_react/out
	@rm -rf services/webui_react/node_modules/.cache
	@rm -f scripts/logs/*.log
	@echo "✨ Clean completed!"
