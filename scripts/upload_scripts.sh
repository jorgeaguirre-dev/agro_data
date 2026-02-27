#!/bin/bash

# Cargar outputs
cd infra
export SCRIPTS_BUCKET=$(terraform output -raw scripts_bucket)
cd ..

echo "📤 Subiendo scripts a s3://${SCRIPTS_BUCKET}/"

# Subir jobs principales
echo "  - Jobs principales..."
aws s3 cp src/ingestion/jobs/ s3://${SCRIPTS_BUCKET}/jobs/ --recursive --exclude "*" --include "*.py"

# Subir jobs de Data Quality
echo "  - Jobs de Data Quality..."
aws s3 cp src/dq/ s3://${SCRIPTS_BUCKET}/jobs/ --recursive --exclude "*" --include "*.py"

# Verificar
echo "✅ Scripts en S3:"
aws s3 ls s3://${SCRIPTS_BUCKET}/jobs/ --recursive | grep "\.py" | tail -5