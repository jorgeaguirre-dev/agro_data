output "landing_bucket_id" {
  value = aws_s3_bucket.landing.id
}

output "landing_bucket_arn" {
  value = aws_s3_bucket.landing.arn
}

output "curated_bucket_id" {
  value = aws_s3_bucket.curated.id
}

output "curated_bucket_arn" {
  value = aws_s3_bucket.curated.arn
}

output "scripts_bucket_id" {
  value = aws_s3_bucket.scripts.id
}

output "scripts_bucket_arn" {
  value = aws_s3_bucket.scripts.arn
}