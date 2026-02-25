#!/bin/bash

# Obtener nombre del bucket desde Terraform
cd infra
SCRIPTS_BUCKET=$(terraform output -raw scripts_bucket)
cd ..

echo "📤 Subiendo scripts a s3://${SCRIPTS_BUCKET}/"

# Crear estructura en S3 y subir archivos
aws s3 cp src/ingestion/jobs/ s3://${SCRIPTS_BUCKET}/jobs/ --recursive

echo "✅ Scripts subidos correctamente"
