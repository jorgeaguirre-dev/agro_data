output "job_names" {
  value = {
    rinde_lotes  = aws_glue_job.process_rinde_lotes.name
    clima_diario = aws_glue_job.process_clima_diario.name
  }
}

output "job_arns" {
  value = {
    rinde_lotes  = aws_glue_job.process_rinde_lotes.arn
    clima_diario = aws_glue_job.process_clima_diario.arn
  }
}