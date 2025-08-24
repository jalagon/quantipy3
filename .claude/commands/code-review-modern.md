# Modern Code Review Command - Python 3.10+ Architecture Assessment

**Purpose**: Comprehensive code review using modern Python standards and tooling assessment.

**Environment**: Designed for `quantipy_modern` environment with ruff, mypy, pytest integration.

## Enhanced Review Standards

### Core Principles (Unchanged)
- **SOLID, DRY, KISS, YAGNI** design principles
- **Security-first** approach with defensive programming
- **Performance-conscious** design for scalability

### Modern Tooling Standards (Enhanced)
- **ruff compliance**: Python 3.10+ syntax enforcement with auto-fixes
- **mypy readiness**: Type hint coverage and static analysis compatibility  
- **pytest architecture**: Fixture-based testing with coverage gates
- **Modern Python features**: Pattern matching, union types, dataclasses

### Python 3.10-3.12 Modernization
- **Type system**: `list[str]` vs `List[str]`, union types `X | Y`
- **Pattern matching**: `match/case` statements for complex conditionals
- **Performance**: Modern syntax optimizations and best practices
- **Compatibility**: Ensures forward compatibility with Python 3.11-3.12

## Modern Assessment Process

### Phase 1: Automated Analysis
1. **Ruff Analysis**: Check for modernization opportunities and violations
2. **MyPy Baseline**: Establish type coverage and identify issues  
3. **Import Validation**: Verify successful module loading
4. **Architecture Scanning**: SOLID principle compliance assessment

### Phase 2: Manual Review
1. **Modern Pattern Assessment**: Evaluate use of Python 3.10+ features
2. **Type System Readiness**: Assess preparedness for comprehensive typing
3. **Testing Architecture**: Review test structure and coverage potential
4. **Performance Analysis**: Modern optimization opportunities

### Phase 3: Strategic Recommendations
1. **Modernization Roadmap**: Specific Python 3.10+ improvements
2. **Type Implementation Plan**: Gradual typing adoption strategy  
3. **Architecture Refactoring**: SOLID principle improvements
4. **Tooling Integration**: ruff/mypy/pytest optimization suggestions

## Enhanced Output Requirements

### Review Document Structure
Save as `ai-code-reviews/{filename}.modern.review.md`:

```markdown
# Modern Code Review: {filename}

**File**: {full_path}  
**Lines of Code**: {count}  
**Review Date**: {date}  
**Python Target**: 3.10-3.12  
**Tooling**: ruff + mypy + pytest  

## Executive Summary
**Overall Rating**: {Excellent/Good/Needs Improvement/Poor}  
**Modernization Score**: {1-10}/10  
**Type Readiness**: {Ready/Needs Work/Not Ready}  
**SOLID Compliance**: {High/Medium/Low}  

## Modern Tooling Assessment

### Ruff Analysis
- **Violations Found**: {count}
- **Auto-fixes Available**: {count} 
- **Modernization Opportunities**: {list}
- **Python 3.10+ Features**: {assessment}

### MyPy Readiness  
- **Type Coverage**: {percentage}%
- **Missing Annotations**: {count}
- **Union Type Opportunities**: {list}
- **Generic Type Usage**: {assessment}

### Pytest Architecture
- **Test Structure**: {assessment}
- **Fixture Usage**: {current_vs_recommended}
- **Coverage Potential**: {estimated_percentage}%
- **Parameterization**: {opportunities}

## SOLID Principle Analysis
{Detailed analysis with modern patterns}

## Python 3.10-3.12 Modernization
### Pattern Matching Opportunities
{Specific match/case recommendations}

### Type System Enhancement
{Modern typing recommendations}

### Performance Optimizations
{Python 3.10+ specific improvements}

## Action Plan
### Phase 1: Immediate (Week 2-3)
{Critical fixes and type baseline}

### Phase 2: Architecture (Week 4-5) 
{SOLID refactoring with modern patterns}

### Phase 3: Advanced (Week 6+)
{Full modernization implementation}
```

### Modern Quality Ratings

| Rating | Criteria |
|--------|----------|
| **Excellent (9-10)** | Full ruff compliance, 80%+ type coverage, SOLID adherent, Python 3.10+ features |
| **Good (7-8)** | Minor ruff issues, 60%+ type coverage, mostly SOLID, some modern features |
| **Needs Improvement (4-6)** | Multiple ruff violations, <40% type coverage, SOLID violations |
| **Poor (1-3)** | Major violations, no type hints, architectural debt, legacy patterns |

## Modern Review Checklist

### Code Quality & Standards
- [ ] **Ruff compliance**: Zero violations with modern rules
- [ ] **Type annotations**: Function signatures have type hints
- [ ] **Import organization**: Following ruff import sorting
- [ ] **Modern syntax**: f-strings, union types, etc.

### Architecture & Design
- [ ] **SOLID principles**: Each class has single responsibility
- [ ] **Pattern matching**: Complex conditionals use match/case
- [ ] **Error handling**: Specific exceptions, no bare except
- [ ] **Dataclasses**: Structured data uses @dataclass

### Testing & Validation
- [ ] **Pytest structure**: Uses fixtures and modern patterns
- [ ] **Coverage potential**: Code structure supports high coverage
- [ ] **Type safety**: MyPy compatible without suppressions
- [ ] **Import validation**: Module loads successfully

### Performance & Scalability  
- [ ] **Efficient algorithms**: No obvious performance anti-patterns
- [ ] **Memory management**: Appropriate data structure choices
- [ ] **Modern optimizations**: Uses Python 3.10+ performance features
- [ ] **Async readiness**: Architecture supports async patterns if needed

### Security & Robustness
- [ ] **Input validation**: All external inputs validated
- [ ] **Error boundaries**: Graceful error handling
- [ ] **Type safety**: Reduces runtime type errors
- [ ] **Defensive coding**: Guards against edge cases

## Integration with Development Workflow

### Before Review
1. Run `check-gates-modern.md $file` to establish baseline
2. Activate `quantipy_modern` environment  
3. Verify import success and basic functionality

### During Review
1. Use ruff output to identify modernization opportunities
2. Check mypy results for type system assessment
3. Evaluate against modern Python patterns
4. Consider pytest architecture improvements

### After Review
1. Generate actionable modernization roadmap
2. Provide specific ruff/mypy command examples
3. Suggest type hint implementation priorities
4. Document architecture refactoring needs

## Advanced Assessments

### Type System Maturity
- **Level 0**: No type hints, mypy failures
- **Level 1**: Basic type hints, some mypy compliance  
- **Level 2**: Comprehensive typing, generic usage
- **Level 3**: Advanced types, protocol usage, full mypy strict

### Modern Pattern Usage
- **Legacy**: String formatting, old-style unions
- **Transitional**: Mix of old and new patterns
- **Modern**: F-strings, `|` unions, match/case
- **Advanced**: Full Python 3.10+ feature utilization

### Architecture Evolution
- **Monolithic**: Single large classes/functions
- **Modular**: Broken down but not SOLID
- **SOLID**: Proper separation of concerns
- **Modern**: SOLID + Python 3.10+ patterns

## Success Metrics

### Immediate (Week 2-3)
- ✅ Zero ruff violations with auto-fixes applied
- ✅ MyPy baseline established (issues documented)
- ✅ Successful import validation
- ✅ Modern syntax adoption (f-strings, etc.)

### Architecture (Week 4-5)
- ✅ SOLID principle compliance 
- ✅ 60%+ type hint coverage
- ✅ Pattern matching implementation
- ✅ Pytest-ready structure

### Advanced (Week 6+)  
- ✅ 90%+ type coverage with mypy strict compliance
- ✅ Full Python 3.10+ feature utilization
- ✅ 80%+ test coverage achieved
- ✅ Performance optimizations implemented

This modern review process ensures comprehensive assessment for Python 3.10+ development while maintaining focus on architectural excellence and modern development practices.