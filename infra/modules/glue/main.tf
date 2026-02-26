# Glue Catalog Database
resource "aws_glue_catalog_database" "db" {
  name = "${var.project_name}_${var.environment}_db"
}

# Job para procesar rinde de lotes
resource "aws_glue_job" "process_rinde_lotes" {
  name     = "${var.project_name}-${var.environment}-process-rinde-lotes"
  role_arn = var.glue_role_arn

  command {
    script_location = "s3://${var.scripts_bucket_id}/jobs/process_rinde_lotes.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                       = "python"
    "--enable-continuous-cloudwatch-log"    = "true"
    "--enable-auto-scaling"                 = "true"
    "--enable-metrics"                       = "true"
    "--TempDir"                             = "s3://${var.scripts_bucket_id}/temporary/"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
}

# Job para procesar clima diario
resource "aws_glue_job" "process_clima_diario" {
  name     = "${var.project_name}-${var.environment}-process-clima-diario"
  role_arn = var.glue_role_arn

  command {
    script_location = "s3://${var.scripts_bucket_id}/jobs/process_clima_diario.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                       = "python"
    "--enable-continuous-cloudwatch-log"    = "true"
    "--enable-auto-scaling"                 = "true"
    "--enable-metrics"                       = "true"
    "--TempDir"                             = "s3://${var.scripts_bucket_id}/temporary/"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
}

# Job para Data Quality (Great Expectations)
resource "aws_glue_job" "great_expectations" {
  name     = "${var.project_name}-${var.environment}-dq-job"
  role_arn = var.glue_role_arn

  command {
    script_location = "s3://${var.scripts_bucket_id}/jobs/great_expectations_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                       = "python"
    "--enable-continuous-cloudwatch-log"    = "true"
    "--enable-metrics"                      = "true"
    "--enable-spark-ui"                     = "true"
    "--spark-event-logs-path"               = "s3://${var.scripts_bucket_id}/spark-logs/"
    "--TempDir"                             = "s3://${var.scripts_bucket_id}/temporary/"
  }

  glue_version      = "4.0"
  worker_type       = "Standard"
  number_of_workers = 2
  timeout           = 30

  tags = {
    Environment = var.environment
    Service     = "data-quality"
  }
}