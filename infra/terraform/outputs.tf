output "repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "cluster_name" {
  value = aws_ecs_cluster.demo.name
}

output "service_name" {
  value = aws_ecs_service.api.name
}

output "mongodb_secret_arn" {
  description = "Solo ARN; Terraform no conoce el valor."
  value       = aws_secretsmanager_secret.mongodb.arn
}

output "log_group" {
  value = aws_cloudwatch_log_group.api.name
}
