variable "environment" {
  description = "Ambiente de despliegue"
  type        = string
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "glue_role_arn" {
  description = "ARN del rol IAM para Glue"
  type        = string
}

variable "scripts_bucket_id" {
  description = "ID del bucket scripts"
  type        = string
}