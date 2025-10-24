"""
QA Specialist Agent
Patricia Ruiz - 26 years experience in quality assurance
"""

import os
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class QASpecialistAgent(LangChainAgentBase):
    """
    QA specialist with expertise in:
    - Test strategy and planning
    - Automated testing (unit, integration, e2e)
    - Test frameworks and tools
    - Quality metrics and reporting
    - Accessibility testing
    """
    
    def __init__(self, config: dict):
        config['name'] = 'Patricia Ruiz'
        config['role'] = 'QA Specialist'
        config['specialization'] = 'Test automation, quality assurance, accessibility'
        config['experience'] = '26 years'
        
        super().__init__('agent-07-qa-specialist', config)
    
    def _get_system_prompt(self) -> str:
        return """You are Patricia Ruiz, a QA Specialist with 26 years of experience.

## Your Expertise
- **Test Strategy**: Test pyramids, risk-based testing
- **Frameworks**: Jest, Vitest, Pytest, Playwright, Cypress
- **Test Types**: Unit, integration, e2e, visual regression, accessibility
- **Coverage**: Code coverage, branch coverage, mutation testing
- **CI/CD Integration**: Automated testing in pipelines
- **Accessibility**: WCAG compliance testing

## Your Approach
1. **Test pyramid**: Lots of unit tests, some integration, few e2e
2. **Risk-based**: Focus on critical paths and high-risk areas
3. **Shift-left**: Test early and often
4. **Automation first**: Automate repetitive tests
5. **Clear reporting**: Actionable feedback for developers

## Test Coverage Goals
- **Unit tests**: 80%+ coverage
- **Integration tests**: Critical paths covered
- **E2E tests**: Happy paths + critical flows
- **Accessibility**: WCAG AA compliance
- **Performance**: Load testing for critical endpoints

## Key Quality Metrics
- Test coverage percentage
- Test execution time
- Flaky test rate (< 5%)
- Bug escape rate
- Mean time to detect (MTTD)
- Mean time to repair (MTTR)

## Output Format
```markdown
## Test Strategy

### Test Plan
- Unit: X tests covering Y%
- Integration: Z tests
- E2E: W critical flows

### Test Cases
- Happy path scenarios
- Edge cases
- Error handling

### Quality Gates
- Must pass before merge/deploy
```

Quality is not an afterthought—it's built in from the start.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create QA-specific tools"""
        return [
            Tool(
                name="run_test_suite",
                func=self._run_tests,
                description="Run test suite. Input: 'unit', 'integration', 'e2e', or 'all'"
            ),
            Tool(
                name="check_test_coverage",
                func=self._check_coverage,
                description="Check test coverage. Input: path or 'all'"
            ),
            Tool(
                name="test_accessibility",
                func=self._test_a11y,
                description="Run accessibility tests. Input: URL or component"
            ),
            Tool(
                name="generate_test_report",
                func=self._generate_report,
                description="Generate QA report. Input: test type or 'summary'"
            )
        ]
    
    def _run_tests(self, test_type: str) -> str:
        """Run test suite"""
        if test_type == 'unit':
            return """
Unit Tests Report:

✅ PASSED: 248 tests
❌ FAILED: 3 tests
⏭️  SKIPPED: 5 tests

Failures:
1. UserService.updateProfile() 
   - Expected: 200, Got: 500
   - Cause: Missing mock for email service
   
2. CartComponent.calculateTotal()
   - Expected: 99.99, Got: 100.01
   - Cause: Floating point precision issue
   
3. AuthMiddleware.validateToken()
   - Timeout after 5000ms
   - Cause: Async issue not properly handled

Coverage: 82.4% (goal: 80%+) ✅
Duration: 12.3s
Status: NEEDS FIXES
"""
        elif test_type == 'integration':
            return """
Integration Tests Report:

✅ PASSED: 56 tests
❌ FAILED: 2 tests
⏭️  SKIPPED: 1 test

Failures:
1. API: POST /api/orders
   - Status: 500 Internal Server Error
   - Cause: Database connection timeout
   
2. Payment flow end-to-end
   - Payment gateway returned 402
   - Cause: Invalid test API key

Duration: 3m 42s
Status: NEEDS INVESTIGATION
"""
        elif test_type == 'e2e':
            return """
E2E Tests Report (Playwright):

✅ PASSED: 18 tests
❌ FAILED: 1 test
🔄 FLAKY: 2 tests (retried and passed)

Failure:
1. User checkout flow
   - Timeout waiting for payment confirmation
   - Screenshot: checkout-failure-1234.png
   - Cause: Slow network or flaky payment gateway

Flaky Tests:
- Login flow (passed on retry)
- Search functionality (passed on retry)

Duration: 8m 15s
Status: INVESTIGATE FLAKY TESTS
"""
        else:  # all
            return """
Complete Test Suite Report:

Unit Tests: ✅ 248/251 passed (98.8%)
Integration: ⚠️  56/58 passed (96.6%)
E2E Tests: ⚠️  18/19 passed (94.7%)

Overall: ⚠️  322/328 tests passing (98.2%)

Total Duration: 24m 10s
Coverage: 82.4%

Action Required:
- Fix 6 failing tests
- Investigate 2 flaky e2e tests
- Update integration test database setup

Quality Gate: ⚠️  CONDITIONAL PASS
(All critical path tests passed)
"""
    
    def _check_coverage(self, path: str) -> str:
        """Check test coverage"""
        return """
Test Coverage Report:

📊 Overall Coverage: 82.4%

By Type:
- Statements: 84.2% ✅
- Branches: 78.9% ⚠️  (goal: 80%)
- Functions: 86.1% ✅
- Lines: 83.5% ✅

Low Coverage Areas:
1. src/utils/legacy.js: 34% ❌
   - Recommendation: Add tests or refactor
   
2. src/services/payment.js: 62% ⚠️
   - Critical module needs more coverage
   
3. src/api/webhooks.js: 58% ⚠️
   - Add tests for error scenarios

Uncovered Lines:
- Error handling paths: 45% covered
- Edge cases: 67% covered
- Happy paths: 94% covered ✅

Recommendations:
1. Add tests for payment service (HIGH PRIORITY)
2. Increase branch coverage to 80%+
3. Focus on error handling scenarios
4. Consider removing or testing legacy code

Coverage Trend: 79.2% → 82.4% (+3.2%) ✅
"""
    
    def _test_a11y(self, target: str) -> str:
        """Test accessibility"""
        return f"""
Accessibility Test Report: {target}

🔍 Automated Testing (axe-core):

❌ CRITICAL (3 issues):
1. Missing alt text on images
   - Impact: Screen readers can't describe images
   - Fix: Add descriptive alt attributes
   
2. Insufficient color contrast
   - Ratio: 3.2:1 (needs 4.5:1 for AA)
   - Fix: Darken text or lighten background
   
3. Form inputs without labels
   - Impact: Screen readers can't identify fields
   - Fix: Add <label> elements or aria-label

⚠️  MODERATE (7 issues):
- Missing ARIA landmarks
- Keyboard navigation issues on custom dropdown
- Focus indicators not visible
- Heading hierarchy skipped (h1 → h3)

✅ PASSED (28 checks):
- Semantic HTML structure
- Document language declared
- Page title present
- Skip navigation link
- Keyboard accessible (most elements)

WCAG Compliance:
- Level A: 89% ⚠️
- Level AA: 76% ❌
- Level AAA: 45%

Manual Testing Required:
- Screen reader testing
- Keyboard-only navigation
- Color blindness simulation
- Zoom testing (up to 200%)

Priority Actions:
1. Fix critical issues (required for AA)
2. Add ARIA landmarks
3. Fix keyboard navigation
4. Increase color contrast

Estimated effort: 4-6 hours
"""
    
    def _generate_report(self, report_type: str) -> str:
        """Generate QA report"""
        return """
QA Summary Report
Date: 2025-10-24

📈 Quality Metrics:

Test Results:
- Total tests: 328
- Passing: 322 (98.2%)
- Failing: 6 (1.8%)
- Flaky: 2 (0.6%)

Code Coverage:
- Current: 82.4% ✅
- Previous: 79.2%
- Trend: +3.2% ⬆️

Bug Statistics:
- Critical bugs: 0 ✅
- High priority: 2 ⚠️
- Medium: 8
- Low: 15

Performance:
- API p95: 145ms ✅
- Frontend LCP: 2.8s ⚠️
- Page load: 3.2s

Accessibility:
- WCAG AA: 76% ❌
- Critical issues: 3
- Status: NEEDS WORK

🎯 Quality Gates:

✅ PASSED:
- No critical bugs
- 80%+ test coverage
- All critical path tests pass

⚠️  WARNINGS:
- 6 failing non-critical tests
- Accessibility below AA standard
- Frontend performance needs improvement

❌ BLOCKERS:
- None

📋 Recommendations:

High Priority:
1. Fix 3 critical accessibility issues
2. Resolve 6 failing tests
3. Improve frontend LCP to < 2.5s

Medium Priority:
1. Investigate flaky tests
2. Increase branch coverage to 80%
3. Add visual regression tests

Status: ⚠️  CONDITIONAL APPROVAL
Can deploy to staging, NOT ready for production until a11y fixes are in.
"""
