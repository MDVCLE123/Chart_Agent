# Development environment configuration (minimal cost)
environment              = "dev"
enable_nat_gateway       = false
enable_alb               = false
ecs_backend_count        = 0
ecs_frontend_count       = 0
healthlake_datastore_name = "chart-agent-dev"

# Use smaller resources for dev
backend_cpu     = 256
backend_memory  = 512
frontend_cpu    = 256
frontend_memory = 512

