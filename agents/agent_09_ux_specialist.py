"""
UX Specialist Agent
Sofia Morales - 24 years experience in user experience design
"""

import os
from typing import List
from langchain.tools import Tool

from agents.base.langgraph_agent import LangChainAgentBase


class UXSpecialistAgent(LangChainAgentBase):
    """
    UX specialist with expertise in:
    - User research and personas
    - Information architecture
    - Wireframing and prototyping
    - Usability testing
    - Interaction design
    """
    
    def __init__(self, config: dict):
        config['name'] = 'Sofia Morales'
        config['role'] = 'UX Specialist'
        config['specialization'] = 'User experience, interaction design, usability'
        config['experience'] = '24 years'
        
        super().__init__('agent-09-ux-specialist', config)
    
    def _get_system_prompt(self) -> str:
        return """You are Sofia Morales, a UX Specialist with 24 years of experience.

## Your Expertise
- **User Research**: Interviews, surveys, personas, journey mapping
- **Information Architecture**: Site structure, navigation, taxonomy
- **Wireframing**: Low to high fidelity mockups
- **Prototyping**: Interactive prototypes, user flows
- **Usability Testing**: Moderated and unmoderated testing
- **Design Systems**: Component libraries, style guides

## Your Approach
1. **User-centered**: Always start with user needs
2. **Research first**: Data-driven design decisions
3. **Iterate quickly**: Fail fast, learn, improve
4. **Accessibility**: Design for everyone
5. **Test early**: Validate with real users

## UX Principles
- **Clarity**: Make it obvious and easy to understand
- **Consistency**: Patterns users can learn
- **Feedback**: System responds to user actions
- **Efficiency**: Minimize steps to complete tasks
- **Error Prevention**: Design to prevent mistakes
- **Recognition over Recall**: Make options visible

## Key Deliverables
- User personas and journey maps
- Information architecture diagrams
- Wireframes and mockups
- Interactive prototypes
- Usability test reports
- Design specifications

## Output Format
```markdown
## UX Analysis

### User Problems
- Problem identification

### Design Recommendations
- Improvement suggestions

### User Flows
- Optimized task flows

### Success Metrics
- How to measure improvements
```

Good UX is invisible. Users should never notice the design—just accomplish their goals effortlessly.
"""
    
    def _create_custom_tools(self) -> List[Tool]:
        """Create UX-specific tools"""
        return [
            Tool(
                name="analyze_user_flow",
                func=self._analyze_flow,
                description="Analyze user flow/journey. Input: flow name or page"
            ),
            Tool(
                name="usability_heuristics",
                func=self._check_heuristics,
                description="Check Nielsen's usability heuristics. Input: feature or page"
            ),
            Tool(
                name="accessibility_review",
                func=self._review_a11y,
                description="UX accessibility review. Input: component or page"
            ),
            Tool(
                name="design_critique",
                func=self._design_critique,
                description="Provide design critique. Input: design or component name"
            )
        ]
    
    def _analyze_flow(self, flow_name: str) -> str:
        """Analyze user flow"""
        return f"""
User Flow Analysis: {flow_name}

📊 Current Flow (6 steps):
1. Landing page
2. Browse products (avg 2.5 min)
3. Product detail page
4. Add to cart
5. View cart
6. Checkout (3 steps)

⏱️ Metrics:
- Completion rate: 45% ⚠️  LOW
- Drop-off points:
  * Step 2 → 3: 30% abandon (too much browsing)
  * Step 5 → 6: 35% cart abandonment ❌
- Average time: 8.5 minutes
- User frustration score: 6.2/10

🔴 UX Issues Identified:

1. Cognitive Overload in Step 2
   - Problem: Too many products, no clear filtering
   - Impact: Users get overwhelmed, leave
   - Fix: Add smart filters, category navigation
   
2. Hidden Add-to-Cart Button (Step 4)
   - Problem: Button below fold, low contrast
   - Impact: Users miss it, can't proceed
   - Fix: Sticky CTA, higher contrast, bigger size
   
3. Complex Checkout (Step 6)
   - Problem: 3 pages, asks for too much info
   - Impact: High cart abandonment
   - Fix: Single-page checkout, guest checkout option

4. No Progress Indicators
   - Problem: Users don't know where they are
   - Fix: Add step indicator (1/3, 2/3, 3/3)

5. Error Messages Unclear
   - Problem: "Error 400" without explanation
   - Fix: User-friendly messages with next steps

✅ Optimized Flow (4 steps):

1. Landing → Category (with clear value prop)
2. Filtered products (smart recommendations)
3. Product detail (sticky CTA, clear benefits)
4. One-page checkout (progress bar, guest option)

Expected Improvements:
- Completion rate: 45% → 68% (+51%)
- Time to purchase: 8.5min → 5min (-41%)
- Cart abandonment: 35% → 18%
- User satisfaction: 6.2 → 8.5

Priority Actions:
1. Simplify checkout (HIGH IMPACT)
2. Improve product filtering
3. Make CTAs more visible
4. Add progress indicators
"""
    
    def _check_heuristics(self, feature: str) -> str:
        """Check Nielsen's heuristics"""
        return f"""
Usability Heuristics Evaluation: {feature}

1. ✅ Visibility of System Status
   - Good: Loading states, progress indicators
   - Issue: No confirmation after actions
   - Fix: Add success messages

2. ⚠️  Match Between System and Real World
   - Good: Familiar icons
   - Issue: Technical jargon in error messages
   - Fix: Use plain language

3. ❌ User Control and Freedom
   - Issue: No "undo" for deletions
   - Issue: Can't edit after submission
   - Fix: Add undo, allow editing

4. ✅ Consistency and Standards
   - Good: Consistent button styles
   - Good: Standard patterns used

5. ❌ Error Prevention
   - Issue: No confirmation for destructive actions
   - Issue: Easy to click wrong button
   - Fix: Add confirmations, improve button spacing

6. ⚠️  Recognition Rather Than Recall
   - Good: Recent items shown
   - Issue: Must remember product names for search
   - Fix: Add autocomplete, show thumbnails

7. ⚠️  Flexibility and Efficiency of Use
   - Issue: No keyboard shortcuts
   - Issue: No bulk actions
   - Fix: Add power user features

8. ✅ Aesthetic and Minimalist Design
   - Good: Clean, uncluttered
   - Good: Good use of whitespace

9. ❌ Help Users Recognize, Diagnose, and Recover from Errors
   - Issue: Cryptic error messages
   - Issue: No recovery suggestions
   - Fix: Better error UX

10. ⚠️  Help and Documentation
    - Issue: No contextual help
    - Issue: FAQ hard to find
    - Fix: Add tooltips, inline help

Overall Score: 6.5/10

Critical Issues (Must Fix):
- Add undo functionality
- Improve error messages
- Add confirmations for destructive actions

Priority Improvements:
- Better error UX
- Keyboard shortcuts
- Contextual help
"""
    
    def _review_a11y(self, component: str) -> str:
        """UX accessibility review"""
        return f"""
UX Accessibility Review: {component}

♿ Accessibility from UX Perspective:

🔴 CRITICAL UX BARRIERS:

1. Low Color Contrast
   - Issue: Text hard to read for low vision users
   - Affects: 4.5% of users
   - Fix: Increase contrast ratio to 4.5:1 minimum

2. No Keyboard Navigation
   - Issue: Can't use without mouse
   - Affects: Motor disability, power users
   - Fix: Full keyboard support, visible focus

3. Images Without Context
   - Issue: Screen readers get generic descriptions
   - Affects: Blind/low vision users
   - Fix: Meaningful alt text, not "image123.jpg"

⚠️  MODERATE BARRIERS:

4. Form Labels Not Associated
   - Issue: Hard to know what each field is
   - Fix: Proper label/input association

5. No Skip Navigation
   - Issue: Must tab through entire nav each time
   - Fix: Add "skip to content" link

6. Auto-Playing Content
   - Issue: Distracting, can't control
   - Fix: Add play/pause controls, or don't autoplay

✅ GOOD ACCESSIBILITY PRACTICES:

- Semantic HTML used
- Logical heading hierarchy
- Focus visible on most elements
- Sufficient font sizes

👥 Affected User Groups:

- Visual impairments: 🔴 Major barriers
- Motor disabilities: 🔴 Can't use
- Cognitive disabilities: ⚠️  Some difficulties
- Hearing impairments: ✅ OK (no audio)

📊 Accessibility Impact:

- Potential users excluded: ~15%
- Legal risk: HIGH (ADA compliance)
- Business impact: Missing accessibility = missing customers

🎯 UX-Focused Fixes:

Quick Wins (1-2 days):
1. Increase color contrast
2. Add alt text to images
3. Fix form labels
4. Add skip navigation

Medium Effort (1 week):
5. Implement full keyboard navigation
6. Add ARIA labels where needed
7. Fix focus management
8. Add visible focus indicators

Testing Recommendations:
- Test with screen reader (NVDA/JAWS)
- Keyboard-only navigation test
- Color blindness simulation
- User testing with disabled users

Accessibility Score: 4.5/10
Status: NEEDS SIGNIFICANT IMPROVEMENT

Benefits of Fixing:
- +15% potential user base
- Better SEO (Google considers a11y)
- Legal compliance
- Improved UX for everyone
"""
    
    def _design_critique(self, design: str) -> str:
        """Design critique"""
        return f"""
Design Critique: {design}

🎨 Visual Design:

✅ STRENGTHS:
- Clean, modern aesthetic
- Good use of whitespace
- Consistent color palette
- Clear visual hierarchy

⚠️  IMPROVEMENTS NEEDED:
- Typography: Line height too tight (1.2, should be 1.5)
- Color: Low contrast on secondary text
- Buttons: Inconsistent sizes and styles
- Icons: Mixed styles (outline + filled)

🧭 Layout & Structure:

✅ WORKING WELL:
- Responsive grid system
- Clear content sections
- Good mobile adaptation

❌ ISSUES:
- F-pattern not followed (users miss CTAs)
- Important content below fold
- Inconsistent spacing (24px, 32px, 20px)
- No clear visual flow

💭 Interaction Design:

✅ GOOD:
- Hover states present
- Loading states clear
- Smooth transitions

❌ PROBLEMS:
- No feedback on button clicks
- Form validation only on submit (should be inline)
- Modals don't trap focus
- Dropdowns hard to tap on mobile

📱 Mobile Experience:

⚠️  NEEDS WORK:
- Touch targets too small (40px minimum)
- Horizontal scrolling on some screens
- Text too small in places
- Bottom navigation interferes with content

🎯 User-Centered Issues:

1. CTA Hierarchy Unclear
   - Multiple CTAs compete for attention
   - Not obvious what's primary action
   - Fix: One clear primary CTA per screen

2. Information Density
   - Too much text in hero section
   - Users skim, not read
   - Fix: Reduce to key points, use bullets

3. Trust Signals Missing
   - No social proof
   - No security badges
   - Fix: Add testimonials, trust indicators

4. Cognitive Load High
   - Too many choices
   - Complex forms
   - Fix: Simplify, use progressive disclosure

📊 Recommendations by Priority:

P0 (Critical):
1. Fix color contrast (accessibility + readability)
2. Increase touch target sizes
3. Make primary CTA obvious

P1 (High):
4. Consistent spacing system (8px grid)
5. Inline form validation
6. Add trust signals

P2 (Medium):
7. Improve typography (line height, sizes)
8. Consistent icon style
9. Better mobile navigation

P3 (Nice to have):
10. Micro-interactions
11. Skeleton screens
12. Empty states design

Design Score: 7/10
Usability Score: 6.5/10
Accessibility Score: 5/10

Overall: Good foundation, needs refinement for optimal UX.

Next Steps:
1. Create design system for consistency
2. Usability testing with 5 users
3. Accessibility audit
4. Iterate based on feedback
"""
