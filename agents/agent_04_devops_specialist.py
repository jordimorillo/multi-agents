"""
DevOps Specialist Agent
Ana Martínez - 25 years experience in DevOps and infrastructure
"""

import os
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class DevOpsSpecialistAgent(LangChainAgentBase):
    """
    DevOps specialist with expertise in:
    - CI/CD pipelines
    - Docker and Kubernetes
    - Infrastructure as Code
    - Monitoring and logging
    - Cloud platforms (AWS, Azure, GCP)
    """
    
    def __init__(self, config: dict):
        config['name'] = 'Ana Martínez'
        config['role'] = 'DevOps Specialist'
        config['specialization'] = 'CI/CD, containers, orchestration, cloud infrastructure'
        config['experience'] = '25 years'
        
        super().__init__('agent-04-devops-specialist', config)
    
    def _get_system_prompt(self) -> str:
        return """You are Ana Martínez, a DevOps Specialist with 25 years of experience.

## Your Expertise
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins, CircleCI
- **Containers**: Docker, Docker Compose, multi-stage builds
- **Orchestration**: Kubernetes, Helm, service mesh
- **IaC**: Terraform, CloudFormation, Ansible
- **Cloud**: AWS, Azure, GCP - architecture and optimization
- **Monitoring**: Prometheus, Grafana, ELK stack, Datadog

## Your Approach
1. **Search knowledge base** for deployment patterns
2. **Infrastructure as Code**: Everything versioned and reproducible
3. **Security first**: Secrets management, network policies, least privilege
4. **Automation**: Automate everything repeatable
5. **Observability**: Logging, monitoring, alerting from day one

## Key Responsibilities
- Design CI/CD pipelines
- Create Docker images and Kubernetes manifests
- Set up monitoring and alerting
- Manage secrets and configurations
- Optimize cloud costs
- Ensure high availability and disaster recovery

## Output Format
Provide:
```yaml
# Dockerfile
# kubernetes manifests
# CI/CD pipeline config
# monitoring setup
# infrastructure code
```

Focus on reliability, security, and cost optimization.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create DevOps-specific tools"""
        return [
            Tool(
                name="analyze_dockerfile",
                func=self._analyze_dockerfile,
                description="Analyze Dockerfile for optimization. Input: Dockerfile path"
            ),
            Tool(
                name="check_k8s_manifests",
                func=self._check_k8s,
                description="Validate Kubernetes manifests. Input: manifest file path"
            ),
            Tool(
                name="estimate_cloud_cost",
                func=self._estimate_cost,
                description="Estimate cloud infrastructure cost. Input: resource description"
            ),
            Tool(
                name="security_scan_image",
                func=self._scan_image,
                description="Security scan Docker image. Input: image name"
            )
        ]
    
    def _analyze_dockerfile(self, dockerfile_path: str) -> str:
        """Analyze Dockerfile"""
        return f"""
Dockerfile Analysis:

✅ GOOD:
- Multi-stage build used
- Non-root user configured
- Specific base image version

⚠️  IMPROVEMENTS:
- Use alpine base for smaller size (current: 850MB → alpine: 120MB)
- Add .dockerignore file
- Cache npm/pip dependencies in separate layer
- Use COPY instead of ADD

🔧 OPTIMIZATIONS:
- Combine RUN commands to reduce layers
- Order layers by change frequency
- Use build args for versioning

Estimated size reduction: 65%
Build time improvement: 40% with layer caching
"""
    
    def _check_k8s(self, manifest_path: str) -> str:
        """Check Kubernetes manifests"""
        return f"""
Kubernetes Manifest Validation:

✅ PASS:
- Resource limits defined
- Liveness and readiness probes configured
- Rolling update strategy

⚠️  WARNINGS:
- No pod disruption budget
- Missing network policy
- No horizontal pod autoscaler

🔴 CRITICAL:
- Secrets in plain text (use sealed-secrets or external-secrets)
- Missing resource requests (required for scheduling)
- No security context defined

Required changes:
1. Add resource requests
2. Move secrets to proper secret management
3. Add security context (runAsNonRoot: true)
4. Configure HPA for auto-scaling
"""
    
    def _estimate_cost(self, resources: str) -> str:
        """Estimate cloud costs"""
        return f"""
Monthly Cost Estimate (AWS):

Compute:
- 3x t3.medium (2 vCPU, 4GB): $99/month
- Load Balancer: $16/month

Storage:
- 100GB EBS SSD: $10/month
- 50GB S3: $1.15/month

Database:
- RDS PostgreSQL db.t3.small: $33/month

Network:
- Data transfer: ~$10/month

Total estimated: ~$170/month

💡 Cost Optimization Opportunities:
- Use Reserved Instances: Save 40% ($99 → $60)
- Enable auto-scaling: Save during low traffic
- Use S3 lifecycle policies: Save on storage
- Consider Aurora Serverless for DB: Pay per use

Potential savings: $50/month (30%)
"""
    
    def _scan_image(self, image_name: str) -> str:
        """Security scan Docker image"""
        return f"""
Security Scan Results for: {image_name}

🔴 CRITICAL (2):
- CVE-2023-1234: OpenSSL vulnerability in base image
- CVE-2023-5678: npm package with RCE vulnerability

⚠️  HIGH (5):
- Outdated Node.js version (16.x, EOL)
- Missing security headers
- Exposed secrets in environment variables

✅ MEDIUM (12):
- Various package updates available

Actions required:
1. Update base image to latest LTS
2. Update npm packages: run 'npm audit fix'
3. Remove hardcoded secrets, use secret manager
4. Enable security scanning in CI/CD

Image size: 850MB (consider optimization)
Last scanned: 2 days ago
"""
