#!/bin/bash
# Sprint 5: Comprehensive Coverage Reporting Script
# Implements 80% coverage threshold with detailed reporting

set -e

echo "🧪 Running comprehensive test coverage analysis..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Clean previous coverage data
print_status "Cleaning previous coverage data..."
rm -f .coverage
rm -rf htmlcov/

# Run tests with coverage
print_status "Running tests with coverage reporting..."
python -m pytest \
    --cov=quantipy \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-fail-under=80 \
    -v \
    tests/ || {
    print_error "Tests failed or coverage below 80% threshold"
    exit 1
}

# Generate additional coverage reports
if [ -f .coverage ]; then
    print_status "Generating additional coverage reports..."
    
    # Generate JSON report for tools integration
    python -m coverage json
    
    # Show coverage summary
    print_status "Coverage Summary:"
    python -m coverage report --show-missing
    
    # Check if coverage meets threshold
    COVERAGE=$(python -m coverage report --format=total)
    echo "Total coverage: ${COVERAGE}%"
    
    if (( $(echo "$COVERAGE >= 80" | bc -l) )); then
        print_success "✅ Coverage threshold met: ${COVERAGE}% >= 80%"
    else
        print_error "❌ Coverage below threshold: ${COVERAGE}% < 80%"
        exit 1
    fi
    
    print_success "HTML coverage report generated: htmlcov/index.html"
    print_success "XML coverage report generated: coverage.xml"
    print_success "JSON coverage report generated: coverage.json"
else
    print_error "No coverage data generated"
    exit 1
fi

print_success "🎉 Coverage analysis completed successfully!"