output "state_machine_arn" {
  description = "ARN de la Step Function"
  value       = aws_sfn_state_machine.pipeline.arn
}

output "sns_topic_arn" {
  description = "ARN del topic SNS para alertas"
  value       = aws_sns_topic.pipeline_alerts.arn
}