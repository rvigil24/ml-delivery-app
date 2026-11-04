# Consulta únicamente: nunca crear, importar o administrar el bucket compartido.
data "aws_s3_bucket" "resources" {
  bucket = "ml-kodigo-resources"
}

resource "aws_ecr_repository" "api" {
  name                 = "delivery-demo-api"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/delivery-demo-api"
  retention_in_days = 7
}

# Solo el contenedor del secreto. El valor se carga fuera de Terraform después
# de autorizar el despliegue; nunca entra en variables, plan o estado.
resource "aws_secretsmanager_secret" "mongodb" {
  name                    = "delivery-demo/mongodb-uri"
  recovery_window_in_days = 7
}

resource "aws_ecs_cluster" "demo" {
  name = "delivery-demo"
}

resource "aws_ecs_task_definition" "api" {
  family                   = "delivery-demo-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
  container_definitions = jsonencode([{
    name         = "api"
    image        = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
    essential    = true
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]
    environment = [
      { name = "AWS_REGION", value = "us-east-1" },
      { name = "S3_BUCKET", value = data.aws_s3_bucket.resources.bucket },
      { name = "S3_ENDPOINT_URL", value = "https://s3.us-east-1.amazonaws.com" },
      { name = "MONGODB_DATABASE", value = var.mongodb_database },
      { name = "DELIVERY_MODEL_V2_MANIFEST_KEY", value = "models/delivery-duration/meituan-eta-risk-v2/manifest.json" },
      { name = "DELIVERY_MODEL_V2_MANIFEST_SHA256", value = "0381a68fb7a7634823217d85718ce0efa5dad04fe3bf4f4b36358fa189d5e102" },
      { name = "DELIVERY_MODEL_V2_MANIFEST_SIZE", value = "1216" }
    ]
    secrets = [{ name = "MONGODB_URI", valueFrom = aws_secretsmanager_secret.mongodb.arn }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.api.name
        awslogs-region        = "us-east-1"
        awslogs-stream-prefix = "api"
      }
    }
    # /health verifica proceso, no disponibilidad de v2 o Atlas. La validación
    # funcional de predicción/persistencia se realiza aparte al desplegar.
    healthCheck = {
      command     = ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 120
    }
  }])
}

resource "aws_ecs_service" "api" {
  name                               = "delivery-demo-api"
  cluster                            = aws_ecs_cluster.demo.id
  task_definition                    = aws_ecs_task_definition.api.arn
  desired_count                      = var.desired_count
  launch_type                        = "FARGATE"
  platform_version                   = "1.4.0"
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100
  wait_for_steady_state              = true
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  network_configuration {
    subnets          = [aws_subnet.public.id]
    security_groups  = [aws_security_group.api.id]
    assign_public_ip = true
  }
  depends_on = [
    aws_route_table_association.public,
    aws_iam_role_policy.execution,
    aws_iam_role_policy.model
  ]
}
