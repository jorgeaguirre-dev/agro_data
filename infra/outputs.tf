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