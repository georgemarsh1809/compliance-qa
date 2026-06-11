resource "aws_s3_bucket" "corpus" {
    bucket = "compliance-qa-corpus-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket" "index" {
    bucket = "compliance-qa-index-${data.aws_caller_identity.current.account_id}"
}

data "aws_caller_identity" "current" {}

output "corpus_bucket_name" {
    value = aws_s3_bucket.corpus.bucket
}

output "index_bucket_name" {
    value = aws_s3_bucket.index.bucket
}
