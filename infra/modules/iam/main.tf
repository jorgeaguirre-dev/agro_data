# Rol para Glue Jobs
resource "aws_iam_role" "glue_role" {
  name = "${var.project_name}-${var.environment}-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

# Política simplificada
resource "aws_iam_policy" "glue_policy" {
  name        = "${var.project_name}-${var.environment}-glue-policy"
  description = "Permisos para jobs de Glue"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.landing_bucket_arn,
          "${var.landing_bucket_arn}/*",
          var.curated_bucket_arn,
          "${var.curated_bucket_arn}/*",
          var.scripts_bucket_arn,
          "${var.scripts_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Adjuntar política personalizada
resource "aws_iam_role_policy_attachment" "glue_policy_attach" {
  role       = aws_iam_role.glue_role.name
  policy_arn = aws_iam_policy.glue_policy.arn
}

# Adjuntar política AWS administrada
resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Rol para Step Functions
resource "aws_iam_role" "step_functions_role" {
  name = "${var.project_name}-${var.environment}-stepfunctions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

# Política para Step Functions
resource "aws_iam_policy" "step_functions_policy" {
  name        = "${var.project_name}-${var.environment}-stepfunctions-policy"
  description = "Permisos para Step Functions ejecutar jobs y crawlers de Glue"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:StartJobRun",
          "glue:GetJobRun",
          "glue:GetJobRuns",
          "glue:StartCrawler",
          "glue:GetCrawler",
          "glue:GetCrawlerMetrics"
        ],
        Resource = [
          "arn:aws:glue:${var.aws_region}:${var.account_id}:job/${var.project_name}-${var.environment}-process-rinde-lotes",
          "arn:aws:glue:${var.aws_region}:${var.account_id}:job/${var.project_name}-${var.environment}-process-clima-diario",
          "arn:aws:glue:${var.aws_region}:${var.account_id}:job/${var.project_name}-${var.environment}-dq-job",
          "arn:aws:glue:${var.aws_region}:${var.account_id}:crawler/agro-rinde-crawler",
          "arn:aws:glue:${var.aws_region}:${var.account_id}:crawler/agro-clima-crawler"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "step_functions_policy_attach" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = aws_iam_policy.step_functions_policy.arn
}