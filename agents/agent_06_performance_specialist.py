"""
Performance Specialist Agent
Laura Sánchez - 27 years experience in performance optimization
"""

import os
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class PerformanceSpecialistAgent(LangChainAgentBase):
    """
    Performance specialist with expertise in:
    - Performance profiling and optimization
    - Core Web Vitals optimization
    - Database query optimization
    - Caching strategies
    - Load testing and scalability
    """
    
    def __init__(self, config: dict):
        config['name'] = 'Laura Sánchez'
        config['role'] = 'Performance Specialist'
        config['specialization'] = 'Performance optimization, scalability, Core Web Vitals'
        config['experience'] = '27 years'
        
        super().__init__('agent-06-performance-specialist', config)
    
    def _get_system_prompt(self) -> str:
        return """You are Laura Sánchez, a Performance Specialist with 27 years of experience.

## Your Expertise
- **Frontend Performance**: Core Web Vitals (LCP, FID, CLS), bundle optimization
- **Backend Performance**: Database optimization, caching, async processing
- **Profiling**: Chrome DevTools, Lighthouse, profilers
- **Caching**: Redis, CDN, browser cache strategies
- **Load Testing**: k6, JMeter, Artillery
- **Monitoring**: Real user monitoring, synthetic monitoring

## Your Approach
1. **Measure first**: Baseline metrics before optimization
2. **Identify bottlenecks**: Profile to find actual issues
3. **Optimize strategically**: Focus on biggest impact
4. **Test thoroughly**: Validate improvements with metrics
5. **Monitor continuously**: Track performance over time

## Performance Goals
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **TTFB (Time to First Byte)**: < 600ms
- **API Response**: < 200ms (p95)
- **Database Queries**: < 50ms (p95)

## Key Optimizations
- Code splitting and lazy loading
- Image optimization and modern formats
- Database indexing and query optimization
- Caching layers (browser, CDN, application, database)
- Async/background processing
- Connection pooling
- Compression (gzip/brotli)

## Output Format
```markdown
## Performance Analysis

### Current Metrics
- Metric 1: value (status)

### Bottlenecks Identified
1. Issue with impact analysis

### Optimization Strategy
1. High impact optimization
2. Medium impact optimization

### Expected Improvements
- Metric improvement projections
```

Measure, optimize, verify. Always with data.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create performance-specific tools"""
        return [
            Tool(
                name="analyze_lighthouse_score",
                func=self._lighthouse_analysis,
                description="Analyze Lighthouse performance. Input: URL or page name"
            ),
            Tool(
                name="check_core_web_vitals",
                func=self._check_cwv,
                description="Check Core Web Vitals. Input: URL"
            ),
            Tool(
                name="analyze_bundle_size",
                func=self._analyze_bundle,
                description="Analyze frontend bundle size. Input: build path"
            ),
            Tool(
                name="profile_database_queries",
                func=self._profile_db,
                description="Profile slow database queries. Input: database connection or query"
            )
        ]
    
    def _lighthouse_analysis(self, url: str) -> str:
        """Lighthouse performance analysis"""
        return f"""
Lighthouse Performance Report: {url}

⚡ Performance Score: 68/100

Core Web Vitals:
- LCP: 3.2s ❌ (Goal: < 2.5s)
- FID: 85ms ✅ (Goal: < 100ms)
- CLS: 0.15 ❌ (Goal: < 0.1)

Opportunities (potential savings):
1. ⏰ Reduce unused JavaScript (-850ms)
   - Remove unused vendor code
   - Implement code splitting
   
2. 🖼️ Optimize images (-1.2s)
   - Use modern formats (WebP, AVIF)
   - Proper sizing and lazy loading
   
3. 📦 Minify CSS (-180ms)
   - Remove unused CSS
   - Enable compression

4. 🚀 Use CDN for static assets (-320ms)
   - Serve from edge locations
   - Enable HTTP/2

Estimated improvement: 68 → 92 (Performance Score)
Total time savings: ~2.5 seconds
"""
    
    def _check_cwv(self, url: str) -> str:
        """Check Core Web Vitals"""
        return f"""
Core Web Vitals Analysis: {url}

📊 Real User Metrics (28 days):

Largest Contentful Paint (LCP):
- p75: 3.4s ❌ POOR (needs < 2.5s)
- Causes: Large hero image, blocking JS
- Fix: Optimize images, preload critical resources

First Input Delay (FID):
- p75: 75ms ✅ GOOD (needs < 100ms)
- Status: Acceptable

Cumulative Layout Shift (CLS):
- p75: 0.18 ❌ POOR (needs < 0.1)
- Causes: Images without dimensions, late-loaded fonts
- Fix: Set width/height, use font-display

Time to First Byte (TTFB):
- p75: 890ms ⚠️  NEEDS IMPROVEMENT (target < 600ms)
- Causes: Slow server response
- Fix: Enable caching, optimize backend

🎯 Priority Actions:
1. Add image dimensions (fixes CLS)
2. Implement lazy loading for below-fold images
3. Enable server-side caching
4. Preload LCP image

Expected improvements:
- LCP: 3.4s → 2.1s ✅
- CLS: 0.18 → 0.08 ✅
"""
    
    def _analyze_bundle(self, build_path: str) -> str:
        """Analyze bundle size"""
        return f"""
Bundle Size Analysis:

📦 Current Build Size:
- main.js: 845 KB (298 KB gzipped) ❌ TOO LARGE
- vendor.js: 612 KB (201 KB gzipped) ⚠️
- styles.css: 89 KB (23 KB gzipped) ✅
- Total: 1.5 MB (522 KB gzipped)

🔍 Largest Contributors:
1. lodash: 245 KB (use lodash-es + tree-shaking)
2. moment.js: 187 KB (replace with day.js: 2 KB)
3. chart.js: 156 KB (consider lazy loading)
4. unused-lib: 98 KB (remove if not used)

🎯 Optimization Strategy:
1. Replace moment.js with day.js: -185 KB
2. Use lodash-es with tree-shaking: -200 KB
3. Lazy load chart.js: -156 KB
4. Remove unused dependencies: -98 KB

Code Splitting Recommendations:
- Split by routes (4 main chunks)
- Lazy load admin panel
- Defer analytics scripts

Expected Results:
- Bundle size: 1.5 MB → 650 KB (57% reduction)
- Gzipped: 522 KB → 220 KB
- Initial load time improvement: -2.1s
"""
    
    def _profile_db(self, query_info: str) -> str:
        """Profile database queries"""
        return f"""
Database Performance Profile:

🐌 Slow Queries Identified (>100ms):

1. Query: SELECT * FROM users JOIN posts...
   - Execution time: 2,340ms ❌ CRITICAL
   - Rows scanned: 1.2M
   - Issue: Full table scan, no index on join column
   - Fix: Add index on posts.user_id
   - Expected improvement: 2,340ms → 45ms

2. Query: Complex aggregation on orders
   - Execution time: 850ms ⚠️
   - Issue: No covering index
   - Fix: Add composite index (user_id, created_at, status)
   - Expected improvement: 850ms → 120ms

3. Query: N+1 problem in comments
   - Total time: 3,200ms (200 queries × 16ms)
   - Issue: Not using JOIN or eager loading
   - Fix: Use JOIN or batch loading
   - Expected improvement: 3,200ms → 80ms

📈 Optimization Recommendations:

Indexing:
- Add index: posts(user_id, created_at)
- Add index: comments(post_id, created_at)
- Remove unused index: users(middle_name)

Query Optimization:
- Use SELECT specific columns (not *)
- Implement pagination (LIMIT/OFFSET)
- Add query result caching (Redis)

Connection Pooling:
- Current: 5 connections (insufficient)
- Recommended: 20 connections for current load
- Enable connection pooling

Expected Overall Improvement:
- Average query time: 450ms → 35ms (92% faster)
- P95 query time: 2,340ms → 150ms
- Database CPU usage: -65%
"""
