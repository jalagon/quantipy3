# KISS & SOLID Check Command

Review $ARGUMENTS for compliance with **KISS** (Keep It Simple, Stupid) and **SOLID** principles.  
Return a concise, actionable report.

---

## Standards
- **KISS:** simple, clear, avoid over-engineering.  
- **SOLID:** SRP (single responsibility), OCP (open/closed), LSP (substitution), ISP (narrow interfaces), DIP (abstract dependencies).  

---

## Process
1. Read exemplars (`src/components/ExpenseForm.tsx`, `src/utils/dataValidation.ts`) for conventions.  
2. Analyze $ARGUMENTS for complexity, responsibilities, and dependencies.  
3. Check each principle:
   - **KISS:** is code unnecessarily complex?  
   - **SRP:** one reason to change?  
   - **OCP:** extensible without editing core?  
   - **LSP:** subtypes behave correctly?  
   - **ISP:** interfaces too broad?  
   - **DIP:** depend on abstractions, not concretes?  
4. Recommend minimal refactors.

---

## Output
- Save as: `ai-design-reviews/{filename}.kiss-solid.md`  
- Include:
  - Verdict: Pass / Needs Improvement / Fail  
  - Score (0–5) for KISS & each SOLID principle  
  - Key issues with file+line refs  
  - 2–3 concrete refactor suggestions  

---

## Checklist
- ≤300 LOC per file; split if bigger  
- Import flow: `ui → domain → infra` only  
- No god objects, deep nesting, or magic numbers  
- Interfaces small & focused  
- Dependencies inverted at boundaries  