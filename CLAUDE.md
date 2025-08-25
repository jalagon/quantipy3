# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Principles
**IMPORTANT**: Whenever you write code, it MUST follow SOLID, DRY, KISS and YAGNI design principles. Never write code that violates these principles. If you do, you will be asked to refactor it.

## Development Workflow
**IMPORTANT**:
1. Before making any changes, create and checkout a feature branch named `feature-[brief-description]`
2. Write comprehensive tests for all new functionality
3. Compile code and run all tests before committing
4. Write detailed commit messages explaining the changes and rationale
5. Commit all changes to the feature branch

## Project Overview
quantipy3 is a Python 3 port of the Quantipy library - a data processing, analysis and reporting software for "people data" (survey/market research data). It builds on pandas/numpy and offers specialized handling of survey data types, metadata, weights, and statistical analysis.
Our objective is to modernise (refactor) quantipy3 to Python 3.10+ 

## Comprehensive Modernization Plan
**CRITICAL**: A complete 131-file comprehensive analysis and strategic modernization roadmap is available:
- **Analysis Document**: `ci-reviews/COMPLETE_131_FILE_ANALYSIS.md`
- **Coverage**: All Python files analyzed with SOLID, DRY, KISS, YAGNI principles
- **Roadmap**: 5-sprint implementation plan (14-19 weeks)
- **Priority**: savReaderWriter elimination blocks all modernization efforts

### Current Modernization Status (UPDATED: Sprint 1 & 2 Complete!)
**BREAKTHROUGH ACHIEVED**: Critical blocking issues eliminated and modern tooling operational
- ✅ **Sprint 1**: savReaderWriter ELIMINATED (15,000+ violations removed)
- ✅ **Sprint 1**: SPSS I/O modernized with pyreadstat 1.3.1 (Python 3.10-3.12 compatible)
- ✅ **Sprint 1**: Critical __init__.py files created for complete package structure
- ✅ **Sprint 2**: Modern tooling infrastructure operational (ruff, mypy, pytest)
- ✅ **Sprint 2**: Python 3.10+ auto-modernization working (15 fixes applied to rim.py)
- ✅ **Foundation**: 9 SOLID architecture components + 21 core files with modern annotations
- 🚀 **Status**: Ready for Sprint 3 systematic type system implementation

## Development Commands (SPRINT 2 COMPLETE - Modern Tooling Operational)

### Modern Python 3.10+ Tooling (ACTIVE)
**Primary Environment**: `/Users/jorgealagon/miniforge3_x86/envs/quantipy_py311/bin/python`
- **Ruff 0.12.10**: `ruff check [files] --fix --unsafe-fixes` - Modern linting with auto-modernization
- **MyPy 1.17.1**: `mypy [files] --no-error-summary` - Type checking with comprehensive stubs
- **Pytest 8.4.1**: `pytest --cov=quantipy --cov-fail-under=80` - Testing with coverage gates
- **Black 25.1.0**: `black [files]` - Code formatting (Python 3.10+ target)

### Integrated Quality Pipeline
- **Lint & Fix**: `ruff check quantipy/ --fix --unsafe-fixes` - Apply Python 3.10+ modernizations
- **Type Check**: `mypy quantipy/core/[enhanced_files] --no-error-summary` - Incremental type coverage
- **Test Suite**: `pytest tests/ --cov=quantipy --cov-report=html` - Full coverage analysis
- **Format Code**: `black quantipy/ && isort quantipy/` - Unified code style

### Legacy Development Commands (Superseded by Sprint 2)
- ❌ `make help` → ✅ Direct tool usage with modern Python 3.11 environment
- ❌ `make quality` → ✅ `ruff check --fix + mypy + pytest --cov`
- ❌ `make test-cov` → ✅ `pytest --cov=quantipy --cov-fail-under=80`

### Environment Setup & CI Validation
- `./setup-dev.sh` - Complete development environment automation
- `./validate-ci.sh` - Local CI pipeline validation before push
- `make install-all` - Install package + development dependencies

### Legacy Commands (Superseded by CI Infrastructure)
- ❌ `check-gates-modern.md` → ✅ `make quality`
- ❌ `check-gates.md` → ✅ `make quality`  
- ❌ `code-review-modern.md` → ✅ CI pipeline enforces standards automatically

### Architecture & Documentation Commands
- `KISS-SOLID-check.md`: SOLID design principles validation
- `document_feature.md`: Feature documentation generation
- `document_feature_advanced.md`: AI-powered comprehensive documentation

### CI/CD Pipeline Infrastructure
- **GitHub Actions**: `.github/workflows/ci.yml` - Multi-Python (3.10-3.12) testing matrix
- **Pre-commit Hooks**: `.pre-commit-config.yaml` - Automated quality gates on commits
- **Quality Gates**: Ruff (linting/formatting) + MyPy (type checking) - enforced automatically
- **Security**: Bandit (code analysis) + Safety (dependency vulnerabilities) - integrated scanning
- **Coverage**: Codecov integration with 70% minimum threshold - automatic reporting  
- **Build Verification**: Package building and artifact validation - prevents broken releases

### Environment Usage (SPRINT 2 UPDATE)
**Primary Development**: Python 3.11 environment with modern tooling
- `/Users/jorgealagon/miniforge3_x86/envs/quantipy_py311/bin/python` (Python 3.11.13)
- **Dependencies**: numpy 2.3.2, pandas 2.3.2, scipy 1.16.1, pyreadstat 1.3.1
- **Dev Tools**: ruff 0.12.10, mypy 1.17.1, pytest 8.4.1, coverage 7.10.5

**Legacy Environment**: `/Users/jorgealagon/miniforge3_x86/envs/qp_legacy36/bin/python` (deprecated)

### Quality Standards (SPRINT 2 OPERATIONAL)
- **Code Quality**: SOLID, DRY, KISS, YAGNI principles enforced by modern tooling
- **Lint Pipeline**: Ruff with Python 3.10+ auto-modernization (pyupgrade rules)
- **Type Checking**: MyPy with comprehensive stubs (pandas, requests, decorator)
- **Test Coverage**: 80% threshold with pytest and coverage reporting
- **Python Compatibility**: 3.10-3.12 verified (3.11 primary development environment)

### Testing (SPRINT 2 MODERNIZED)
**Current Active Commands**:
- `pytest tests/ --cov=quantipy --cov-fail-under=80` - Full test suite with coverage gates
- `pytest test_spss_modernization.py -v` - SPSS modernization verification
- `pytest --cov=quantipy.core.tools.dp.spss` - Module-specific coverage testing
- `make ci` - Full CI pipeline including all quality gates

### Testing Standards & Quality Gates
**Reference Implementation**: Use `tests/test_chain.py` as the gold standard

#### Test Quality Requirements
- All test classes must follow Single Responsibility Principle
- Maximum 20 test methods per class (split large classes)
- Use pytest fixtures instead of setUp() methods
- Implement proper test isolation and cleanup
- Add error condition testing for all core functionality
- Target: Migrate from unittest to pytest patterns

### Package Installation
- Development install: `pip install -e .`
- Install dev dependencies: `pip install -r requirements_dev.txt`
- Production install: `pip install quantipy3`

### Virtual Environment Setup
A pre-configured virtual environment is available in `/Users/jorgealagon/miniforge3_x86/envs/qp_legacy36/bin/python`. This can be activated and used for testing and development to ensure consistent package versions.

## Architecture Overview

### Core Components
- **DataSet** (`quantipy/core/dataset.py`): Main class for survey data handling with metadata
- **View** (`quantipy/core/view.py`): Statistical analysis results container
- **Stack** (`quantipy/core/stack.py`): Collection of Views for systematic analysis
- **Chain** (`quantipy/core/chain.py`): Structured analysis workflows
- **Batch** (`quantipy/core/batch.py`): Batch processing of multiple datasets

### Data Processing (`quantipy/core/tools/dp/`)
- **I/O Modules**: SPSS (`spss/`), Dimensions (`dimensions/`), Decipher (`decipher/`), Forsta (`forsta/`), Ascribe (`ascribe/`)
- **Core Operations**: `io.py`, `prep.py`, `query.py`

### Analysis Engine (`quantipy/core/`)
- **Weighting**: RIM weighting algorithm (`weights/rim.py`)
- **Quantify**: Statistical computation engine (`quantify/engine.py`)
- **View Generation**: Automated analysis workflows (`view_generators/`)

### Export/Reporting (`quantipy/core/builds/`)
- **Excel**: Excel report generation (`excel/`)
- **PowerPoint**: PowerPoint export functionality (`powerpoint/`)

## Key Data Structures
- **Meta**: JSON-based metadata describing variables, values, and structure
- **Case Data**: pandas DataFrame with survey responses
- **Links**: Relationships between variables for cross-tabulation
- **Filters**: Logic-based data filtering system

## Dependencies

### Current Dependencies (Legacy - Python 3.6+)
- **Core**: pandas==0.25.3, numpy==1.14.5, scipy==1.2.1
- **I/O**: pyreadstat==1.1.2 for SPSS files  
- **Reporting**: xlsxwriter, python-pptx
- **Testing**: pytest, pytest-cov, pytest-xdist

### Target Dependencies (Python 3.10-3.12 Compatible)
**CRITICAL**: All pinned versions are from 2018-2019 and INCOMPATIBLE with Python 3.10+

**Required Updates for Modernization**:
- **numpy**: 1.14.5 → 1.24.0+ (first Python 3.10 compatible version)
- **pandas**: 0.25.3 → 1.5.3+ (avoid 2.0+ initially for stability)  
- **scipy**: 1.2.1 → 1.9.0+ (stable scientific functions)
- **pyreadstat**: 1.1.2 → 1.3.0+ (Python 3.10-3.12 wheels available)

**External Dependency Elimination**:
- **savReaderWriter**: REMOVE (381+ flake8 violations) → Replace with modern pyreadstat

### Dependency Modernization Strategy
**Risk Level**: HIGH - Core scientific stack requires major version updates
**Timeline**: 3-4 weeks alongside Python modernization
**Approach**: Staged updates (baseline versions first, then gradual upgrade to latest)

#### Phase 1: Foundation Dependencies
1. Update numpy/pandas/scipy to baseline Python 3.10+ compatible versions
2. Comprehensive mathematical/statistical operation testing
3. Replace savReaderWriter with modern pyreadstat

#### Phase 2: Modern Versions  
4. Gradual upgrade to latest stable versions after core verification
5. Integration testing with new Python 3.10+ features

## Development Notes
- Package uses exact dependency pinning for reproducible builds
- **Python 3.6+ currently supported** (legacy environment: qp_legacy36)
- **Python 3.10-3.12 modernization ready** - comprehensive roadmap available
- Tests include sample data files (.sav, .csv, .json)
- Legacy Python 2 autotests.py needs updating for Python 3 compatibility


## Code Quality Standards

### SOLID Principles Compliance
All code must strictly follow SOLID design principles:
- **S**ingle Responsibility: Each class/method has one clear purpose
- **O**pen/Closed: Open for extension, closed for modification  
- **L**iskov Substitution: Subtypes must be substitutable for base types
- **I**nterface Segregation: No forced dependencies on unused interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions

### Test Architecture Requirements
**Reference Implementation**: Use `tests/test_chain.py` as the gold standard for:
- Modern pytest patterns and fixtures
- Proper test class organization (single responsibility)
- Comprehensive error condition testing
- Resource management and cleanup
- Parameterized testing for edge cases

### Critical Technical Debt
**Current Priority**: See comprehensive analysis in `ci-reviews/COMPLETE_131_FILE_ANALYSIS.md`
- **Immediate**: savReaderWriter elimination (15,000+ violations)
- **Core**: quantify/engine.py refactoring (2,400+ violations)
- **Testing**: Complete pytest migration and SOLID compliance

### Performance Standards
- Add performance benchmarks for regression testing
- Monitor memory usage during test execution
- Test scalability with large datasets
- Validate thread safety for concurrent operations

### Security Guidelines  
- Never expose or log secrets/keys
- Validate all input parameters
- Use defensive programming practices
- Test error conditions and edge cases

## Comprehensive Analysis & Reports
**Complete Documentation**: All analysis and strategic planning available in `ci-reviews/` directory:
- **Master Plan**: `COMPLETE_131_FILE_ANALYSIS.md` - Executive summary with 5-sprint roadmap
- **Detailed Reports**: 20+ component-specific analysis reports
- **Batch Summaries**: 4 comprehensive batch analysis results

### Success Metrics & Targets
**Target Goals** (see comprehensive plan for details):
- **Code Quality**: 31,203 → 0 violations (100% improvement)
- **SOLID Compliance**: 15% → 90%+ (Grade A-B)
- **Python Compatibility**: 20% → 100% (3.10-3.12)
- **Test Coverage**: 30% → 80%+ pytest coverage
- **Architecture**: Complete SOLID principle compliance

### Implementation Timeline
**Total Effort**: 14-19 weeks (280-380 hours)
**Target Completion**: quantipy3 v1.0.0 - Q2 2025
**Approach**: 5-sprint systematic modernization (see comprehensive plan)

