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

variable "landing_bucket_arn" {
  description = "ARN of the landing bucket"
  type        = string
}

variable "curated_bucket_arn" {
  description = "ARN of the curated bucket"
  type        = string
}

variable "scripts_bucket_arn" {
  description = "ARN of the scripts bucket"
  type        = string
}