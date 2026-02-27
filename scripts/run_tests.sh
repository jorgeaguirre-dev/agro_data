#!/bin/bash
# Script simple para ejecutar tests

echo "🧪 Ejecutando tests unitarios..."
echo "================================"

# Ir a la raíz del repo
cd "$(dirname "$0")/.."

# Instalar dependencias si es necesario
# pip install -r requirements-dev.txt

# Ejecutar tests
python -m pytest tests/unit -v --cov=src/ingestion/utils

echo "================================"
echo "✅ Tests completados"