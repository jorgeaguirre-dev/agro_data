output "database_name" {
  value = aws_glue_catalog_database.db.name
}

output "job_names" {
  value = {
    rinde_lotes  = aws_glue_job.process_rinde_lotes.name
    clima_diario = aws_glue_job.process_clima_diario.name
    dq           = aws_glue_job.great_expectations.name
  }
}

output "job_arns" {
  value = {
    rinde_lotes  = aws_glue_job.process_rinde_lotes.arn
    clima_diario = aws_glue_job.process_clima_diario.arn
    dq           = aws_glue_job.great_expectations.arn
  }
}