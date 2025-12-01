# Testing environment configuration (full stack)
environment              = "testing"
enable_nat_gateway       = true
enable_alb               = true
ecs_backend_count        = 1
ecs_frontend_count       = 1
healthlake_datastore_name = "chart-agent-dev"

# Standard resources for testing
backend_cpu     = 512
backend_memory  = 1024
frontend_cpu    = 256
frontend_memory = 512

