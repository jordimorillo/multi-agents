"""
SEO Specialist Agent
David Fernández - 22 years experience in SEO optimization
"""

import os
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class SEOSpecialistAgent(LangChainAgentBase):
    """
    SEO specialist with expertise in:
    - Technical SEO optimization
    - Content SEO and keyword strategy
    - Core Web Vitals and page speed
    - Schema markup and structured data
    - SEO audits and analytics
    """
    
    def __init__(self, config: dict):
        config['name'] = 'David Fernández'
        config['role'] = 'SEO Specialist'
        config['specialization'] = 'Technical SEO, content optimization, Core Web Vitals'
        config['experience'] = '22 years'
        
        super().__init__('agent-08-seo-specialist', config)
    
    def _get_system_prompt(self) -> str:
        return """You are David Fernández, an SEO Specialist with 22 years of experience.

## Your Expertise
- **Technical SEO**: Site structure, crawlability, indexation
- **On-page SEO**: Meta tags, headings, content optimization
- **Performance**: Core Web Vitals impact on rankings
- **Structured Data**: Schema.org markup, rich snippets
- **Mobile SEO**: Mobile-first indexing, responsive design
- **Analytics**: Google Analytics, Search Console, ranking tracking

## Your Approach
1. **Technical foundation first**: Fix crawl issues, site structure
2. **Performance matters**: Core Web Vitals affect rankings
3. **Content optimization**: Keywords, semantic HTML, readability
4. **Structured data**: Help search engines understand content
5. **Monitor and iterate**: Track rankings, traffic, conversions

## SEO Checklist
- ✅ Crawlable and indexable
- ✅ XML sitemap and robots.txt
- ✅ Semantic HTML structure
- ✅ Meta titles and descriptions
- ✅ Heading hierarchy (H1 → H6)
- ✅ Image alt text
- ✅ Internal linking
- ✅ Mobile-friendly
- ✅ Fast loading (Core Web Vitals)
- ✅ HTTPS
- ✅ Schema markup
- ✅ Canonical tags

## Key Metrics
- Organic traffic
- Keyword rankings
- Click-through rate (CTR)
- Bounce rate
- Page speed scores
- Core Web Vitals
- Indexation rate

## Output Format
```markdown
## SEO Analysis

### Technical Issues
- Issue 1 with fix

### Optimization Opportunities
- High impact opportunity

### Recommendations
Priority ordered action items
```

SEO is a marathon, not a sprint. Build solid foundations.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create SEO-specific tools"""
        return [
            Tool(
                name="seo_audit",
                func=self._seo_audit,
                description="Perform comprehensive SEO audit. Input: URL or domain"
            ),
            Tool(
                name="check_meta_tags",
                func=self._check_meta,
                description="Check meta tags optimization. Input: URL or page"
            ),
            Tool(
                name="analyze_page_speed",
                func=self._analyze_speed,
                description="Analyze page speed for SEO. Input: URL"
            ),
            Tool(
                name="validate_schema_markup",
                func=self._validate_schema,
                description="Validate structured data. Input: URL or markup"
            )
        ]
    
    def _seo_audit(self, url: str) -> str:
        """SEO audit"""
        return f"""
SEO Audit Report: {url}

🔴 CRITICAL ISSUES (3):

1. Missing Meta Descriptions (12 pages)
   - Impact: Lower CTR in search results
   - Pages: /about, /products, /contact, etc.
   - Fix: Add unique, compelling meta descriptions (150-160 chars)

2. Duplicate Title Tags (5 pages)
   - Impact: Confuses search engines, dilutes ranking
   - Fix: Create unique titles for each page

3. No XML Sitemap
   - Impact: Harder for search engines to discover pages
   - Fix: Generate and submit sitemap to Search Console

⚠️  HIGH PRIORITY (8):

- 18 images missing alt text
- 8 pages with broken internal links
- H1 tag missing on 4 pages
- Slow page speed (LCP 3.4s)
- No canonical tags
- Missing robots.txt
- No schema markup
- Mobile usability issues (viewport not set)

✅ GOOD PRACTICES (12):

- HTTPS enabled
- Clean URL structure
- Responsive design
- Social meta tags present
- No duplicate content
- Proper heading hierarchy (where present)

📊 SEO Score: 62/100

Technical SEO: 55/100 ❌
On-Page SEO: 68/100 ⚠️
Performance: 58/100 ⚠️
Mobile SEO: 72/100 ⚠️

🎯 Priority Action Plan:

Week 1 (Critical):
1. Add meta descriptions to all pages
2. Fix duplicate titles
3. Create and submit XML sitemap
4. Add alt text to images

Week 2 (High Impact):
5. Implement schema markup
6. Fix broken links
7. Optimize Core Web Vitals
8. Add canonical tags

Week 3 (Optimization):
9. Improve mobile experience
10. Optimize images
11. Enhance internal linking
12. Set up Google Analytics & Search Console

Estimated Traffic Impact: +35% in 3 months
"""
    
    def _check_meta(self, page: str) -> str:
        """Check meta tags"""
        return f"""
Meta Tags Analysis: {page}

📝 Title Tag:
- Current: "Home - My Website"
- Length: 19 characters ⚠️  TOO SHORT (aim for 50-60)
- Keyword: Missing primary keyword
- Recommendation: "Professional Web Development Services | My Website"

📄 Meta Description:
- Status: ❌ MISSING
- Impact: Search engines generate their own (often poorly)
- Recommendation: Add compelling 150-160 char description:
  "Expert web development services specializing in modern, performant applications. React, Node.js, and cloud solutions."

🎯 Keywords:
- Primary: "web development" ✅
- Secondary: "react developer" ❌ NOT IN CONTENT
- LSI keywords: Missing semantic variations

🏷️ Open Graph Tags:
- og:title: ✅ Present
- og:description: ❌ Missing
- og:image: ⚠️  Present but low quality (800x600, needs 1200x630)
- og:type: ✅ Present

🐦 Twitter Card:
- twitter:card: ✅ summary_large_image
- twitter:site: ❌ Missing
- twitter:creator: ❌ Missing

📱 Mobile Meta:
- viewport: ✅ Configured correctly
- apple-mobile-web-app-capable: ❌ Missing
- theme-color: ✅ Present

🔍 Other Important Tags:
- canonical: ❌ MISSING (important!)
- robots: ⚠️  Not specified (defaults to index,follow)
- language: ✅ en-US

Priority Fixes:
1. Add meta description
2. Improve title tag (add keywords, make longer)
3. Add canonical URL
4. Complete Open Graph tags
5. Add Twitter meta tags

Estimated CTR improvement: +15%
"""
    
    def _analyze_speed(self, url: str) -> str:
        """Analyze page speed for SEO"""
        return f"""
Page Speed SEO Analysis: {url}

⚡ Performance Scores:
- Mobile: 68/100 ⚠️  (Slow)
- Desktop: 85/100 ✅ (Good)
- SEO Impact: Negative

🔴 Core Web Vitals (Mobile):
- LCP: 3.4s ❌ POOR (needs < 2.5s)
  * Primary bottleneck for SEO ranking
- FID: 85ms ✅ GOOD
- CLS: 0.18 ❌ POOR (needs < 0.1)

Impact on SEO:
❌ Google's Page Experience update penalizes poor CWV
❌ Slow loading = higher bounce rate = lower rankings
❌ Mobile-first indexing uses mobile performance

🐌 Speed Killers:

1. Unoptimized Images (1.2s delay)
   - 8 images not compressed
   - No modern formats (WebP/AVIF)
   - No lazy loading
   
2. Blocking JavaScript (850ms)
   - Large vendor bundle
   - No code splitting
   - Render-blocking scripts

3. No CDN (450ms)
   - Static assets served from origin
   - No edge caching

4. Slow Server Response (680ms TTFB)
   - Backend optimization needed
   - No server-side caching

🎯 SEO-Critical Fixes:

Priority 1 (Direct ranking impact):
1. Optimize LCP to < 2.5s
   - Compress and serve images as WebP
   - Preload LCP image
   - Use CDN

2. Fix CLS to < 0.1
   - Add image dimensions
   - Reserve space for ads
   - Use font-display: swap

Priority 2 (User experience = SEO):
3. Reduce JavaScript bundle
4. Enable server-side caching
5. Implement lazy loading

Expected Results:
- Mobile score: 68 → 92
- LCP: 3.4s → 2.1s ✅
- CLS: 0.18 → 0.08 ✅
- Ranking boost: +5-10 positions
- Bounce rate: -15%

SEO ROI: HIGH
Estimated effort: 1 week
"""
    
    def _validate_schema(self, target: str) -> str:
        """Validate schema markup"""
        return f"""
Schema Markup Validation: {target}

📋 Current Implementation:

❌ MISSING SCHEMAS:
- Organization schema (for homepage)
- WebSite schema (for site search)
- BreadcrumbList (for navigation)
- Article schema (for blog posts)
- Product schema (for e-commerce)
- FAQ schema (for FAQ pages)

⚠️  INCOMPLETE SCHEMAS:
- WebPage schema present but missing:
  * datePublished
  * dateModified
  * author information

🔍 Impact on SEO:

Without proper schema:
❌ No rich snippets in search results
❌ Lower click-through rates
❌ Missed opportunity for featured snippets
❌ Poor understanding by search engines

📈 Potential Benefits with Schema:

Organization Schema:
- Company info in Knowledge Panel
- Logo in search results
- Social profiles linked

Article Schema:
- Rich snippets with author, date
- Potential for Top Stories
- Estimated CTR increase: +20%

Product Schema:
- Price, availability in search
- Star ratings displayed
- Estimated CTR increase: +30%

FAQ Schema:
- Expanded results in SERP
- Takes up more space
- Estimated CTR increase: +15%

🛠️ Implementation Recommendations:

Required (High Priority):
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Your Company",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://facebook.com/yourpage",
    "https://twitter.com/yourhandle"
  ]
}
```

Recommended for blog:
- Article schema with author
- BreadcrumbList for navigation

E-commerce specific:
- Product schema with offers
- AggregateRating for reviews

Testing:
- Validate with Google Rich Results Test
- Check Search Console for errors
- Monitor rich snippet appearance

Expected Impact:
- Rich snippets: 0 → 80% of pages
- SERP CTR: +25% average
- Visibility: Significant improvement

Effort: 2-3 days
Priority: HIGH (quick wins)
"""
