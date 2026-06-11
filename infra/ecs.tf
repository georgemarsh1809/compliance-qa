resource "aws_ecs_cluster" "backend" {
  name = "compliance-qa"
}

resource "aws_ecs_express_gateway_service" "backend" {
  cluster                 = aws_ecs_cluster.backend.name
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  infrastructure_role_arn = aws_iam_role.ecs_infrastructure.arn
  task_role_arn           = aws_iam_role.ecs_task.arn
  health_check_path       = "/health"
  cpu                     = "1024"
  memory                  = "2048"
  region                  = "eu-west-2"

  primary_container {
    image          = "${aws_ecr_repository.backend.repository_url}:latest"
    container_port = 8000

    environment {
      name  = "ANTHROPIC_API_KEY"
      value = var.anthropic_api_key
    }

    environment {
      name  = "VOYAGE_API_KEY"
      value = var.voyage_api_key
    }

    environment {
      name  = "S3_CORPUS_BUCKET"
      value = aws_s3_bucket.corpus.bucket
    }

    environment {
      name  = "S3_INDEX_BUCKET"
      value = aws_s3_bucket.index.bucket
    }
  }
}

output "service_url" {
  value = aws_ecs_express_gateway_service.backend.ingress_paths
}
