# Identidad real comprobada con la API GitHub; sin comodines de repositorio.
data "aws_caller_identity" "current" {}

locals {
  github_subject  = "repo:rvigil24@23065092/ml-delivery-app@1443588308:environment:aws-demo"
  task_family_arn = "arn:aws:ecs:us-east-1:${data.aws_caller_identity.current.account_id}:task-definition/delivery-demo-api:*"
}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  # GitHub se verifica con las CA de confianza AWS; no fijar thumbprints viejos.
}

resource "aws_iam_role" "github_deploy" {
  name                 = "delivery-demo-github-deploy"
  max_session_duration = 3600
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRoleWithWebIdentity"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = local.github_subject
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "github_deploy" {
  name = "publish-and-update-demo"
  role = aws_iam_role.github_deploy.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Action    = ["ecr:GetAuthorizationToken", "ec2:DescribeNetworkInterfaces"]
        Resource  = "*"
        Condition = { StringEquals = { "aws:RequestedRegion" = "us-east-1" } }
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:DescribeImages", "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload", "ecr:PutImage"
        ]
        Resource = aws_ecr_repository.api.arn
      },
      {
        Effect   = "Allow"
        Action   = ["ecs:RegisterTaskDefinition", "ecs:DescribeTaskDefinition"]
        Resource = local.task_family_arn
      },
      {
        Effect   = "Allow"
        Action   = ["ecs:DescribeServices"]
        Resource = aws_ecs_service.api.id
      },
      {
        Effect    = "Allow"
        Action    = ["ecs:UpdateService"]
        Resource  = aws_ecs_service.api.id
        Condition = { ArnLike = { "ecs:task-definition" = local.task_family_arn } }
      },
      {
        Effect    = "Allow"
        Action    = ["ecs:ListTasks"]
        Resource  = "*"
        Condition = { ArnEquals = { "ecs:cluster" = aws_ecs_cluster.demo.arn } }
      },
      {
        Effect   = "Allow"
        Action   = ["ecs:DescribeTasks"]
        Resource = "arn:aws:ecs:us-east-1:${data.aws_caller_identity.current.account_id}:task/delivery-demo/*"
      },
      {
        Effect    = "Allow"
        Action    = ["iam:PassRole"]
        Resource  = [aws_iam_role.execution.arn, aws_iam_role.task.arn]
        Condition = { StringEquals = { "iam:PassedToService" = "ecs-tasks.amazonaws.com" } }
      }
    ]
  })
}
