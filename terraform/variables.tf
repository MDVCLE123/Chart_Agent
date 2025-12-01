variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "chart-agent"
}

# Network Configuration
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# Cost Control Variables
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (costs ~$32/month)"
  type        = bool
  default     = false
}

variable "enable_alb" {
  description = "Enable Application Load Balancer"
  type        = bool
  default     = false
}

variable "ecs_backend_count" {
  description = "Number of backend ECS tasks"
  type        = number
  default     = 0
}

variable "ecs_frontend_count" {
  description = "Number of frontend ECS tasks"
  type        = number
  default     = 0
}

# HealthLake Configuration
variable "healthlake_datastore_name" {
  description = "HealthLake data store name"
  type        = string
  default     = "chart-agent-dev"
}

# ECS Configuration
variable "backend_image_tag" {
  description = "Backend Docker image tag"
  type        = string
  default     = "latest"
}

variable "frontend_image_tag" {
  description = "Frontend Docker image tag"
  type        = string
  default     = "latest"
}

variable "backend_cpu" {
  description = "Backend task CPU units"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Backend task memory (MB)"
  type        = number
  default     = 512
}

variable "frontend_cpu" {
  description = "Frontend task CPU units"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Frontend task memory (MB)"
  type        = number
  default     = 512
}

