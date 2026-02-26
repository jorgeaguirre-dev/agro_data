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

variable "glue_job_names" {
  description = "Nombres de los jobs de Glue"
  type        = map(string)
}

variable "alarm_sns_topic_arn" {
  description = "ARN del topic SNS para alarmas"
  type        = string
}