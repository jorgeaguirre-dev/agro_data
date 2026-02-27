#!/bin/bash

# Cargar outputs
source "$(dirname "$0")/get_outputs.sh"

# Validar que tenemos el ARN
if [ -z "$STEP_FUNCTION_ARN" ]; then
    echo "❌ Error: STEP_FUNCTION_ARN no está definido"
    echo "   Ejecuta 'terraform apply' primero y verifica el output"
    exit 1
fi

# Ejecutar Step Function
EXECUTION_ARN=$(aws stepfunctions start-execution \
  --state-machine-arn $STEP_FUNCTION_ARN \
  --input '{"timestamp":"'$(date -Iseconds)'"}' \
  --query 'executionArn' \
  --output text)

if [ $? -ne 0 ]; then
    echo "❌ Error al ejecutar Step Function"
    exit 1
fi

echo "🚀 Step Function ejecutada: $EXECUTION_ARN"
echo "Ver progreso en: https://console.aws.amazon.com/states/home?region=us-east-1#/executions/details/$EXECUTION_ARN"

# Esperar a que termine
echo "⏳ Esperando ejecución..."
while true; do
    STATUS=$(aws stepfunctions describe-execution \
      --execution-arn $EXECUTION_ARN \
      --query 'status' \
      --output text)
    
    echo "   Estado: $STATUS"
    
    if [[ "$STATUS" == "SUCCEEDED" ]]; then
        break
    elif [[ "$STATUS" == "FAILED" ]] || [[ "$STATUS" == "TIMED_OUT" ]] || [[ "$STATUS" == "ABORTED" ]]; then
        echo "❌ Falló la ejecución (estado: $STATUS)"
        
        # Obtener causa del error
        CAUSE=$(aws stepfunctions describe-execution \
          --execution-arn $EXECUTION_ARN \
          --query 'cause' \
          --output text)
        
        if [ "$CAUSE" != "None" ]; then
            echo "   Causa: $CAUSE"
        fi
        exit 1
    fi
    sleep 5
done

echo "✅ Pipeline completado!"