resource "aws_vpc" "demo" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "delivery-demo" }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.demo.id
  cidr_block        = "10.42.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_internet_gateway" "demo" {
  vpc_id = aws_vpc.demo.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.demo.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.demo.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "api" {
  name        = "delivery-demo-api"
  description = "API academica solo desde el presentador"
  vpc_id      = aws_vpc.demo.id

  ingress {
    description = "Demo HTTP restringida"
    protocol    = "tcp"
    from_port   = 8000
    to_port     = 8000
    cidr_blocks = [var.presenter_cidr]
  }
  egress {
    description = "ECR, S3, logs, secretos y DNS de Atlas"
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
