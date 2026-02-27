#!/bin/bash
# Simple: ejecuta la Step Function

# Primero carga variables (asume que estás en raíz)
cd infra
STEP_FUNCTION_ARN=$(terraform output -raw step_function_arn)
cd ..

echo "🚀 Ejecutando: $STEP_FUNCTION_ARN"
aws stepfunctions start-execution --state-machine-arn "$STEP_FUNCTION_ARN"