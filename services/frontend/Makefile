# Wealthsimple CX Analytics Frontend Makefile

.PHONY: dev build install clean help

# Default target
dev:
	@echo "Starting development server..."
	npm run dev

build:
	@echo "Building static frontend..."
	npm run build

install:
	@echo "Installing dependencies..."
	npm install

clean:
	@echo "Cleaning build artifacts..."
	rm -rf .next out node_modules/.cache

help:
	@echo "Available commands:"
	@echo "  make dev     - Start development server"
	@echo "  make build   - Build static frontend and copy to backend"
	@echo "  make install - Install npm dependencies"
	@echo "  make clean   - Clean build artifacts and cache"
	@echo "  make help    - Show this help message"
