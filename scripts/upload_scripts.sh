#!/bin/bash

# Load outputs
cd infra
export SCRIPTS_BUCKET=$(terraform output -raw scripts_bucket)
cd ..

echo "📤 Uploading scripts to s3://${SCRIPTS_BUCKET}/"

# Upload main jobs
echo "  - Main jobs..."
aws s3 cp src/ingestion/jobs/ s3://${SCRIPTS_BUCKET}/jobs/ --recursive --exclude "*" --include "*.py"

# Upload Data Quality jobs
echo "  - Data Quality jobs..."
aws s3 cp src/dq/ s3://${SCRIPTS_BUCKET}/jobs/ --recursive --exclude "*" --include "*.py"

# Verify
echo "✅ Scripts in S3:"
aws s3 ls s3://${SCRIPTS_BUCKET}/jobs/ --recursive | grep "\.py" | tail -5