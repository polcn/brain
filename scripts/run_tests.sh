#!/bin/bash
# Script to run Brain tests

set -e

echo "Setting up test environment..."

# Export test environment variables
export TESTING=true
export LOG_LEVEL=DEBUG
export DATABASE_URL="postgresql://brain_user:brain_password@localhost:5433/brain_test"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Brain Test Suite${NC}"
echo "================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${RED}Error: Virtual environment not activated${NC}"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

# Install test dependencies if needed
echo "Installing test dependencies..."
pip install -q -r requirements-dev.txt

# Create test database if it doesn't exist
echo "Setting up test database..."
psql -U postgres -h localhost -p 5433 -c "CREATE DATABASE brain_test;" 2>/dev/null || true

# Run database migrations on test database
echo "Running migrations on test database..."
DATABASE_URL=$DATABASE_URL alembic upgrade head

# Run different test suites based on argument
case "$1" in
    "unit")
        echo -e "${GREEN}Running unit tests only...${NC}"
        pytest -m "not integration" --cov-report=term-missing
        ;;
    "integration")
        echo -e "${GREEN}Running integration tests only...${NC}"
        pytest -m integration --cov-report=term-missing
        ;;
    "coverage")
        echo -e "${GREEN}Running all tests with coverage report...${NC}"
        pytest --cov-report=html --cov-report=term-missing
        echo "Coverage report generated in htmlcov/index.html"
        ;;
    "watch")
        echo -e "${GREEN}Running tests in watch mode...${NC}"
        pytest-watch -- -x --ff
        ;;
    "verbose")
        echo -e "${GREEN}Running all tests with verbose output...${NC}"
        pytest -vv --tb=long
        ;;
    "fast")
        echo -e "${GREEN}Running fast tests only (no integration)...${NC}"
        pytest -m "not integration and not slow" -x --ff
        ;;
    *)
        echo -e "${GREEN}Running all tests...${NC}"
        pytest
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi