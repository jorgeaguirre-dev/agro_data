output "dashboard_name" {
  description = "CloudWatch dashboard name"
  value       = aws_cloudwatch_dashboard.pipeline_dashboard.dashboard_name
}

output "log_group_name" {
  description = "Log group name for DQ"
  value       = aws_cloudwatch_log_group.dq_metrics.name
}