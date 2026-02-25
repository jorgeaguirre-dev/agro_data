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