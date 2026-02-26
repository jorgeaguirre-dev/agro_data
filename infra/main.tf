terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Datos de la cuenta AWS
data "aws_caller_identity" "current" {}

# Módulo S3 (se crea primero)
module "s3" {
  source = "./modules/s3"
  
  environment  = var.environment
  project_name = var.project_name
}

# Módulo IAM (depende explícitamente de S3)
module "iam" {
  source = "./modules/iam"
  
  environment          = var.environment
  project_name         = var.project_name
  aws_region          = var.aws_region
  account_id           = data.aws_caller_identity.current.account_id
  landing_bucket_arn   = module.s3.landing_bucket_arn
  curated_bucket_arn   = module.s3.curated_bucket_arn
  scripts_bucket_arn   = module.s3.scripts_bucket_arn
  
  depends_on = [module.s3]  # FORZAR dependencia
}

# Módulo Glue (depende de IAM y S3)
module "glue" {
  source = "./modules/glue"
  
  environment       = var.environment
  project_name      = var.project_name
  glue_role_arn     = module.iam.glue_role_arn
  scripts_bucket_id = module.s3.scripts_bucket_id
  
  depends_on = [module.iam, module.s3]
}


# Step Function
resource "aws_sfn_state_machine" "pipeline" {
  name     = "${var.project_name}-${var.environment}-pipeline"
  role_arn = module.iam.step_functions_role_arn

  definition = templatefile("${path.module}/../orchestration/step_functions/pipeline_definition.asl.json", {
    GLUE_JOB_RINDE  = module.glue.job_names.rinde_lotes
    GLUE_JOB_CLIMA  = module.glue.job_names.clima_diario
    LANDING_BUCKET  = module.s3.landing_bucket_id
    CURATED_BUCKET  = module.s3.curated_bucket_id
  })
}


# Outputs
output "landing_bucket" {
  value = module.s3.landing_bucket_id
}

output "curated_bucket" {
  value = module.s3.curated_bucket_id
}

output "scripts_bucket" {
  value = module.s3.scripts_bucket_id
}

output "glue_jobs" {
  value = module.glue.job_names
}

output "glue_database" {
  value = module.glue.database_name
}

output "step_function_arn" {
  value = aws_sfn_state_machine.pipeline.arn
}