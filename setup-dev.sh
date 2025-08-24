#!/bin/bash
# quantipy3 Development Environment Setup
# Sets up a complete modern Python development environment for quantipy3

set -e  # Exit on error

echo "🚀 Setting up quantipy3 development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -d "quantipy" ]; then
    print_error "This script must be run from the quantipy3 root directory"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f2)

print_status "Detected Python version: $PYTHON_VERSION"

if [ "$MAJOR_VERSION" -ne 3 ] || [ "$MINOR_VERSION" -lt 10 ]; then
    print_error "Python 3.10+ is required. Please install Python 3.10, 3.11, or 3.12"
    exit 1
fi

print_success "Python version is compatible ✅"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created ✅"
else
    print_warning "Virtual environment already exists, skipping creation"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
print_status "Installing quantipy3 in development mode..."
pip install -e .

# Install development dependencies
print_status "Installing development tools..."
pip install \
    ruff==0.6.7 \
    mypy==1.8.0 \
    pytest==8.0.0 \
    pytest-cov==4.1.0 \
    pytest-xdist==3.5.0 \
    pre-commit==3.6.0 \
    bandit==1.7.5 \
    safety==3.0.1 \
    build==1.0.3 \
    wheel==0.42.0

# Install type stubs
print_status "Installing type stubs..."
pip install pandas-stubs types-requests || print_warning "Some type stubs may not be available"

# Install pre-commit hooks
print_status "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type pre-push

print_success "Pre-commit hooks installed ✅"

# Run initial quality check
print_status "Running initial quality checks..."

echo "📋 Checking code formatting..."
ruff format --check quantipy/ || print_warning "Code formatting issues detected (run 'ruff format quantipy/' to fix)"

echo "🔍 Running linter..."
ruff check quantipy/ || print_warning "Linting issues detected (run 'ruff check --fix quantipy/' to fix)"

echo "🔍 Running type checks on enhanced files..."
TYPE_CHECK_FILES=(
    "quantipy/core/weights/weight_engine.py"
    "quantipy/core/tools/dp/query.py"
    "quantipy/core/rules.py"
    "quantipy/core/cache.py"
    "quantipy/core/cluster.py"
    "quantipy/core/options.py"
    "quantipy/core/chain.py"
    "quantipy/core/stack.py"
)

for file in "${TYPE_CHECK_FILES[@]}"; do
    if [ -f "$file" ]; then
        mypy "$file" --ignore-missing-imports || print_warning "Type issues in $file"
    fi
done

# Test imports
print_status "Testing critical imports..."
python3 -c "
import quantipy as qp
from quantipy.core.stack import Stack
from quantipy.core.chain import Chain  
from quantipy.core.cache import Cache
from quantipy.core.cluster import Cluster
from quantipy.core.options import set_option
print('✅ All critical imports successful!')
" || print_error "Import test failed"

# Run basic tests if they exist
if [ -d "tests" ] && [ -n "$(ls -A tests/*.py 2>/dev/null)" ]; then
    print_status "Running basic test suite..."
    pytest tests/ -v --tb=short -x || print_warning "Some tests failed - this is expected during development"
else
    print_warning "No tests found in tests/ directory"
fi

# Create development configuration
print_status "Creating development configuration..."

cat > .env.dev << 'EOF'
# quantipy3 Development Environment
# This file contains development-specific environment variables

# Python environment
PYTHONPATH=.
QUANTIPY_ENV=development

# Development tools
QUANTIPY_DEBUG=1
QUANTIPY_TESTING=1

# Modern Python features
QUANTIPY_USE_MODERN_SYNTAX=1
EOF

print_success "Development environment configuration created ✅"

# Summary
echo ""
echo "🎉 Development environment setup completed!"
echo ""
print_success "Environment Summary:"
echo "  • Python version: $PYTHON_VERSION"
echo "  • Virtual environment: ./venv"
echo "  • Development tools installed: ruff, mypy, pytest, pre-commit"
echo "  • Pre-commit hooks configured"
echo "  • Package installed in development mode"
echo ""
print_status "Next steps:"
echo "  1. Activate the environment: source venv/bin/activate"
echo "  2. Run tests: pytest tests/"
echo "  3. Check code quality: ruff check quantipy/"
echo "  4. Format code: ruff format quantipy/"
echo "  5. Type check: mypy quantipy/core/stack.py --ignore-missing-imports"
echo ""
print_success "Happy coding! 🚀"