#!/bin/bash

# Script para obtener outputs de Terraform de forma segura
cd infra

# Obtener valores
export RINDE_JOB=$(terraform output -json glue_jobs | jq -r '.rinde_lotes')
export CLIMA_JOB=$(terraform output -json glue_jobs | jq -r '.clima_diario')
export DQ_JOB=$(terraform output -json glue_jobs | jq -r '.dq')
export LANDING_BUCKET=$(terraform output -raw landing_bucket)
export CURATED_BUCKET=$(terraform output -raw curated_bucket)
export SCRIPTS_BUCKET=$(terraform output -raw scripts_bucket)
export DATABASE_NAME=$(terraform output -raw glue_database 2>/dev/null || echo "agro-data-pipeline_dev_db")
export STEP_FUNCTION_ARN=$(terraform output -raw step_function_arn 2>/dev/null || echo "")

cd ..

echo "✅ Outputs cargados:"
echo "  RINDE_JOB: $RINDE_JOB"
echo "  CLIMA_JOB: $CLIMA_JOB"
echo "  DQ_JOB: $DQ_JOB"
echo "  LANDING_BUCKET: $LANDING_BUCKET"
echo "  CURATED_BUCKET: $CURATED_BUCKET"
echo "  SCRIPTS_BUCKET: $SCRIPTS_BUCKET"
echo "  DATABASE_NAME: $DATABASE_NAME"
echo "  STEP_FUNCTION_ARN: $STEP_FUNCTION_ARN"