#!/bin/bash
# demo.sh - Demostración completa del pipeline

echo "🎬 DEMO: Pipeline de Datos Agrícolas"
echo "====================================="

# 1. Mostrar infraestructura
echo "1️⃣ Infraestructura desplegada:"
terraform -chdir=infra output

# 2. Subir nuevos datos
echo "2️⃣ Subiendo nuevos datos de prueba..."
./scripts/upload_data.sh

# 3. Ejecutar pipeline
echo "3️⃣ Ejecutando Step Function..."
./scripts/run_step_function.sh

# 4. Consultar resultados
echo "4️⃣ Resultados en Athena:"
aws athena start-query-execution \
  --query-string "SELECT COUNT(*) as registros, 
                         AVG(rinde) as rinde_promedio,
                         MIN(rinde) as rinde_min,
                         MAX(rinde) as rinde_max
                  FROM agro_data_pipeline_dev_db.rinde_lotes" \
  --result-configuration "OutputLocation=s3://$(terraform -chdir=infra output -raw curated_bucket)/athena-results/" \
  --output text \
  --query 'QueryExecutionId'

echo "====================================="
echo "✅ Pipeline demostrado exitosamente!"