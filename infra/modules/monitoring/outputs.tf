output "dashboard_name" {
  description = "Nombre del dashboard de CloudWatch"
  value       = aws_cloudwatch_dashboard.pipeline_dashboard.dashboard_name
}

output "log_group_name" {
  description = "Nombre del grupo de logs para DQ"
  value       = aws_cloudwatch_log_group.dq_metrics.name
}