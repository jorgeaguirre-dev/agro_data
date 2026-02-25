variable "environment" {
  description = "Ambiente de despliegue"
  type        = string
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "account_id" {
  description = "ID de la cuenta AWS"
  type        = string
}

variable "landing_bucket_id" {
  description = "ID del bucket landing"
  type        = string
}

variable "curated_bucket_id" {
  description = "ID del bucket curated"
  type        = string
}

variable "glue_job_names" {
  description = "Nombres de los jobs de Glue"
  type        = map(string)
}

variable "step_functions_role_arn" {
  description = "ARN del rol IAM para Step Functions"
  type        = string
}

variable "alerts_email" {
  description = "Email para alertas"
  type        = string
  default     = ""
}

variable "create_schedule" {
  description = "Crear trigger programado"
  type        = bool
  default     = true
}

variable "schedule_expression" {
  description = "Expresión de schedule para CloudWatch (cron o rate)"
  type        = string
  default     = "cron(0 8 * * ? *)"  # 8 AM todos los días
}