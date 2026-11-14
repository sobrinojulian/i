# DB2 FastAPI — makefile
# Common aliases for running and managing the project.

# Phony targets — these are commands, not file names
.PHONY: help install run stop sync clean env-check odbc-check

# Default target shows help
help:
	@echo "DB2 FastAPI — available commands:"
	@echo ""
	@echo "  make install    Install Python dependencies with uv"
	@echo "  make sync       Sync the uv environment (install + update lockfile)"
	@echo "  make run        Start the FastAPI dev server with hot reload"
	@echo "  make stop       Stop the running FastAPI server"
	@echo "  make run-prod   Start the FastAPI server without reload (production)"
	@echo "  make env-check  Verify that required environment variables are set"
	@echo "  make odbc-check Check if the IBM i Access ODBC driver is registered"
	@echo "  make clean      Remove the uv virtual environment"
	@echo ""

# Install dependencies from pyproject.toml using uv
install:
	uv sync

# Sync the uv environment (install + update lockfile if needed)
sync:
	uv lock
	uv sync

# Start the FastAPI dev server with hot reload (port 8000)
run:
	uv run uvicorn src.fastapi_db2:app --reload --host 0.0.0.0 --port 8000

# Stop the running FastAPI server on port 8000
stop:
	@echo "Stopping server on port 8000..."
	@fuser -k 8000/tcp 2>/dev/null && echo "Server stopped." || echo "No server found on port 8000."

# Start the FastAPI server without reload (for production)
run-prod:
	uv run uvicorn src.fastapi_db2:app --host 0.0.0.0 --port 8000

# Check that required environment variables are set
env-check:
	@echo "Checking environment variables..."
	@echo -n "  DB2_HOSTNAME: " && \
	([ -n "$$DB2_HOSTNAME" ] && echo "$$DB2_HOSTNAME" || echo "NOT SET")
	@echo -n "  DB2_PORT: " && \
	([ -n "$$DB2_PORT" ] && echo "$$DB2_PORT" || echo "NOT SET (default: 446)")
	@echo -n "  DB2_USER: " && \
	([ -n "$$DB2_USER" ] && echo "$$DB2_USER" || echo "NOT SET")
	@echo -n "  DB2_PASSWORD: " && \
	([ -n "$$DB2_PASSWORD" ] && echo "****" || echo "NOT SET")
	@echo ""
	@echo "To set them from .env file, run:"
	@echo "  export $$(cat .env | xargs)"

# Check if the IBM i Access ODBC driver is registered
odbc-check:
	@echo "Checking ODBC drivers..."
	@odbcinst -q -d 2>/dev/null | grep -i "IBM" && \
		echo "IBM i Access ODBC Driver found." || \
		echo "WARNING: IBM i Access ODBC Driver not found. Install it first."

# Remove the uv virtual environment
clean:
	rm -rf .venv
	@echo "Virtual environment removed."
