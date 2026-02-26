# Agro Data Pipeline

Pipeline de datos para procesamiento de información agrícola en AWS.

## 📋 Prerrequisitos

- AWS CLI configurado
- Terraform >= 1.0
- Python 3.9+

## 🏗️ Arquitectura

- **Ingesta**: CSV → S3 Landing
- **Procesamiento**: AWS Glue (PySpark)
- **Orquestación**: AWS Step Functions
- **Catálogo**: AWS Glue Data Catalog
- **Data Quality**: Great Expectations
- **Consumo**: Amazon Athena

## 📁 Estructura del Proyecto
agro_data/
├── .github/workflows/ # CI/CD
├── infra/ # Terraform
├── src/ # Código fuente
│ ├── ingestion/ # Jobs de Glue
│ └── dq/ # Data Quality
├── tests/ # Tests
└── orchestration/ # Step Functions

## 🚀 Despliegue rápido

```bash
# 1. Clonar repositorio
git clone agro_data
cd agro_data

# 2. Desplegar infraestructura
cd infra
terraform init
terraform apply
cd ..

# 3. Subir scripts de Glue
./scripts/upload_scripts.sh

# 4. Subir datos de prueba
aws s3 cp data/rinde_lotes.csv s3://$(cd infra && terraform output -raw landing_bucket)/
aws s3 cp data/clima_diario.csv s3://$(cd infra && terraform output -raw landing_bucket)/

```bash
# Obtener los valores correctamente
cd infra
RINDE_JOB=$(terraform output -json glue_jobs | jq -r '.rinde_lotes')
CLIMA_JOB=$(terraform output -json glue_jobs | jq -r '.clima_diario')
LANDING_BUCKET=$(terraform output -raw landing_bucket)
CURATED_BUCKET=$(terraform output -raw curated_bucket)

# Verificar que se obtuvieron
echo "RINDE_JOB: $RINDE_JOB"
echo "CLIMA_JOB: $CLIMA_JOB"
echo "LANDING_BUCKET: $LANDING_BUCKET"
echo "CURATED_BUCKET: $CURATED_BUCKET"
cd ..

# Ejecutar job de rinde
aws glue start-job-run \
  --job-name ${RINDE_JOB} \
  --arguments '{"--input_path":"s3://'${LANDING_BUCKET}'/rinde_lotes.csv","--output_path":"s3://'${CURATED_BUCKET}'/rinde_lotes"}'

# Ejecutar job de clima
aws glue start-job-run \
  --job-name ${CLIMA_JOB} \
  --arguments '{"--input_path":"s3://'${LANDING_BUCKET}'/clima_diario.csv","--output_path":"s3://'${CURATED_BUCKET}'/clima_diario"}'

aws glue get-job-runs --job-name ${RINDE_JOB} --max-items 1
aws glue get-job-runs --job-name ${CLIMA_JOB} --max-items 1

# Ver archivos Parquet generados
aws s3 ls s3://${CURATED_BUCKET}/rinde_lotes/ --recursive
aws s3 ls s3://${CURATED_BUCKET}/clima_diario/ --recursive

# Ver archivos Parquet generados
aws s3 ls s3://${CURATED_BUCKET}/rinde_lotes/ --recursive
aws s3 ls s3://${CURATED_BUCKET}/clima_diario/ --recursive
```

## 🔄 Flujo completo del pipeline

### Pasos manuales (solo primera vez)
1. **Desplegar infraestructura**: `cd infra && terraform apply`
2. **Subir scripts**: `./scripts/upload_scripts.sh`
3. **Crear crawlers** (una vez): 
```bash
aws glue create-crawler --name "agro-rinde-crawler" --role arn:aws:iam::... --database-name agro_data_pipeline_dev_db --targets '{"S3Targets":[{"Path":"s3://.../rinde_lotes/"}]}'
aws glue create-crawler --name "agro-clima-crawler" --role arn:aws:iam::... --database-name agro_data_pipeline_dev_db --targets '{"S3Targets":[{"Path":"s3://.../clima_diario/"}]}'
```

## Pipeline automático (después de configurado)
bash
# Opción 1: Ejecutar Step Function
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:...:pipeline

# Opción 2: Trigger programado (CloudWatch Events)
# - Se ejecuta automáticamente cada día a las 8 AM

## Pipeline (Deploy MVP)
```bash
# 1. Desplegar infraestructura (UNA VEZ)
cd infra
terraform apply
cd ..

# 2. Subir scripts a S3 (UNA VEZ, o cuando cambien)
./scripts/upload_scripts.sh

# 3. Subir datos raw (CADA VEZ que llegan nuevos datos)
./scripts/upload_data.sh

# 4. Ejecutar Step Function (AUTOMATIZABLE)
./scripts/run_step_function.sh

# 5. Consultar en Athena (A Demanda)
# (desde consola o script)
-- Ejemplo de consulta que podemos realizar
SELECT 
    r.lote_id,
    r.campana,
    r.rinde,
    c.temperatura,
    c.precipitacion
FROM agro_data_pipeline_dev_db.rinde_lotes r
JOIN agro_data_pipeline_dev_db.clima_diario c
    ON r.lote_id = c.lote_id 
    AND substr(r.fecha_cosecha,1,10) = c.fecha
WHERE r.rinde > 5000
LIMIT 10;
```