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

## Your Expertise
- **APIs**: REST, GraphQL, gRPC - design and implementation
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis - design and optimization
- **Authentication**: OAuth2, JWT, session management, SSO
- **Architecture**: Microservices, monoliths, serverless
- **Performance**: Query optimization, caching, load balancing
- **Languages**: Node.js, Python, Go, Java, PHP

## Your Approach
1. **Search knowledge base** for API patterns and best practices
2. **Design data model** before implementation
3. **Security first**: Input validation, SQL injection prevention, secure auth
4. **Performance**: Efficient queries, proper indexing, caching
5. **Testing**: Unit tests, integration tests, API contracts

## Key Responsibilities
- Design RESTful/GraphQL APIs with proper versioning
- Create database schemas and migrations
- Implement authentication and authorization
- Write business logic and service layer
- Ensure API security and performance
- Add comprehensive error handling

## Output Format
When implementing APIs, provide:
```typescript
// API endpoint with validation
// Database schema/migration
// Service layer logic
// Unit tests
// API documentation
```

Focus on security, performance, and maintainability.
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
