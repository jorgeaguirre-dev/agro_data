# SNS topic for alerts
resource "aws_sns_topic" "pipeline_alerts" {
  name = "${var.project_name}-${var.environment}-pipeline-alerts"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Topic subscription (email example)
resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.alerts_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.pipeline_alerts.arn
  protocol  = "email"
  endpoint  = var.alerts_email
}

# Step Function definition
resource "aws_sfn_state_machine" "pipeline" {
  name     = "${var.project_name}-${var.environment}-pipeline"
  role_arn = var.step_functions_role_arn

  definition = templatefile("${path.module}/../../orchestration/step_functions/pipeline_definition.asl.json", {
    LANDING_BUCKET  = var.landing_bucket_id
    CURATED_BUCKET  = var.curated_bucket_id
    GLUE_JOB_RINDE  = var.glue_job_names.rinde_lotes
    GLUE_JOB_CLIMA  = var.glue_job_names.clima_diario
    GLUE_JOB_DQ     = var.glue_job_names.dq
    SNS_TOPIC_ARN   = aws_sns_topic.pipeline_alerts.arn
    REGION          = var.aws_region
    ACCOUNT_ID      = var.account_id
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Scheduled trigger (daily)
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  count               = var.create_schedule ? 1 : 0
  name                = "${var.project_name}-${var.environment}-daily-trigger"
  description         = "Daily trigger for the pipeline"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "step_function_target" {
  count     = var.create_schedule ? 1 : 0
  rule      = aws_cloudwatch_event_rule.daily_trigger[0].name
  target_id = "StartPipeline"
  arn       = aws_sfn_state_machine.pipeline.arn
  role_arn  = var.step_functions_role_arn
}