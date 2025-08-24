Check Gates Command (Python, with auto-fix)

Run linting, code formatting, and tests on $ARGUMENTS to ensure code quality before committing.
This command enforces the project’s minimum standards and can auto-fix style issues.

⸻

Requisitos (una sola vez, en el venv)

Intérprete recomendado: /Users/jorgealagon/miniforge3_x86/envs/qp_legacy36/bin/python

python -m pip install \
  "flake8==3.9.2" \
  "black==21.12b0" \
  "isort==5.10.1" \
  "pytest==6.2.5" "pytest-cov==2.12.1" "coverage==5.5" \
  "autopep8==1.6.0" "flake8-autopep8==1.1.1" \
  "flake8-docstrings==1.6.0" "pydocstyle==5.1.1"


⸻

Standards

All code must:
	•	Pass Flake8 rules (including docstrings) with zero errors
	•	Match Black + isort formatting
	•	Achieve ≥80% test coverage with pytest-cov
	•	Pass all unit and integration tests

⸻

Process
	1.	Linting (Flake8)

python -m flake8 .


	2.	Autopep8 (auto-fix style issues)

python -m autopep8 --in-place --recursive --aggressive --aggressive .


	3.	Black (format check + auto-fix)
	•	Check:

python -m black --check .


	•	Auto-fix if needed:

python -m black .


	4.	isort (import order check + auto-fix)
	•	Check:

python -m isort --check-only .


	•	Auto-fix if needed:

python -m isort .


	5.	Tests (Pytest + Coverage)

python -m pytest --cov=quantipy --cov-report=term-missing --cov-fail-under=80


	6.	Verification (combined, with auto-fix where possible)

python -m autopep8 --in-place --recursive --aggressive --aggressive . && \
python -m black . && \
python -m isort . && \
python -m flake8 . && \
python -m pytest --cov=quantipy --cov-report=term-missing --cov-fail-under=80



⸻

Output Requirements
	•	Save report as ai-quality-reports/{date}-{branch}.report.md
	•	Include:
	•	Flake8 issues (file + line references)
	•	Autopep8 / Black / isort fixes applied
	•	Test results summary
	•	Coverage percentage
	•	Provide recommendations if thresholds are not met

⸻

Checklist
	•	Flake8 passes with no errors (docstrings checked)
	•	Autopep8 applied (spacing, unused imports, etc.)
	•	Black formatting applied
	•	isort applied
	•	All tests pass locally
	•	Coverage ≥80%
	•	No untracked fixes left in working directory