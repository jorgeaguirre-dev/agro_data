variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "account_id" {
  description = "AWS account ID"
  type        = string
}

variable "landing_bucket_id" {
  description = "Landing bucket ID"
  type        = string
}

variable "curated_bucket_id" {
  description = "Curated bucket ID"
  type        = string
}

variable "glue_job_names" {
  description = "Glue job names"
  type        = map(string)
}

variable "step_functions_role_arn" {
  description = "ARN of the IAM role for Step Functions"
  type        = string
}

variable "alerts_email" {
  description = "Email for alerts"
  type        = string
  default     = ""
}

variable "create_schedule" {
  description = "Create scheduled trigger"
  type        = bool
  default     = true
}

variable "schedule_expression" {
  description = "Schedule expression for CloudWatch (cron or rate)"
  type        = string
  default     = "cron(0 8 * * ? *)"  # 8 AM every day
}