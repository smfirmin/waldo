#!/bin/bash

# Script to run both backend and frontend tests locally
# This mimics what the CI pipeline does

set -e  # Exit on any error

# Change to script directory
cd "$(dirname "$0")"

echo "🧪 Running Waldo Test Suite"
echo "=========================="

# Backend tests
echo ""
echo "🐍 Running Python backend tests..."
echo "-----------------------------------"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if requirements file exists
if [ -f "requirements-dev.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements-dev.txt > /dev/null
fi

# Run linting
echo "Running Ruff linting..."
ruff check .

# Run Python tests
echo "Running pytest..."
pytest --cov=app --cov-report=term-missing

# Frontend tests
echo ""
echo "🌐 Running JavaScript frontend tests..."
echo "--------------------------------------"

cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm ci > /dev/null

# Run Jest tests
echo "Running Jest tests..."
npm test

# Run with coverage
echo "Running Jest tests with coverage..."
npm run test:coverage

cd ..

echo ""
echo "✅ All tests completed successfully!"
echo "Backend coverage: Check output above"
echo "Frontend coverage: Check frontend/coverage/ directory"