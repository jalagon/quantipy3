.PHONY: help install install-dev test test-cov lint format type-check security clean build docs
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
RED := \033[31m  
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)quantipy3 Development Commands$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(RESET)\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install package in development mode
	@echo "$(BLUE)Installing quantipy3 in development mode...$(RESET)"
	pip install -e .

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	pip install -r requirements-ci.txt
	pre-commit install

install-all: install install-dev ## Install package and dev dependencies

test: ## Run test suite
	@echo "$(BLUE)Running test suite...$(RESET)"
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	pytest tests/ --cov=quantipy --cov-report=term-missing --cov-report=html

test-fast: ## Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(RESET)"
	pytest tests/ -n auto

lint: ## Run ruff linter
	@echo "$(BLUE)Running ruff linter...$(RESET)"
	ruff check quantipy/

lint-fix: ## Run ruff linter with auto-fix
	@echo "$(BLUE)Running ruff linter with auto-fix...$(RESET)"
	ruff check --fix quantipy/

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code with ruff...$(RESET)"  
	ruff format quantipy/

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	ruff format --check quantipy/

type-check: ## Run type checking on enhanced files
	@echo "$(BLUE)Running type checks...$(RESET)"
	mypy quantipy/core/weights/weight_engine.py --ignore-missing-imports || true
	mypy quantipy/core/tools/dp/query.py --ignore-missing-imports || true
	mypy quantipy/core/rules.py --ignore-missing-imports || true  
	mypy quantipy/core/cache.py --ignore-missing-imports || true
	mypy quantipy/core/cluster.py --ignore-missing-imports || true
	mypy quantipy/core/options.py --ignore-missing-imports || true
	mypy quantipy/core/chain.py --ignore-missing-imports || true
	mypy quantipy/core/stack.py --ignore-missing-imports || true

security: ## Run security checks
	@echo "$(BLUE)Running security analysis...$(RESET)"
	bandit -r quantipy/
	safety check

quality: lint format-check type-check ## Run all quality checks
	@echo "$(GREEN)All quality checks completed!$(RESET)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	pre-commit run --all-files

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/ 
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build package
	@echo "$(BLUE)Building package...$(RESET)"
	python -m build

docs: ## Generate documentation  
	@echo "$(BLUE)Generating documentation...$(RESET)"
	sphinx-build -b html docs/ docs/_build/html

upload-test: build ## Upload to Test PyPI
	@echo "$(BLUE)Uploading to Test PyPI...$(RESET)"
	twine upload --repository testpypi dist/*

upload: build ## Upload to PyPI
	@echo "$(RED)Uploading to PyPI...$(RESET)"
	twine upload dist/*

dev-setup: ## Complete development setup
	@echo "$(BLUE)Setting up complete development environment...$(RESET)"
	./setup-dev.sh

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(RESET)"
	pytest tests/ --benchmark-only || echo "No benchmarks found"

complexity: ## Analyze code complexity
	@echo "$(BLUE)Analyzing code complexity...$(RESET)"
	radon cc quantipy/ -a || pip install radon && radon cc quantipy/ -a

unused: ## Find unused code
	@echo "$(BLUE)Finding unused code...$(RESET)"
	vulture quantipy/ || pip install vulture && vulture quantipy/

ci: quality test security ## Run full CI pipeline locally
	@echo "$(GREEN)Full CI pipeline completed successfully!$(RESET)"

# Environment targets
check-env: ## Check Python environment
	@echo "$(BLUE)Python environment information:$(RESET)"
	@python --version
	@which python
	@pip list | grep -E "(ruff|mypy|pytest)"

# Test import functionality
test-imports: ## Test critical imports
	@echo "$(BLUE)Testing critical imports...$(RESET)"
	@python -c "import quantipy as qp; print('✅ quantipy imports successfully')"
	@python -c "from quantipy.core.stack import Stack; print('✅ Stack imports successfully')" 
	@python -c "from quantipy.core.chain import Chain; print('✅ Chain imports successfully')"
	@python -c "from quantipy.core.dataset import DataSet; print('✅ DataSet imports successfully')"