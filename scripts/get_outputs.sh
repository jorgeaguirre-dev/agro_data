#!/bin/bash

# Script para obtener outputs de Terraform de forma segura
cd "$(dirname "$0")/../infra" || exit 1

# Verificar que terraform output funciona
if ! terraform output > /dev/null 2>&1; then
    echo "❌ Error: No se pueden obtener outputs. Ejecuta 'terraform apply' primero."
    exit 1
fi

# Obtener valores
export RINDE_JOB=$(terraform output -json glue_jobs | jq -r '.rinde_lotes')
export CLIMA_JOB=$(terraform output -json glue_jobs | jq -r '.clima_diario')
export LANDING_BUCKET=$(terraform output -raw landing_bucket)
export CURATED_BUCKET=$(terraform output -raw curated_bucket)
export DATABASE_NAME=$(terraform output -raw glue_database 2>/dev/null || echo "agro_data_pipeline_dev_db")

cd - > /dev/null

echo "✅ Outputs cargados:"
echo "  RINDE_JOB: $RINDE_JOB"
echo "  CLIMA_JOB: $CLIMA_JOB"
echo "  LANDING_BUCKET: $LANDING_BUCKET"
echo "  CURATED_BUCKET: $CURATED_BUCKET"
echo "  DATABASE_NAME: $DATABASE_NAME"
