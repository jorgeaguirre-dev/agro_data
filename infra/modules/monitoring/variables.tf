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

variable "glue_job_names" {
  description = "Glue job names"
  type        = map(string)
}

variable "alarm_sns_topic_arn" {
  description = "ARN of the SNS topic for alarms"
  type        = string
}