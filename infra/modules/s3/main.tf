# Crear buckets (sin tags)
resource "aws_s3_bucket" "landing" {
  bucket = "${var.project_name}-${var.environment}-landing"
}

resource "aws_s3_bucket" "curated" {
  bucket = "${var.project_name}-${var.environment}-curated"
}

resource "aws_s3_bucket" "scripts" {
  bucket = "${var.project_name}-${var.environment}-scripts"
}

# Bloque único para public access block
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

# Bloque único para cifrado
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

# Versionado solo para curated (opcional)
resource "aws_s3_bucket_versioning" "curated" {
  bucket = aws_s3_bucket.curated.id
  versioning_configuration {
    status = "Enabled"
  }
}