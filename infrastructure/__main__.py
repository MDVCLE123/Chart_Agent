"""
Chart Preparation Agent - Pulumi Infrastructure
AWS infrastructure defined in Python using Pulumi
"""

import pulumi
import pulumi_aws as aws
from pulumi import Config, export

# Load configuration
config = Config()
environment = config.get("environment") or "dev"
enable_nat_gateway = config.get_bool("enableNATGateway") or False
enable_alb = config.get_bool("enableALB") or False
ecs_backend_count = config.get_int("ecsBackendCount") or 0
ecs_frontend_count = config.get_int("ecsFrontendCount") or 0

# Tags to apply to all resources
common_tags = {
    "Project": "ChartAgent",
    "Environment": environment,
    "ManagedBy": "Pulumi",
}

# ====================
# VPC & Networking
# ====================

# VPC
vpc = aws.ec2.Vpc(
    f"{environment}-chart-agent-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={**common_tags, "Name": f"{environment}-chart-agent-vpc"},
)

# Internet Gateway
igw = aws.ec2.InternetGateway(
    f"{environment}-chart-agent-igw",
    vpc_id=vpc.id,
    tags={**common_tags, "Name": f"{environment}-chart-agent-igw"},
)

# Public Subnets
public_subnet_1 = aws.ec2.Subnet(
    f"{environment}-chart-agent-public-1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone=aws.get_availability_zones().names[0],
    map_public_ip_on_launch=True,
    tags={**common_tags, "Name": f"{environment}-chart-agent-public-1", "Type": "Public"},
)

public_subnet_2 = aws.ec2.Subnet(
    f"{environment}-chart-agent-public-2",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone=aws.get_availability_zones().names[1],
    map_public_ip_on_launch=True,
    tags={**common_tags, "Name": f"{environment}-chart-agent-public-2", "Type": "Public"},
)

# Private Subnets
private_subnet_1 = aws.ec2.Subnet(
    f"{environment}-chart-agent-private-1",
    vpc_id=vpc.id,
    cidr_block="10.0.11.0/24",
    availability_zone=aws.get_availability_zones().names[0],
    tags={**common_tags, "Name": f"{environment}-chart-agent-private-1", "Type": "Private"},
)

private_subnet_2 = aws.ec2.Subnet(
    f"{environment}-chart-agent-private-2",
    vpc_id=vpc.id,
    cidr_block="10.0.12.0/24",
    availability_zone=aws.get_availability_zones().names[1],
    tags={**common_tags, "Name": f"{environment}-chart-agent-private-2", "Type": "Private"},
)

# Public Route Table
public_route_table = aws.ec2.RouteTable(
    f"{environment}-chart-agent-public-rt",
    vpc_id=vpc.id,
    tags={**common_tags, "Name": f"{environment}-chart-agent-public-rt"},
)

public_route = aws.ec2.Route(
    f"{environment}-chart-agent-public-route",
    route_table_id=public_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=igw.id,
)

# Associate public subnets with public route table
public_rt_assoc_1 = aws.ec2.RouteTableAssociation(
    f"{environment}-chart-agent-public-rt-assoc-1",
    subnet_id=public_subnet_1.id,
    route_table_id=public_route_table.id,
)

public_rt_assoc_2 = aws.ec2.RouteTableAssociation(
    f"{environment}-chart-agent-public-rt-assoc-2",
    subnet_id=public_subnet_2.id,
    route_table_id=public_route_table.id,
)

# NAT Gateway (conditional)
nat_eip = None
nat_gateway = None

if enable_nat_gateway:
    nat_eip = aws.ec2.Eip(
        f"{environment}-chart-agent-nat-eip",
        vpc=True,
        tags={**common_tags, "Name": f"{environment}-chart-agent-nat-eip"},
    )
    
    nat_gateway = aws.ec2.NatGateway(
        f"{environment}-chart-agent-nat",
        allocation_id=nat_eip.id,
        subnet_id=public_subnet_1.id,
        tags={**common_tags, "Name": f"{environment}-chart-agent-nat"},
    )

# Private Route Table
private_route_table = aws.ec2.RouteTable(
    f"{environment}-chart-agent-private-rt",
    vpc_id=vpc.id,
    tags={**common_tags, "Name": f"{environment}-chart-agent-private-rt"},
)

# Private route to NAT Gateway (if enabled)
if enable_nat_gateway and nat_gateway:
    private_route = aws.ec2.Route(
        f"{environment}-chart-agent-private-route",
        route_table_id=private_route_table.id,
        destination_cidr_block="0.0.0.0/0",
        nat_gateway_id=nat_gateway.id,
    )

# Associate private subnets with private route table
private_rt_assoc_1 = aws.ec2.RouteTableAssociation(
    f"{environment}-chart-agent-private-rt-assoc-1",
    subnet_id=private_subnet_1.id,
    route_table_id=private_route_table.id,
)

private_rt_assoc_2 = aws.ec2.RouteTableAssociation(
    f"{environment}-chart-agent-private-rt-assoc-2",
    subnet_id=private_subnet_2.id,
    route_table_id=private_route_table.id,
)

# ====================
# Security Groups
# ====================

# ALB Security Group (conditional)
alb_security_group = None
if enable_alb:
    alb_security_group = aws.ec2.SecurityGroup(
        f"{environment}-chart-agent-alb-sg",
        vpc_id=vpc.id,
        description="Security group for Application Load Balancer",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=80,
                to_port=80,
                cidr_blocks=["0.0.0.0/0"],
                description="Allow HTTP from anywhere",
            ),
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["0.0.0.0/0"],
                description="Allow HTTPS from anywhere",
            ),
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
                description="Allow all outbound traffic",
            ),
        ],
        tags={**common_tags, "Name": f"{environment}-chart-agent-alb-sg"},
    )

# ECS Security Group
ecs_security_group_ingress = []
if enable_alb and alb_security_group:
    ecs_security_group_ingress = [
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=8000,
            to_port=8000,
            security_groups=[alb_security_group.id],
            description="Allow backend traffic from ALB",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=3000,
            to_port=3000,
            security_groups=[alb_security_group.id],
            description="Allow frontend traffic from ALB",
        ),
    ]

ecs_security_group = aws.ec2.SecurityGroup(
    f"{environment}-chart-agent-ecs-sg",
    vpc_id=vpc.id,
    description="Security group for ECS tasks",
    ingress=ecs_security_group_ingress,
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
            description="Allow all outbound traffic",
        ),
    ],
    tags={**common_tags, "Name": f"{environment}-chart-agent-ecs-sg"},
)

# ====================
# IAM Roles
# ====================

# ECS Task Execution Role
ecs_task_execution_role = aws.iam.Role(
    f"{environment}-chart-agent-ecs-execution-role",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }""",
    tags={**common_tags, "Name": f"{environment}-chart-agent-ecs-execution-role"},
)

ecs_task_execution_role_policy_attachment = aws.iam.RolePolicyAttachment(
    f"{environment}-chart-agent-ecs-execution-policy",
    role=ecs_task_execution_role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
)

# ECS Task Role (for HealthLake and Bedrock access)
ecs_task_role = aws.iam.Role(
    f"{environment}-chart-agent-ecs-task-role",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }""",
    tags={**common_tags, "Name": f"{environment}-chart-agent-ecs-task-role"},
)

ecs_task_role_policy = aws.iam.RolePolicy(
    f"{environment}-chart-agent-ecs-task-policy",
    role=ecs_task_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "healthlake:ReadResource",
                    "healthlake:SearchWithGet",
                    "healthlake:GetFHIRResource"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel"],
                "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
            }
        ]
    }""",
)

# ====================
# ECR Repositories
# ====================

backend_ecr = aws.ecr.Repository(
    "chart-agent-backend",
    name="chart-agent-backend",
    image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
        scan_on_push=True,
    ),
    tags={**common_tags, "Name": "chart-agent-backend"},
)

# Lifecycle policy to keep only last 10 images
backend_ecr_lifecycle_policy = aws.ecr.LifecyclePolicy(
    "chart-agent-backend-lifecycle",
    repository=backend_ecr.name,
    policy="""{
        "rules": [{
            "rulePriority": 1,
            "description": "Keep last 10 images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": {"type": "expire"}
        }]
    }""",
)

frontend_ecr = aws.ecr.Repository(
    "chart-agent-frontend",
    name="chart-agent-frontend",
    image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
        scan_on_push=True,
    ),
    tags={**common_tags, "Name": "chart-agent-frontend"},
)

frontend_ecr_lifecycle_policy = aws.ecr.LifecyclePolicy(
    "chart-agent-frontend-lifecycle",
    repository=frontend_ecr.name,
    policy="""{
        "rules": [{
            "rulePriority": 1,
            "description": "Keep last 10 images",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": {"type": "expire"}
        }]
    }""",
)

# ====================
# CloudWatch Log Groups
# ====================

backend_log_group = aws.cloudwatch.LogGroup(
    f"{environment}-chart-agent-backend-logs",
    name=f"/ecs/{environment}-chart-agent-backend",
    retention_in_days=7,
    tags=common_tags,
)

frontend_log_group = aws.cloudwatch.LogGroup(
    f"{environment}-chart-agent-frontend-logs",
    name=f"/ecs/{environment}-chart-agent-frontend",
    retention_in_days=7,
    tags=common_tags,
)

# ====================
# ECS Cluster
# ====================

ecs_cluster = aws.ecs.Cluster(
    f"{environment}-chart-agent-cluster",
    name=f"{environment}-chart-agent-cluster",
    settings=[
        aws.ecs.ClusterSettingArgs(
            name="containerInsights",
            value="enabled",
        ),
    ],
    tags={**common_tags, "Name": f"{environment}-chart-agent-cluster"},
)

# ====================
# Application Load Balancer (Conditional)
# ====================

alb = None
backend_target_group = None
frontend_target_group = None

if enable_alb and alb_security_group:
    alb = aws.lb.LoadBalancer(
        f"{environment}-chart-agent-alb",
        name=f"{environment}-chart-agent-alb",
        load_balancer_type="application",
        subnets=[public_subnet_1.id, public_subnet_2.id],
        security_groups=[alb_security_group.id],
        tags={**common_tags, "Name": f"{environment}-chart-agent-alb"},
    )
    
    backend_target_group = aws.lb.TargetGroup(
        f"{environment}-backend-tg",
        name=f"{environment}-backend-tg",
        port=8000,
        protocol="HTTP",
        vpc_id=vpc.id,
        target_type="ip",
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            path="/api/health",
            protocol="HTTP",
            interval=30,
            timeout=5,
            healthy_threshold=2,
            unhealthy_threshold=3,
        ),
        tags=common_tags,
    )
    
    frontend_target_group = aws.lb.TargetGroup(
        f"{environment}-frontend-tg",
        name=f"{environment}-frontend-tg",
        port=80,
        protocol="HTTP",
        vpc_id=vpc.id,
        target_type="ip",
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            path="/",
            protocol="HTTP",
            interval=30,
            timeout=5,
            healthy_threshold=2,
            unhealthy_threshold=3,
        ),
        tags=common_tags,
    )
    
    # ALB Listener
    alb_listener = aws.lb.Listener(
        f"{environment}-chart-agent-alb-listener",
        load_balancer_arn=alb.arn,
        port=80,
        protocol="HTTP",
        default_actions=[
            aws.lb.ListenerDefaultActionArgs(
                type="forward",
                target_group_arn=frontend_target_group.arn,
            ),
        ],
    )
    
    # Backend Listener Rule
    backend_listener_rule = aws.lb.ListenerRule(
        f"{environment}-backend-listener-rule",
        listener_arn=alb_listener.arn,
        priority=1,
        actions=[
            aws.lb.ListenerRuleActionArgs(
                type="forward",
                target_group_arn=backend_target_group.arn,
            ),
        ],
        conditions=[
            aws.lb.ListenerRuleConditionArgs(
                path_pattern=aws.lb.ListenerRuleConditionPathPatternArgs(
                    values=["/api/*"],
                ),
            ),
        ],
    )

# ====================
# Exports
# ====================

export("vpc_id", vpc.id)
export("public_subnet_1_id", public_subnet_1.id)
export("public_subnet_2_id", public_subnet_2.id)
export("private_subnet_1_id", private_subnet_1.id)
export("private_subnet_2_id", private_subnet_2.id)
export("ecs_cluster_name", ecs_cluster.name)
export("ecs_cluster_arn", ecs_cluster.arn)
export("backend_ecr_repository_url", backend_ecr.repository_url)
export("frontend_ecr_repository_url", frontend_ecr.repository_url)
export("ecs_task_execution_role_arn", ecs_task_execution_role.arn)
export("ecs_task_role_arn", ecs_task_role.arn)
export("ecs_security_group_id", ecs_security_group.id)

if enable_alb and alb:
    export("alb_dns_name", alb.dns_name)
    export("backend_target_group_arn", backend_target_group.arn)
    export("frontend_target_group_arn", frontend_target_group.arn)

if enable_nat_gateway and nat_eip:
    export("nat_gateway_ip", nat_eip.public_ip)

