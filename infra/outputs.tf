output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnets" {
  value = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "ecr_repo_url" {
  value = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "alb_dns" {
  value = aws_lb.app.dns_name
}