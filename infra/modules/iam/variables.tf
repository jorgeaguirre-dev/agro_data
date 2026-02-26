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