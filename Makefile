# Makefile for deploying services

.PHONY: deploy-react help clean

# Default target
help:
	@echo "Available targets:"
	@echo "  deploy-react    - Deploy the React web UI service"
	@echo "  clean          - Clean build artifacts and logs"
	@echo "  help           - Show this help message"

# Deploy the React web UI service
deploy-react:
	@echo "🚀 Starting React service deployment..."
	@chmod +x scripts/deploy-webui_react-service.sh
	@cd scripts && ./deploy-webui_react-service.sh

# Clean build artifacts and logs
clean:
	@echo "🧹 Cleaning build artifacts and logs..."
	@rm -rf services/webui_react/.next
	@rm -rf services/webui_react/out
	@rm -rf services/webui_react/node_modules/.cache
	@rm -f scripts/logs/*.log
	@echo "✨ Clean completed!"
