variable "environment" {
  description = "Ambiente de despliegue"
  type        = string
}

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "landing_bucket_arn" {
  description = "ARN del bucket landing"
  type        = string
}

variable "curated_bucket_arn" {
  description = "ARN del bucket curated"
  type        = string
}

variable "scripts_bucket_arn" {
  description = "ARN del bucket scripts"
  type        = string
}