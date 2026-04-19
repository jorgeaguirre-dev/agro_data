#!/bin/bash
# Simple: runs the Step Function

# Load variables first (assumes you are at root)
cd infra
STEP_FUNCTION_ARN=$(terraform output -raw step_function_arn)
cd ..

echo "🚀 Running: $STEP_FUNCTION_ARN"
aws stepfunctions start-execution --state-machine-arn "$STEP_FUNCTION_ARN"