#!/bin/bash

# Cargar outputs
# source "$(dirname "$0")/get_outputs.sh"

echo "🔄 Configurando tablas para Athena..."

# Opción 1: Usar crawlers (recomendado)
echo "📋 Creando crawlers..."

# Obtener account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
GLUE_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/agro-data-pipeline-dev-glue-role"

# Crear crawler para rinde
aws glue create-crawler \
  --name "agro-rinde-crawler" \
  --role $GLUE_ROLE_ARN \
  --database-name $DATABASE_NAME \
  --targets '{"S3Targets":[{"Path":"s3://'$CURATED_BUCKET'/rinde_lotes/"}]}' \
  --schema-change-policy '{"UpdateBehavior":"UPDATE_IN_DATABASE","DeleteBehavior":"DEPRECATE_IN_DATABASE"}' 2>/dev/null || echo "Crawler rinde ya existe"

# Crear crawler para clima
aws glue create-crawler \
  --name "agro-clima-crawler" \
  --role $GLUE_ROLE_ARN \
  --database-name $DATABASE_NAME \
  --targets '{"S3Targets":[{"Path":"s3://'$CURATED_BUCKET'/clima_diario/"}]}' \
  --schema-change-policy '{"UpdateBehavior":"UPDATE_IN_DATABASE","DeleteBehavior":"DEPRECATE_IN_DATABASE"}' 2>/dev/null || echo "Crawler clima ya existe"

# Ejecutar crawlers
echo "▶️ Ejecutando crawlers..."
aws glue start-crawler --name "agro-rinde-crawler"
aws glue start-crawler --name "agro-clima-crawler"

echo "⏳ Esperando que los crawlers terminen..."
sleep 10

# Verificar estado
for CRAWLER in "agro-rinde-crawler" "agro-clima-crawler"; do
    STATUS=$(aws glue get-crawler --name $CRAWLER --query 'Crawler.LastCrawl.Status' --output text)
    echo "  $CRAWLER: $STATUS"
done

echo ""
echo "✅ Tablas creadas. Para verificar:"
echo "  aws glue get-tables --database-name $DATABASE_NAME --query 'TableList[].Name'"
echo ""
echo "🔍 Para consultar en Athena:"
echo "  Database: $DATABASE_NAME"
echo "  Tablas: rinde_lotes, clima_diario"
echo ""
echo "Ejemplo de consulta:"
echo "  SELECT * FROM $DATABASE_NAME.rinde_lotes LIMIT 10;"