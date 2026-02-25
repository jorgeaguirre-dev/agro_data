# Obtener nombre del bucket landing
cd infra
LANDING_BUCKET=$(terraform output -raw landing_bucket)
cd ..

# Subir archivos de prueba
aws s3 cp data/rinde_lotes.csv s3://${LANDING_BUCKET}/
aws s3 cp data/clima_diario.csv s3://${LANDING_BUCKET}/

# Verificar
aws s3 ls s3://${LANDING_BUCKET}/
