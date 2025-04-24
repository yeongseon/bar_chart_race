.PHONY: setup install run clean build test

UV_BIN := $(shell command -v uv 2>/dev/null)

# Install uv if not already installed
install-uv:
ifndef UV_BIN
	@echo "🔧 Installing uv..."
	@curl -Ls https://astral.sh/uv/install.sh | sh
else
	@echo "✅ uv is already installed at $(UV_BIN)"
endif

# Set up the project environment and install dependencies
setup: install-uv
	@echo "📦 Setting up the project with uv..."
	uv venv
	uv pip install -e .[dev]
	uv pip install build

# Run the demo script
run:
	@echo "🚀 Running bar_chart_race example..."
	PYTHONPATH=src .venv/bin/python examples/run_demo.py

# Clean up the virtual environment and dist
clean:
	@echo "🧹 Cleaning virtual environment and build artifacts..."
	rm -rf .venv dist build *.egg-info

# Build the package using uv-installed build module
build:
	@echo "📦 Building distribution files..."
	test -d .venv || make setup
	uv run python -m build

test:
	@echo "✅ Running tests..."
	PYTHONPATH=src pytest tests
