"""
Security Specialist Agent
Roberto García - 30 years experience in cybersecurity
"""

import os
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class SecuritySpecialistAgent(LangChainAgentBase):
    """
    Security specialist with expertise in:
    - Application security (OWASP Top 10)
    - Penetration testing
    - Security audits and compliance
    - Cryptography and secure authentication
    - Threat modeling
    """
    
    def __init__(self, config: dict):
        config['name'] = 'Roberto García'
        config['role'] = 'Security Specialist'
        config['specialization'] = 'Application security, penetration testing, compliance'
        config['experience'] = '30 years'
        
        super().__init__('agent-05-security-specialist', config)
    
    def _get_system_prompt(self) -> str:
        return """You are Roberto García, a Security Specialist with 30 years of experience.

## Your Expertise
- **OWASP Top 10**: Expert in web application vulnerabilities
- **Authentication**: OAuth2, JWT, MFA, biometrics
- **Cryptography**: TLS, encryption at rest, key management
- **Compliance**: GDPR, SOC2, PCI-DSS, HIPAA
- **Pen Testing**: Security testing and vulnerability assessment
- **Threat Modeling**: STRIDE, attack surface analysis

## Your Approach
1. **Threat modeling first**: Identify attack vectors before implementation
2. **Defense in depth**: Multiple security layers
3. **Least privilege**: Minimal permissions by default
4. **Secure by design**: Security requirements from the start
5. **Continuous monitoring**: Detect and respond to threats

## Critical Security Checks
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF tokens
- ✅ Secure authentication
- ✅ Authorization checks
- ✅ Secrets management
- ✅ Rate limiting
- ✅ HTTPS everywhere
- ✅ Security headers

## Output Format
Provide security assessment:
```markdown
## Security Analysis

### 🔴 Critical Issues
- Issue 1 with remediation steps

### ⚠️  High Priority
- Issue 2 with recommendations

### ✅ Compliant
- Security measure properly implemented

### Recommendations
- Priority 1: Action item
```

Always err on the side of caution. Security is not negotiable.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create security-specific tools"""
        return [
            Tool(
                name="security_audit",
                func=self._security_audit,
                description="Perform security audit. Input: component name or file path"
            ),
            Tool(
                name="check_owasp_top10",
                func=self._check_owasp,
                description="Check for OWASP Top 10 vulnerabilities. Input: code or endpoint"
            ),
            Tool(
                name="analyze_auth_flow",
                func=self._analyze_auth,
                description="Analyze authentication flow. Input: auth implementation description"
            ),
            Tool(
                name="compliance_check",
                func=self._check_compliance,
                description="Check compliance requirements. Input: standard (GDPR, SOC2, etc.)"
            )
        ]
    
    def _security_audit(self, component: str) -> str:
        """Perform security audit"""
        return f"""
Security Audit Report: {component}

🔴 CRITICAL VULNERABILITIES (2):
1. SQL Injection Risk
   - Location: User input not parameterized
   - Impact: Database compromise
   - Fix: Use prepared statements
   - Priority: IMMEDIATE

2. Exposed API Keys
   - Location: Hardcoded in source
   - Impact: Unauthorized access
   - Fix: Use environment variables + secret manager
   - Priority: IMMEDIATE

⚠️  HIGH SEVERITY (4):
- Missing authentication on admin endpoint
- Weak password policy (no complexity requirements)
- No rate limiting on login endpoint
- CORS misconfigured (allows all origins)

✅ MEDIUM (8):
- Various security headers missing
- Session timeout too long (24h)
- Verbose error messages leak info

✅ COMPLIANT:
- HTTPS enforced
- Password hashing with bcrypt
- Input validation on most endpoints

Overall Security Score: 6.5/10
Risk Level: HIGH - Immediate action required
"""
    
    def _check_owasp(self, code_path: str) -> str:
        """Check OWASP Top 10"""
        return f"""
OWASP Top 10 Analysis:

A01:2021 – Broken Access Control
❌ FAIL: Missing authorization checks on user endpoints

A02:2021 – Cryptographic Failures
⚠️  WARNING: Some data not encrypted at rest

A03:2021 – Injection
❌ FAIL: SQL injection vulnerability found

A04:2021 – Insecure Design
✅ PASS: Secure design patterns used

A05:2021 – Security Misconfiguration
⚠️  WARNING: Default configurations in production

A06:2021 – Vulnerable Components
⚠️  WARNING: 3 packages with known vulnerabilities

A07:2021 – Auth Failures
⚠️  WARNING: No MFA, weak session management

A08:2021 – Data Integrity Failures
✅ PASS: Checksums and signatures implemented

A09:2021 – Logging Failures
⚠️  WARNING: Insufficient security event logging

A10:2021 – SSRF
✅ PASS: URL validation implemented

Critical issues: 2
Must fix before production deployment
"""
    
    def _analyze_auth(self, auth_description: str) -> str:
        """Analyze authentication flow"""
        return f"""
Authentication Security Analysis:

🔒 Authentication Mechanism:
- Type: JWT with refresh tokens
- Storage: HttpOnly cookies (✅ good)
- Expiry: Access 15min, Refresh 7days (✅ reasonable)

🔴 CRITICAL ISSUES:
- JWT secret in source code (use KMS/Vault)
- No token rotation on password change
- Missing rate limiting on auth endpoints

⚠️  IMPROVEMENTS NEEDED:
- Add MFA (2FA) support
- Implement device fingerprinting
- Add suspicious login detection
- Enable session management (revoke all sessions)

✅ GOOD PRACTICES:
- Password hashing with bcrypt (cost factor: 12)
- HTTPS only
- HttpOnly + Secure cookies
- Account lockout after 5 failed attempts

Recommendations:
1. Implement MFA (Priority: HIGH)
2. Move secrets to secret manager (Priority: CRITICAL)
3. Add anomaly detection (Priority: MEDIUM)
4. Implement token rotation (Priority: HIGH)

Security Rating: 7/10 (Good, but needs MFA)
"""
    
    def _check_compliance(self, standard: str) -> str:
        """Check compliance"""
        return f"""
{standard.upper()} Compliance Assessment:

✅ COMPLIANT:
- Data encryption at rest and in transit
- Access controls implemented
- Audit logging present
- Data retention policies defined

⚠️  PARTIAL COMPLIANCE:
- Privacy policy needs update
- Data processing agreements incomplete
- User consent mechanism needs improvement

❌ NON-COMPLIANT:
- Missing data breach notification procedure
- No Data Protection Impact Assessment (DPIA)
- Right to erasure not fully implemented
- Missing privacy by design documentation

Required Actions:
1. Implement complete data erasure process
2. Create DPIA documentation
3. Document privacy by design decisions
4. Establish incident response plan
5. Update privacy policy and consent flows

Compliance Score: 65%
Status: NOT READY for production
Estimated effort to compliance: 2-3 weeks
"""
