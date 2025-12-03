# Pulumi Infrastructure Guide

Complete guide for using Pulumi with Python for the Chart Preparation Agent.

## What is Pulumi?

Pulumi is a modern Infrastructure as Code (IaC) tool that lets you define cloud infrastructure using **real programming languages** like Python, TypeScript, Go, C#, or Java - instead of YAML or JSON templates.

### Why Pulumi with Python?

✅ **Real Python Code**: Use actual Python, not YAML config files  
✅ **IDE Support**: Autocomplete, type checking, refactoring  
✅ **Programming Logic**: Loops, conditionals, functions, classes  
✅ **Testing**: Unit test your infrastructure code  
✅ **Multi-Cloud**: Same code works for AWS, Azure, GCP, Kubernetes  
✅ **State Management**: Pulumi Cloud (free) or self-hosted  
✅ **Better Errors**: Stack traces instead of cryptic YAML errors  

### Pulumi vs Other Tools

| Feature | Pulumi | CloudFormation | Terraform |
|---------|--------|----------------|-----------|
| **Language** | Python, TS, Go, etc. | YAML/JSON | HCL |
| **IDE Support** | Full autocomplete | YAML validation | Limited |
| **Type Safety** | Yes (with Python types) | No | Limited |
| **Loops/Logic** | Native Python | Template magic | HCL syntax |
| **Testing** | Unit tests | Limited | Limited |
| **Multi-Cloud** | Yes | AWS only | Yes |
| **State Storage** | Pulumi Cloud or S3 | AWS-managed | S3 + DynamoDB |
| **Learning Curve** | Easy if you know Python | Medium | Medium |

## Installation

### macOS
```bash
brew install pulumi
pulumi version
```

### Linux
```bash
curl -fsSL https://get.pulumi.com | sh
pulumi version
```

### Windows
```powershell
choco install pulumi
pulumi version
```

## Project Structure

```
Chart_Agent/
└── infrastructure/
    ├── __main__.py            # Infrastructure code (Python!)
    ├── Pulumi.yaml            # Project definition
    ├── Pulumi.dev.yaml        # Dev configuration
    ├── Pulumi.testing.yaml    # Testing configuration
    ├── requirements.txt       # Python dependencies
    ├── venv/                  # Python virtual environment
    └── .gitignore            # Ignore state files
```

## Understanding the Code

### __main__.py Structure

```python
import pulumi
import pulumi_aws as aws

# Configuration (from Pulumi.{stack}.yaml)
config = pulumi.Config()
environment = config.get("environment") or "dev"

# Create resources using Python
vpc = aws.ec2.Vpc(
    "my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
)

# Conditional logic (real Python!)
if environment == "production":
    # Create NAT Gateway only in production
    nat_gateway = aws.ec2.NatGateway(...)

# Loops (real Python!)
for i in range(2):
    subnet = aws.ec2.Subnet(f"subnet-{i}", ...)

# Export values
pulumi.export("vpc_id", vpc.id)
```

### Key Concepts

**1. Resources**: AWS resources defined as Python objects

```python
vpc = aws.ec2.Vpc(
    "my-vpc",              # Logical name (must be unique)
    cidr_block="10.0.0.0/16",  # Properties
    tags={"Name": "my-vpc"},
)
```

**2. Outputs**: Values available after deployment

```python
pulumi.export("vpc_id", vpc.id)

# Access after deployment:
# pulumi stack output vpc_id
```

**3. Configuration**: Values from Pulumi.{stack}.yaml

```python
config = pulumi.Config()
enable_nat = config.get_bool("enableNATGateway")

if enable_nat:
    nat = aws.ec2.NatGateway(...)
```

**4. Dependencies**: Pulumi tracks automatically

```python
# Internet Gateway depends on VPC
igw = aws.ec2.InternetGateway(
    "igw",
    vpc_id=vpc.id,  # Pulumi knows: create VPC first!
)
```

## Basic Commands

### Initial Setup

```bash
# Navigate to infrastructure folder
cd infrastructure

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Login to Pulumi

```bash
# Option 1: Pulumi Cloud (free, recommended)
pulumi login

# Option 2: Local storage
pulumi login --local

# Option 3: AWS S3
pulumi login s3://my-pulumi-state-bucket
```

### Stack Management

```bash
# List stacks
pulumi stack ls

# Create new stack
pulumi stack init dev

# Select existing stack
pulumi stack select dev

# View current stack
pulumi stack

# Delete stack
pulumi stack rm dev
```

### Deploy Infrastructure

```bash
# Preview changes (like 'plan')
pulumi preview

# Deploy changes
pulumi up

# Deploy without confirmation
pulumi up --yes

# Deploy specific resources
pulumi up --target urn:pulumi:dev::chart-agent::aws:ec2/vpc:Vpc::my-vpc
```

### View State

```bash
# List all resources
pulumi stack --show-urns

# View outputs
pulumi stack output

# View specific output
pulumi stack output vpc_id

# Export all outputs as JSON
pulumi stack output --json
```

### Destroy Infrastructure

```bash
# Preview destruction
pulumi destroy --preview

# Destroy all resources
pulumi destroy

# Destroy without confirmation
pulumi destroy --yes
```

### Update Stack Configuration

```bash
# Set configuration value
pulumi config set aws:region us-east-1
pulumi config set chart-agent:environment dev
pulumi config set chart-agent:enableNATGateway false

# Set secret (encrypted)
pulumi config set --secret apiKey mySecretValue

# View configuration
pulumi config

# Get specific value
pulumi config get chart-agent:environment
```

## Using Helper Scripts

### Setup

```bash
./scripts/setup-pulumi.sh
```

Interactive setup that:
- Installs Python dependencies
- Configures Pulumi login
- Creates virtual environment

### Development Environment (~$5/month)

```bash
./scripts/start-dev.sh
```

Creates minimal infrastructure:
- VPC and subnets
- Security groups
- IAM roles
- ECR repositories

No expensive resources (NAT Gateway, ALB, running ECS tasks).

### Testing Environment (~$50-70/month)

```bash
./scripts/start-testing.sh
```

Creates full infrastructure:
- Everything from dev
- NAT Gateway ($32/month)
- Application Load Balancer ($18/month)
- ECS tasks configured (charged per hour running)

### Teardown

```bash
./scripts/teardown.sh
```

Interactive script to destroy:
- Dev stack
- Testing stack
- Both

## Advanced Features

### 1. Using Python Functions

```python
def create_subnet(name: str, cidr: str, az_index: int):
    return aws.ec2.Subnet(
        name,
        vpc_id=vpc.id,
        cidr_block=cidr,
        availability_zone=azs[az_index],
        tags={"Name": name},
    )

# Use the function
public_subnet_1 = create_subnet("public-1", "10.0.1.0/24", 0)
public_subnet_2 = create_subnet("public-2", "10.0.2.0/24", 1)
```

### 2. Using Python Classes

```python
class NetworkStack:
    def __init__(self, name: str, cidr: str):
        self.vpc = aws.ec2.Vpc(f"{name}-vpc", cidr_block=cidr)
        self.igw = aws.ec2.InternetGateway(
            f"{name}-igw",
            vpc_id=self.vpc.id,
        )
    
    def create_subnet(self, name: str, cidr: str):
        return aws.ec2.Subnet(
            name,
            vpc_id=self.vpc.id,
            cidr_block=cidr,
        )

# Use the class
network = NetworkStack("dev", "10.0.0.0/16")
subnet = network.create_subnet("public", "10.0.1.0/24")
```

### 3. Using apply() for Outputs

When you need to use resource outputs in calculations:

```python
# WRONG - won't work:
# cidr = f"{vpc.cidr_block}/24"  # vpc.cidr_block is an Output, not a string

# RIGHT - use apply():
subnet_cidr = vpc.cidr_block.apply(lambda cidr: f"{cidr}/24")
```

### 4. Component Resources

Group related resources:

```python
from pulumi import ComponentResource, ResourceOptions

class NetworkInfrastructure(ComponentResource):
    def __init__(self, name: str, opts=None):
        super().__init__("custom:NetworkInfrastructure", name, None, opts)
        
        self.vpc = aws.ec2.Vpc(
            f"{name}-vpc",
            cidr_block="10.0.0.0/16",
            opts=ResourceOptions(parent=self),
        )
        
        self.igw = aws.ec2.InternetGateway(
            f"{name}-igw",
            vpc_id=self.vpc.id,
            opts=ResourceOptions(parent=self),
        )
        
        self.register_outputs({
            "vpc_id": self.vpc.id,
        })

# Use it
network = NetworkInfrastructure("dev")
```

### 5. Stack References

Reference outputs from other stacks:

```python
# In networking stack
pulumi.export("vpc_id", vpc.id)

# In app stack
import pulumi

network_stack = pulumi.StackReference("organization/chart-agent-network/dev")
vpc_id = network_stack.get_output("vpc_id")

# Use vpc_id in this stack
ec2_instance = aws.ec2.Instance(
    "my-instance",
    vpc_id=vpc_id,
    ...
)
```

## Testing Infrastructure Code

### Unit Testing

Create `__main___test.py`:

```python
import unittest
import pulumi

class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + '_id', args.inputs]
    
    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}

pulumi.runtime.set_mocks(MyMocks())

# Now import and test your infrastructure
import __main__ as infra

class TestInfrastructure(unittest.TestCase):
    @pulumi.runtime.test
    def test_vpc_created(self):
        def check_vpc(args):
            vpc_id = args[0]
            self.assertIsNotNone(vpc_id)
        
        return infra.vpc.id.apply(lambda args: check_vpc(args))
```

Run tests:
```bash
python -m pytest __main___test.py
```

## Troubleshooting

### "No stacks found"

**Problem**: `pulumi up` says no stacks exist

**Solution**:
```bash
pulumi stack init dev
pulumi up
```

### "Conflict: Another update is in progress"

**Problem**: Previous update didn't complete

**Solution**:
```bash
# Cancel stuck update
pulumi cancel

# Or force unlock (dangerous!)
pulumi stack select dev
pulumi state delete "urn:..."
```

### "ImportError: No module named pulumi"

**Problem**: Python dependencies not installed

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Resource already exists"

**Problem**: Resource exists in AWS but not in Pulumi state

**Solution**:
```bash
# Import existing resource
pulumi import aws:ec2/vpc:Vpc my-vpc vpc-12345678

# Or destroy manually in AWS Console
```

### Permission Denied Errors

**Problem**: AWS IAM permissions insufficient

**Solution**:
- Verify AWS credentials: `aws sts get-caller-identity`
- Check IAM user has AdministratorAccess (for dev) or specific permissions

## Best Practices

### 1. Use Type Hints

```python
from typing import List

def create_subnets(vpc_id: pulumi.Output[str], cidrs: List[str]):
    return [
        aws.ec2.Subnet(f"subnet-{i}", vpc_id=vpc_id, cidr_block=cidr)
        for i, cidr in enumerate(cidrs)
    ]
```

### 2. Use Configuration Files

Don't hardcode values:

```python
# BAD
enable_nat = True

# GOOD
config = pulumi.Config()
enable_nat = config.get_bool("enableNATGateway")
```

### 3. Tag Everything

```python
common_tags = {
    "Project": "ChartAgent",
    "Environment": environment,
    "ManagedBy": "Pulumi",
}

vpc = aws.ec2.Vpc(
    "my-vpc",
    cidr_block="10.0.0.0/16",
    tags={**common_tags, "Name": "my-vpc"},
)
```

### 4. Use Resource Options

```python
vpc = aws.ec2.Vpc(
    "my-vpc",
    cidr_block="10.0.0.0/16",
    opts=pulumi.ResourceOptions(
        protect=True,  # Prevent accidental deletion
        ignore_changes=["tags"],  # Ignore tag changes
    ),
)
```

### 5. Document Your Code

```python
def create_security_group(name: str, vpc_id: pulumi.Output[str]) -> aws.ec2.SecurityGroup:
    """
    Create a security group for ECS tasks.
    
    Args:
        name: Logical name for the security group
        vpc_id: The VPC ID to create the security group in
    
    Returns:
        The created security group resource
    """
    return aws.ec2.SecurityGroup(...)
```

## Cost Optimization

### Development Strategy

Use dev configuration (Pulumi.dev.yaml):
```yaml
config:
  chart-agent:enableNATGateway: false  # Save $32/month
  chart-agent:enableALB: false          # Save $18/month
  chart-agent:ecsBackendCount: 0        # No running tasks
```

**Cost**: ~$5/month (just VPC, security groups, IAM roles)

### Testing Strategy

Use testing configuration (Pulumi.testing.yaml):
```yaml
config:
  chart-agent:enableNATGateway: true
  chart-agent:enableALB: true
  chart-agent:ecsBackendCount: 1
```

**Cost**: ~$50-70/month

**Best Practice**: Deploy testing only when needed, destroy when done.

## Resources

- [Pulumi Docs](https://www.pulumi.com/docs/)
- [Pulumi Python Guide](https://www.pulumi.com/docs/languages-sdks/python/)
- [Pulumi AWS](https://www.pulumi.com/registry/packages/aws/)
- [Pulumi Examples](https://github.com/pulumi/examples)
- [Pulumi Community Slack](https://slack.pulumi.com/)

## Next Steps

1. Explore `infrastructure/__main__.py` - see real Python code!
2. Try modifying the code (add a new subnet, change CIDR blocks)
3. Run `pulumi preview` to see what would change
4. Deploy with `pulumi up`
5. Experiment with Python features (functions, loops, conditionals)

**Welcome to Infrastructure as REAL CODE!** 🐍🚀

