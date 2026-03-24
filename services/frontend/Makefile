# Wealthsimple CX Analytics Frontend Makefile

.PHONY: dev build install clean test test-e2e release release-major release-minor release-patch help

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

test:
	@echo "Running tests with coverage..."
	npm run test:coverage

test-e2e:
	@echo "Running E2E tests (Chromium)..."
	npm run test:e2e -- --project=chromium
	@echo "Opening test report..."
	npx playwright show-report

release:
	@echo "Creating release (automatic version bump)..."
	npm run release

release-major:
	@echo "Creating major release..."
	npm run release:major

release-minor:
	@echo "Creating minor release..."
	npm run release:minor

release-patch:
	@echo "Creating patch release..."
	npm run release:patch

help:
	@echo "Available commands:"
	@echo "  make dev           - Start development server"
	@echo "  make build         - Build static frontend and copy to backend"
	@echo "  make install       - Install npm dependencies"
	@echo "  make clean         - Clean build artifacts and cache"
	@echo "  make test          - Run unit/component tests with coverage"
	@echo "  make test-e2e      - Run E2E tests with Playwright"
	@echo "  make release       - Create release with automatic version bump"
	@echo "  make release-major - Create major version release (x.0.0)"
	@echo "  make release-minor - Create minor version release (0.x.0)"
	@echo "  make release-patch - Create patch version release (0.0.x)"
	@echo "  make help          - Show this help message"
