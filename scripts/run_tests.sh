#!/bin/bash
# Simple script to run tests

echo "🧪 Running unit tests..."
echo "================================"

# Go to repo root
cd "$(dirname "$0")/.."

# Install dependencies if needed
# pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/unit -v --cov=src/ingestion/utils

echo "================================"
echo "✅ Tests completed"