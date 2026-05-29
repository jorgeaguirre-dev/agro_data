# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "pipeline_dashboard" {
  dashboard_name = "${var.project_name}-${var.environment}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Glue", "glue.driver.aggregate.elapsedTime", { stat = "Average" }],
            ["AWS/Glue", "glue.driver.aggregate.bytesRead", { stat = "Sum" }],
            ["AWS/Glue", "glue.driver.aggregate.bytesWritten", { stat = "Sum" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Glue Jobs Metrics"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/States", "ExecutionsStarted", { stat = "Sum" }],
            ["AWS/States", "ExecutionsSucceeded", { stat = "Sum" }],
            ["AWS/States", "ExecutionsFailed", { stat = "Sum" }],
            ["AWS/States", "ExecutionTime", { stat = "Average" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Step Functions Metrics"
        }
      }
    ]
  })
}

# Alarm for Glue Job failures
resource "aws_cloudwatch_metric_alarm" "glue_job_failures" {
  for_each = var.glue_job_names

  alarm_name          = "${var.project_name}-${var.environment}-${each.value}-failure"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name        = "Failed"
  namespace          = "AWS/Glue"
  period             = 300
  statistic          = "Sum"
  threshold          = 0
  alarm_description  = "Alarm for Glue job failure: ${each.value}"
  alarm_actions      = [var.alarm_sns_topic_arn]

  dimensions = {
    JobName = each.value
    JobRunId = "ALL"
    Type     = "ALL"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Alarm for high null rate (custom metric)
resource "aws_cloudwatch_metric_alarm" "high_null_rate" {
  alarm_name          = "${var.project_name}-${var.environment}-high-null-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name        = "NullPercentage"
  namespace          = "Agro/DataQuality"
  period             = 300
  statistic          = "Average"
  threshold          = 5.0  # 5% null rate
  alarm_description  = "Alarm for high null rate in data"
  alarm_actions      = [var.alarm_sns_topic_arn]

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Log group for custom metrics
resource "aws_cloudwatch_log_group" "dq_metrics" {
  name              = "/aws/glue/${var.project_name}-${var.environment}/dq-metrics"
  retention_in_days = 30

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}