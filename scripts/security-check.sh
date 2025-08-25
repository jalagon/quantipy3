#!/bin/bash
# Sprint 5: Comprehensive Security Analysis Script
# Implements security scanning and dependency vulnerability checking

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[SECURITY]${NC} $1"
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

print_status "🔒 Starting comprehensive security analysis..."

# Create reports directory
mkdir -p security-reports

# 1. Bandit Security Analysis
print_status "Running Bandit security analysis..."
bandit -r quantipy/ \
    -f json -o security-reports/bandit-report.json \
    --exclude tests/ \
    || {
    print_warning "Bandit found potential security issues (see security-reports/bandit-report.json)"
    bandit -r quantipy/ --exclude tests/ || true
}

# Generate human-readable bandit report
bandit -r quantipy/ \
    -f txt -o security-reports/bandit-report.txt \
    --exclude tests/ \
    || print_warning "Bandit analysis completed with issues"

print_success "✅ Bandit analysis completed"

# 2. Safety - Dependency Vulnerability Check
print_status "Checking dependencies for known security vulnerabilities..."
safety check \
    --json --output security-reports/safety-report.json \
    || {
    print_warning "Safety found vulnerable dependencies (see security-reports/safety-report.json)"
    safety check || true
}

print_success "✅ Dependency vulnerability check completed"

# 3. pip-audit (alternative dependency scanner)
print_status "Running pip-audit for additional dependency scanning..."
pip install pip-audit --quiet 2>/dev/null || {
    print_warning "pip-audit not available, skipping additional dependency scan"
}

if command -v pip-audit &> /dev/null; then
    pip-audit \
        --format=json --output=security-reports/pip-audit-report.json \
        || {
        print_warning "pip-audit found issues (see security-reports/pip-audit-report.json)"
        pip-audit || true
    }
    print_success "✅ pip-audit analysis completed"
else
    print_warning "⚠️ pip-audit not available"
fi

# 4. Check for secrets/keys (simple grep-based scan)
print_status "Scanning for potential secrets and API keys..."
SECRET_PATTERNS=(
    "password"
    "api_key"
    "secret"
    "token"
    "private_key"
    "aws_access_key"
    "ssh_key"
)

SECRET_FOUND=false
for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -i "$pattern" quantipy/ --exclude-dir=__pycache__ | grep -v ".pyc" | grep -q .; then
        print_warning "Potential secret pattern '$pattern' found:"
        grep -r -i "$pattern" quantipy/ --exclude-dir=__pycache__ | grep -v ".pyc" | head -3
        SECRET_FOUND=true
    fi
done

if [ "$SECRET_FOUND" = false ]; then
    print_success "✅ No obvious secret patterns detected"
fi

# 5. File permissions check
print_status "Checking file permissions for security issues..."
INSECURE_FILES=$(find quantipy/ -type f -perm /o+w 2>/dev/null || true)
if [ -n "$INSECURE_FILES" ]; then
    print_warning "Files with world-writable permissions found:"
    echo "$INSECURE_FILES"
else
    print_success "✅ No insecure file permissions detected"
fi

# 6. Generate security summary report
print_status "Generating security summary report..."
cat > security-reports/security-summary.txt << EOF
Security Analysis Summary
========================
Date: $(date)
Project: quantipy3

Analysis Performed:
- Bandit: Code security vulnerability scan
- Safety: Dependency vulnerability check
- pip-audit: Alternative dependency scan (if available)
- Secret pattern detection
- File permission check

Reports Generated:
- security-reports/bandit-report.json (JSON format)
- security-reports/bandit-report.txt (Human readable)
- security-reports/safety-report.json (JSON format)
- security-reports/pip-audit-report.json (if available)

Review these reports for detailed findings.

Next Steps:
1. Review all generated reports
2. Address any HIGH severity issues immediately
3. Plan remediation for MEDIUM severity issues
4. Consider LOW severity issues for future improvements

EOF

print_success "✅ Security summary report generated: security-reports/security-summary.txt"

# 7. Exit code determination
CRITICAL_ISSUES=false

# Check bandit for high severity issues
if [ -f security-reports/bandit-report.json ]; then
    HIGH_SEVERITY=$(grep -c '"issue_severity": "HIGH"' security-reports/bandit-report.json 2>/dev/null || echo "0")
    if [ "$HIGH_SEVERITY" -gt "0" ]; then
        print_error "❌ $HIGH_SEVERITY HIGH severity security issues found by Bandit"
        CRITICAL_ISSUES=true
    fi
fi

# Check safety for vulnerabilities
if [ -f security-reports/safety-report.json ]; then
    if grep -q '"vulnerabilities"' security-reports/safety-report.json 2>/dev/null; then
        print_error "❌ Vulnerable dependencies found by Safety"
        CRITICAL_ISSUES=true
    fi
fi

if [ "$CRITICAL_ISSUES" = true ]; then
    print_error "🚨 CRITICAL SECURITY ISSUES FOUND - Please review security reports immediately"
    exit 1
else
    print_success "🎉 Security analysis completed - No critical issues detected"
    print_status "📊 Review security-reports/ directory for detailed analysis"
fi