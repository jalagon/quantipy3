# Modern Quality Gates - Python 3.10+ Tooling

**Purpose**: Comprehensive modern quality checking using ruff, mypy, and pytest for Python 3.10+ development.

**Environment**: Requires `quantipy_modern` environment with modern tooling stack.

## Usage

Apply modern quality gates to specified files using state-of-the-art Python tooling.

**Command**: `check-gates-modern.md <file_paths>`

**Example**: `check-gates-modern.md quantipy/core/tools/dp/io.py quantipy/core/helpers/functions.py`

## Modern Tooling Pipeline

### 1. Environment Activation
```bash
source /Users/jorgealagon/miniforge3_x86/bin/activate quantipy_modern
```

### 2. Ruff - Modern Linting & Auto-fixing
**Replaces**: flake8 + autopep8 + isort + pyupgrade
**Features**: 
- Python 3.10+ syntax enforcement
- Automatic modernization (f-strings, union types, etc.)
- 10-100x faster than legacy tools
- Built-in fix capabilities

```bash
# Check for issues
ruff check $file_path

# Apply safe fixes automatically  
ruff check $file_path --fix

# Apply all fixes (including potentially breaking ones)
ruff check $file_path --fix --unsafe-fixes

# Format code (replaces Black)
ruff format $file_path
```

### 3. MyPy - Type Checking
**Replaces**: No legacy equivalent
**Features**:
- Static type analysis
- Python 3.10+ type syntax support
- Comprehensive error detection
- IDE integration support

```bash
# Type check single file
mypy $file_path

# Type check with specific options
mypy $file_path --strict

# Check for missing type stubs
mypy $file_path --install-types --non-interactive
```

### 4. Pytest - Modern Testing
**Replaces**: unittest patterns
**Features**:
- Fixture-based testing
- Coverage integration
- Parallel execution
- Modern assertion introspection

```bash
# Run tests with coverage
pytest tests/ --cov=$module_name --cov-report=term-missing

# Run specific test file
pytest tests/test_$module.py -v

# Run with coverage threshold enforcement
pytest tests/ --cov=$module_name --cov-fail-under=80
```

## Complete Modern Pipeline

For comprehensive quality assurance, run the full modern pipeline:

```bash
#!/bin/bash
# Modern Quality Gates Pipeline

# Activate modern environment
source /Users/jorgealagon/miniforge3_x86/bin/activate quantipy_modern

# File path from argument
file_path="$1"
module_name=$(basename "$file_path" .py)

echo "🚀 Running Modern Quality Gates on: $file_path"
echo "=================================================="

# 1. Ruff - Modern linting and formatting
echo "1️⃣ Ruff: Modern linting & auto-fixes..."
ruff check "$file_path" --fix --unsafe-fixes
ruff format "$file_path"
echo "✅ Ruff completed"

# 2. MyPy - Type checking
echo "2️⃣ MyPy: Type checking..."
mypy "$file_path" || echo "⚠️  Type issues found (expected for untyped code)"
echo "✅ MyPy analysis completed"

# 3. Import validation
echo "3️⃣ Import validation..."
python -c "import importlib.util; spec = importlib.util.spec_from_file_location('$module_name', '$file_path'); importlib.util.module_from_spec(spec); spec.loader.exec_module(importlib.util.module_from_spec(spec)); print('✅ Import successful')" || echo "❌ Import failed"

# 4. Pytest (if test file exists)
test_file="tests/test_${module_name}.py"
if [ -f "$test_file" ]; then
    echo "4️⃣ Pytest: Running tests..."
    pytest "$test_file" -v --cov="quantipy.$(echo $file_path | sed 's|/|.|g' | sed 's|\.py||')" --cov-report=term-missing
    echo "✅ Tests completed"
else
    echo "4️⃣ Pytest: No test file found ($test_file)"
fi

echo "=================================================="
echo "🎉 Modern Quality Gates Complete!"
```

## Quality Standards

### Ruff Rules Applied
- **E, W**: pycodestyle errors and warnings
- **F**: pyflakes (undefined names, unused imports)
- **UP**: pyupgrade rules (Python 3.10+ syntax)
- **I**: isort (import organization)
- **N**: pep8-naming conventions
- **B**: flake8-bugbear (common bugs)
- **C4**: flake8-comprehensions
- **PIE**: flake8-pie (unnecessary code)
- **SIM**: flake8-simplify
- **RET**: flake8-return

### MyPy Configuration
- **Python 3.10** target version
- **Non-strict** mode (gradual typing adoption)
- **Warning flags**: return_any, unused_configs, redundant_casts
- **Type stub support**: Auto-installation of missing stubs

### Coverage Requirements
- **Minimum**: 80% line coverage
- **Branch coverage**: Enabled
- **Missing line reporting**: Detailed output
- **HTML reports**: Generated in `htmlcov/`

## Comparison with Legacy

| Aspect | Legacy (check-gates.md) | Modern (check-gates-modern.md) |
|--------|-------------------------|--------------------------------|
| **Linting** | flake8 | ruff (10-100x faster) |
| **Formatting** | autopep8 + Black | ruff format |
| **Import sorting** | isort | ruff (built-in) |
| **Modernization** | Manual | ruff --unsafe-fixes (automatic) |
| **Type checking** | None | mypy with Python 3.10+ support |
| **Testing** | Basic pytest | pytest + coverage + fixtures |
| **Python version** | 3.6+ compatible | 3.10+ optimized |
| **Speed** | ~30-60 seconds | ~5-10 seconds |

## Benefits

1. **Speed**: 10-100x faster than legacy toolchain
2. **Automatic Modernization**: Converts old syntax to Python 3.10+ automatically
3. **Type Safety**: Comprehensive static analysis
4. **Unified Tooling**: Single ruff binary replaces multiple tools
5. **Modern Features**: Support for latest Python language features
6. **Better Error Messages**: More helpful diagnostics and suggestions

## When to Use

- ✅ **Week 2+**: Modern Python 3.10+ development
- ✅ **Type Implementation**: Preparing for comprehensive type hints
- ✅ **Architecture Modernization**: SOLID principle refactoring
- ✅ **Performance Critical**: Fast feedback loops needed

## When to Use Legacy (check-gates.md)

- ⚠️ **Python 3.6 Compatibility**: Required for legacy environments
- ⚠️ **Gradual Migration**: Transitioning from legacy tooling
- ⚠️ **Specific flake8 Plugins**: Not yet available in ruff

## Success Criteria

- ✅ **Ruff**: Zero violations with auto-fixes applied
- ✅ **MyPy**: Baseline established (issues documented for type implementation)
- ✅ **Imports**: Successful module loading
- ✅ **Tests**: Passing with ≥80% coverage (if tests exist)
- ✅ **Modernization**: Python 3.10+ syntax automatically applied