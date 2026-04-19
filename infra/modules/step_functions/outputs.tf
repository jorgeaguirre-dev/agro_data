output "state_machine_arn" {
  description = "ARN of the Step Function"
  value       = aws_sfn_state_machine.pipeline.arn
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = aws_sns_topic.pipeline_alerts.arn
}