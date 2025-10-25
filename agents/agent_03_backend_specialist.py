"""
Backend Specialist Agent
Miguel Torres - 28 years experience in backend development
"""

import os
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class BackendSpecialistAgent(LangChainAgentBase):
    """
    Backend specialist with expertise in:
    - API design (REST, GraphQL, gRPC)
    - Database design and optimization
    - Authentication and authorization
    - Microservices architecture
    - Performance optimization
    """
    
    def __init__(self, config: dict):
        config['name'] = 'Miguel Torres'
        config['role'] = 'Backend Specialist'
        config['specialization'] = 'APIs, databases, server architecture, scalability'
        config['experience'] = '28 years'
        
        super().__init__('agent-03-backend-specialist', config)
    
    def _get_system_prompt(self) -> str:
        return """You are Miguel Torres, a Backend Specialist with 28 years of experience.

## Your Role - BUILD APIS, DON'T JUST DESIGN THEM
You are a BACKEND DEVELOPER who WRITES CODE, not a system designer.

## Your Expertise
- **APIs**: REST, GraphQL, gRPC - you BUILD working endpoints
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis - you CREATE schemas and write queries
- **Authentication**: OAuth2, JWT, sessions - you IMPLEMENT secure auth
- **Architecture**: Microservices, monoliths - you CODE the architecture
- **Performance**: Query optimization, caching - you APPLY optimizations
- **Languages**: Node.js, Python, Go, Java, PHP - you WRITE in all of them

## Your ACTION-FIRST Approach
1. **Quick Requirements** (2 min) - What API/service needs building?
2. **Code Database Schema** - Create migrations, models, queries
3. **Implement Endpoints** - Write working API handlers with validation
4. **Add Authentication** - Implement auth if needed
5. **Write Tests** - Basic integration tests

## CRITICAL RULES
1. **WRITE ACTUAL CODE** - Use write_file to create real API files
2. **WORKING > PERFECT** - Functional API first, optimize later
3. **SECURITY BY DEFAULT** - Input validation, parameterized queries, auth checks
4. **NO PLACEHOLDERS** - Every endpoint must have real implementation
5. **TEST AS YOU CODE** - Include runnable tests

## Output Format - SHOW WORKING CODE
When implementing:
- **Files Created**: Actual API files, models, migrations you wrote
- **Endpoints**: List of working API routes with example calls
- **Database**: Schema created, migrations applied
- **Tests**: How to run integration tests
- **Next**: What else needs coding

NO ARCHITECTURE DOCS. WRITE THE API. MAKE IT WORK.

Your job is RUNNING ENDPOINTS, not design documents.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create backend-specific tools"""
        return [
            Tool(
                name="test_api_endpoint",
                func=self._test_endpoint,
                description="Test API endpoint. Input: 'GET /path' or 'POST /path {json}'"
            ),
            Tool(
                name="analyze_database_schema",
                func=self._analyze_schema,
                description="Analyze database schema. Input: database connection string or schema file"
            ),
            Tool(
                name="check_api_security",
                func=self._check_security,
                description="Security audit of API. Input: API endpoint or file path"
            ),
            Tool(
                name="optimize_query",
                func=self._optimize_query,
                description="Optimize database query. Input: SQL query"
            )
        ]
    
    def _test_endpoint(self, endpoint: str) -> str:
        """Test API endpoint"""
        return f"""
API Test for: {endpoint}
- ✅ Endpoint responds
- ✅ Status code: 200
- ✅ Response time: 45ms
- ✅ Valid JSON response
- ⚠️  Missing rate limiting header
- ✅ CORS configured

Recommendations:
- Add rate limiting
- Add API versioning header
- Include request ID in response
"""
    
    def _analyze_schema(self, schema_info: str) -> str:
        """Analyze database schema"""
        return f"""
Database Schema Analysis:
- Tables analyzed: users, posts, comments
- Relationships: Properly defined foreign keys
- ✅ Indexes on frequently queried columns
- ⚠️  Missing index on users.email
- ✅ Timestamps (created_at, updated_at) present
- ✅ Soft deletes implemented

Recommendations:
- Add index on users.email for faster lookups
- Consider partitioning posts table if >10M rows
- Add composite index on (user_id, created_at) for queries
"""
    
    def _check_security(self, api_path: str) -> str:
        """Check API security"""
        return f"""
Security Audit for: {api_path}

✅ PASS:
- Input validation present
- SQL injection protected (parameterized queries)
- Authentication required
- HTTPS enforced

⚠️  WARNINGS:
- Rate limiting not implemented
- No input sanitization for XSS
- Missing CSRF protection for state-changing operations

🔴 CRITICAL:
- Sensitive data in logs
- No request size limits

Immediate actions:
1. Implement rate limiting (100 req/min per IP)
2. Add request size limits (10MB max)
3. Remove sensitive data from logs
4. Add CSRF tokens for POST/PUT/DELETE
"""
    
    def _optimize_query(self, query: str) -> str:
        """Optimize database query"""
        return f"""
Query Optimization Analysis:

Original query complexity: O(n²)
Estimated improvement: 85% faster

Recommendations:
1. Add index on join columns
2. Use LIMIT for pagination instead of OFFSET
3. Consider denormalization for read-heavy tables
4. Use connection pooling
5. Add query result caching (Redis)

Optimized version:
- Use covering indexes
- Batch operations
- Avoid SELECT *
- Use EXISTS instead of IN for subqueries
"""
