variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "glue_role_arn" {
  description = "ARN of the IAM role for Glue"
  type        = string
}

variable "scripts_bucket_id" {
  description = "Scripts bucket ID"
  type        = string
}