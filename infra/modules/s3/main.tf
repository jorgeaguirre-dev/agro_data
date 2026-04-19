# Create buckets (no tags)
resource "aws_s3_bucket" "landing" {
  bucket = "${var.project_name}-${var.environment}-landing"
}

resource "aws_s3_bucket" "curated" {
  bucket = "${var.project_name}-${var.environment}-curated"
}

resource "aws_s3_bucket" "scripts" {
  bucket = "${var.project_name}-${var.environment}-scripts"
}

# Single block for public access block
resource "aws_s3_bucket_public_access_block" "all" {
  for_each = {
    landing  = aws_s3_bucket.landing.id
    curated  = aws_s3_bucket.curated.id
    scripts  = aws_s3_bucket.scripts.id
  }

  bucket = each.value

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Single block for encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "all" {
  for_each = {
    landing  = aws_s3_bucket.landing.id
    curated  = aws_s3_bucket.curated.id
    scripts  = aws_s3_bucket.scripts.id
  }

  bucket = each.value

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Versioning only for curated (optional)
resource "aws_s3_bucket_versioning" "curated" {
  bucket = aws_s3_bucket.curated.id
  versioning_configuration {
    status = "Enabled"
  }
}