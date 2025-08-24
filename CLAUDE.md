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
quantipy3 is a Python 3 port of the Quantipy library - a data processing, analysis and reporting software for "people data" (survey/market research data). It builds on pandas/numpy and offers specialized handling of survey data types, metadata, weights, and statistical analysis. We will be updating it to newer Python (3.10-3.12) and package versions.

## Development Commands
- `check-gates.md`: run linting and code formatting
- `KISS-SOLID-check.md`: check design principles
- `code-review.md`: design principles, CI+Lint+types, Python 3.10–3.12, enable pytest and ruff
- `document_feature.md`: generate documentation for new feature both developer and user-facing
- `document_feature_advanced.md`: generate intelligent, multi-dimensional documentation with AI-powered analysis, accessibility compliance, and automated quality assurance

### Testing
- Run all tests: `python3 -m pytest tests`
- Run specific test module: `python3 -m unittest tests.test_dataset`
- Run tests with coverage: `coverage run -m unittest discover` then `coverage html` for reports
- Auto-run tests on file changes: `python autotests.py`

### Testing Standards & Quality Gates
**CRITICAL**: Several test files have significant quality issues that must be addressed:

#### Test Implementation Status
- ❌ `tests/test_stack.py` - SKIPPED (Python 3 port incomplete)
- ❌ `tests/test_view.py` - EMPTY (zero implementation)  
- ⚠️ `tests/test_dataset.py` - Needs refactoring (violates SRP)
- ✅ `tests/test_chain.py` - EXCELLENT (reference implementation)
- ✅ `tests/test_batch.py` - GOOD (minor improvements needed)

#### Testing Framework Migration
- **Target**: Migrate from unittest to pytest (following test_chain.py patterns)
- **Required**: Implement comprehensive fixtures for test data management
- **Priority**: Complete Python 3 compatibility for all test files

#### Test Quality Requirements
- All test classes must follow Single Responsibility Principle
- Maximum 20 test methods per class (split large classes)
- Use pytest fixtures instead of setUp() methods
- Implement proper test isolation and cleanup
- Add error condition testing for all core functionality

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
- Core: pandas (0.25.3), numpy (1.14.5), scipy (1.2.1)
- I/O: pyreadstat (1.1.2) for SPSS files
- Reporting: xlsxwriter, python-pptx
- Testing: pytest, pytest-cov, pytest-xdist

## Development Notes
- Package uses exact dependency pinning for reproducible builds
- Python 3.5+ supported (3.8 not fully tested)
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
**Immediate Action Required**:
1. **test_stack.py**: Remove `@unittest.skip` and complete Python 3 implementation
2. **test_view.py**: Implement comprehensive View class testing (currently empty)
3. **test_dataset.py**: Refactor monolithic test class into focused components

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

## Code Review Reports Available
Comprehensive code reviews have been generated in `ai-code-reviews/` directory:

### Core Module Reviews (Production Code)
- `dataset.py.review.md` - **CRITICAL PRIORITY** (Poor - 3/10) - Monolithic class requiring major refactoring
- `stack.py.review.md` - **IMMEDIATE ACTION** (Needs Improvement - 3/10) - Critical bugs in logic and error handling  
- `batch.py.review.md` - **HIGH PRIORITY** (Needs Improvement - 4/10) - Complex architecture needs decomposition
- `view.py.review.md` - **MEDIUM PRIORITY** (Needs Improvement - 4/10) - SOLID principle violations
- `chain.py.review.md` - **LOW PRIORITY** (Good - 6/10) - Well-designed, needs type hints and minor improvements
- `rim.py.review.md` - **MEDIUM PRIORITY** (Needs Improvement - 4/10) - Deprecated pandas usage and error handling issues
- `weight_engine.py.review.md` - **LOW PRIORITY** (Good - 6/10) - Clean coordination layer, needs type annotations
- `__init__.py.review.md` - (Excellent - 9/10) - Appropriately minimal

### Test Suite Reviews  
- `test_dataset.py.review.md` - Comprehensive review (Needs Improvement)
- `test_batch.py.review.md` - Quality assessment (Good)  
- `test_chain.py.review.md` - Best practices example (Excellent)
- `test_stack.py.review.md` - Critical issues identified (Poor)
- `test_view.py.review.md` - Implementation gap analysis (Critical)

These reports provide detailed SOLID principle analysis, refactoring recommendations, and technical debt assessments. **Priority should be given to core module issues, especially stack.py and dataset.py which contain critical bugs and architecture problems.**

### Current Codebase Status
Based on comprehensive code reviews, the quantipy3 codebase has significant technical debt:
- **CRITICAL ISSUES**: `stack.py` contains logic bugs (string identity comparisons) and bare exception handlers that risk data integrity
- **MAJOR REFACTORING NEEDED**: `dataset.py` is a 7,595-line monolithic class violating all SOLID principles  
- **DEPRECATED API USAGE**: Multiple files use deprecated pandas methods that will break in newer versions
- **TYPE SAFETY**: Complete absence of type hints across most core modules
- **ARCHITECTURE**: Most core classes need decomposition following SOLID principles

**Recommended Development Approach**: Address critical bugs first, then systematic modernization and refactoring following the priorities outlined in the review reports.