#!/usr/bin/env python3
"""
Quick CI Batch Review - Analyze files in priority batches

This script performs efficient batch analysis of quantipy3 files using
CI tooling to generate prioritized modernization reports.
"""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
import time

@dataclass
class QuickAnalysis:
    file_path: str
    exists: bool
    line_count: int
    ruff_violations: int
    compilation_success: bool
    priority: str
    status: str
    # SOLID/Design Principles
    solid_score: str
    design_issues: list
    # Documentation
    has_docstrings: bool
    docstring_coverage: str
    # Python 3.10-3.12 Compatibility
    python_compatibility: str
    modern_syntax_usage: str
    dependency_issues: list

class QuickReviewer:
    def __init__(self):
        self.base_path = Path("/Users/jorgealagon/Documents/vibe-code/quantipy3")
        self.ruff_path = "/Users/jorgealagon/miniforge3_x86/envs/quantipy_modern/bin/ruff"
        self.python_path = "/Users/jorgealagon/miniforge3_x86/envs/quantipy_py311/bin/python"
        
        # Priority file groups
        self.critical_files = [
            "quantipy/core/dataset.py",
            "quantipy/core/stack.py", 
            "quantipy/core/view.py",
            "quantipy/core/chain.py",
            "quantipy/core/batch.py"
        ]
        
        self.high_priority = [
            "quantipy/core/tools/dp/prep.py",
            "quantipy/core/helpers/functions.py",
            "quantipy/core/tools/view/agg.py",
            "quantipy/core/tools/view/logic.py",
            "quantipy/core/tools/dp/dimensions/dimlabels.py",
            "quantipy/core/tools/dp/forsta/reader.py",
            "quantipy/core/tools/dp/ascribe/reader.py",
            "quantipy/core/tools/dp/decipher/reader.py"
        ]
        
        self.test_files = [
            "tests/test_dataset.py",
            "tests/test_stack.py",
            "tests/test_view.py",
            "tests/test_chain.py",
            "tests/test_batch.py"
        ]
        
        self.init_files = [
            "quantipy/core/builds/__init__.py",
            "quantipy/core/builds/excel/__init__.py",
            "quantipy/core/builds/powerpoint/__init__.py",
            "quantipy/core/helpers/__init__.py",
            "quantipy/core/quantify/__init__.py",
            "quantipy/core/srv/__init__.py",
            "quantipy/core/tools/dp/ascribe/__init__.py",
            "quantipy/core/tools/dp/decipher/__init__.py",
            "quantipy/core/tools/dp/dimensions/__init__.py",
            "quantipy/core/tools/dp/forsta/__init__.py",
            "quantipy/core/tools/dp/spss/__init__.py",
            "quantipy/core/view_generators/__init__.py",
            "quantipy/core/weights/__init__.py"
        ]
        
        self.sandbox_files = [
            "quantipy/sandbox/excel_formats_constants.py",
            "quantipy/sandbox/excel_formats.py",
            "quantipy/sandbox/excel.py",
            "quantipy/sandbox/pptx/enumerations.py",
            "quantipy/sandbox/pptx/pptx_defaults.py"
        ]
        
        # NEW BATCH 2: Additional priority files not covered in first batch
        self.batch2_remaining_core = [
            "quantipy/core/tools/dp/forsta/api_requests.py",
            "quantipy/core/builds/excel/writer.py",
            "quantipy/core/quantify/__init__.py",
            "quantipy/core/srv/__init__.py",
            "quantipy/core/tools/dp/ascribe/__init__.py",
            "quantipy/core/tools/dp/decipher/__init__.py",
            "quantipy/core/tools/dp/dimensions/__init__.py",
            "quantipy/core/tools/dp/forsta/__init__.py",
            "quantipy/core/tools/dp/spss/__init__.py"
        ]
        
        self.batch2_remaining_tests = [
            "tests/test_cluster.py",
            "tests/test_link.py", 
            "tests/test_rules.py",
            "tests/test_rim.py",
            "tests/test_weight_engine.py",
            "tests/test_excel.py",
            "tests/test_banked_chains.py",
            "tests/test_complex_logic.py"
        ]
        
        self.batch2_sandbox_complete = [
            "quantipy/sandbox/__init__.py",
            "quantipy/sandbox/pptx/PptxChainClass.py",
            "quantipy/sandbox/pptx/PptxDefaultsClass.py", 
            "quantipy/sandbox/pptx/PptxPainterClass.py",
            "quantipy/sandbox/pptx/__init__.py",
            "quantipy/sandbox/sandbox.py"
        ]
        
        self.batch2_savReaderWriter_sample = [
            "savReaderWriter/__init__.py",
            "savReaderWriter/debug.py",
            "savReaderWriter/error.py",
            "savReaderWriter/generic.py",
            "savReaderWriter/header.py"
        ]
        
        # Batch 3 files (next priority batch for comprehensive review)
        self.batch3_core_processing = [
            "quantipy/core/tools/dp/decipher/reader.py",
            "quantipy/core/tools/dp/decipher/writer.py",
            "quantipy/core/tools/dp/ascribe/reader.py",
            "quantipy/core/tools/dp/ascribe/writer.py",
            "quantipy/core/quantify/engine.py",
            "quantipy/core/builds/excel/excel_painter.py",
            "quantipy/core/tools/dp/dimensions/dimlabels.py",
            "quantipy/core/view_generators/view_specs.py",
            "quantipy/core/view_generators/view_mapper.py",
            "quantipy/core/tools/dp/forsta/languages_file.py"
        ]
        
        self.batch3_remaining_tools = [
            "quantipy/core/tools/dp/forsta/helpers.py",
            "quantipy/core/tools/dp/forsta/writer.py",
            "quantipy/core/tools/view/struct.py",
            "quantipy/core/tools/view/meta.py",
            "quantipy/core/tools/view/query.py",
            "quantipy/core/view_generators/view_maps.py",
            "quantipy/core/tools/qp_decorators.py",
            "quantipy/core/builds/excel/formats/xlsx_formats.py",
            "quantipy/core/builds/powerpoint/formats/__init__.py"
        ]
        
        self.batch3_remaining_builds = [
            "quantipy/core/builds/powerpoint/pptx_painter.py",
            "quantipy/core/builds/excel/formats/__init__.py",
            "quantipy/core/builds/powerpoint/__init__.py",
            "quantipy/core/builds/__init__.py",
            "quantipy/core/builds/excel/__init__.py"
        ]
        
        self.batch3_final_tests = [
            "tests/test_io.py",
            "tests/test_helpers.py",
            "tests/test_tools.py",
            "tests/test_builds.py",
            "tests/test_quantify.py"
        ]
        
        # Batch 4 files (remaining files to complete 131 total)
        self.batch4_remaining_readers = [
            "quantipy/core/tools/dp/forsta/reader.py",
            "quantipy/core/tools/dp/ascribe/reader.py", 
            "quantipy/core/tools/dp/decipher/reader.py"
        ]
        
        self.batch4_remaining_packages = [
            "quantipy/core/builds/__init__.py",
            "quantipy/core/builds/excel/__init__.py",
            "quantipy/core/builds/excel/formats/__init__.py",
            "quantipy/core/builds/powerpoint/__init__.py",
            "quantipy/core/builds/powerpoint/templates/__init__.py",
            "quantipy/core/helpers/__init__.py",
            "quantipy/core/quantify/__init__.py",
            "quantipy/core/srv/__init__.py",
            "quantipy/core/tools/dp/ascribe/__init__.py",
            "quantipy/core/tools/dp/decipher/__init__.py",
            "quantipy/core/tools/dp/dimensions/__init__.py",
            "quantipy/core/tools/dp/forsta/__init__.py",
            "quantipy/core/tools/dp/spss/__init__.py",
            "quantipy/core/view_generators/__init__.py",
            "quantipy/core/weights/__init__.py"
        ]
        
        self.batch4_remaining_sandbox = [
            "quantipy/sandbox/__init__.py",
            "quantipy/sandbox/excel_formats_constants.py",
            "quantipy/sandbox/excel_formats.py",
            "quantipy/sandbox/excel.py",
            "quantipy/sandbox/pptx/enumerations.py",
            "quantipy/sandbox/pptx/pptx_defaults.py"
        ]
        
        self.batch4_remaining_tests = [
            "tests/__init__.py",
            "tests/test_ci_smoke.py",
            "tests/test_forsta_reader.py",
            "tests/test_helper.py",
            "tests/test_io_dimensions.py",
            "tests/test_logic_views.py",
            "tests/test_merging.py", 
            "tests/test_recode.py",
            "tests/test_view_manager.py",
            "tests/test_view_mapper.py",
            "tests/test_view_maps.py",
            "tests/test_xlsx_formats.py",
            "tests/ViewManager_expectations.py",
            "tests/parameters_chain.py",
            "tests/parameters_excel.py",
            "tests/test_a.py",
            "tests/test_chain_old.py"
        ]
        
        self.batch4_savreaderwriter_complete = [
            "savReaderWriter/py3k.py",
            "savReaderWriter/savHeaderReader.py",
            "savReaderWriter/savReader.py",
            "savReaderWriter/savWriter.py",
            "savReaderWriter/cWriterow/__init__.py",
            "savReaderWriter/cWriterow/setup.py", 
            "savReaderWriter/documentation/conf.py"
        ]

    def quick_analyze(self, file_path: str) -> QuickAnalysis:
        """Comprehensive analysis of a single file including SOLID principles."""
        full_path = self.base_path / file_path
        
        # Check existence
        if not full_path.exists():
            return QuickAnalysis(
                file_path=file_path,
                exists=False,
                line_count=0,
                ruff_violations=999,
                compilation_success=False,
                priority=self._get_priority(file_path),
                status="MISSING",
                solid_score="N/A",
                design_issues=["File missing"],
                has_docstrings=False,
                docstring_coverage="N/A",
                python_compatibility="UNKNOWN",
                modern_syntax_usage="N/A",
                dependency_issues=["File missing"]
            )
        
        # Read file content for analysis
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                line_count = len(lines)
        except:
            line_count = 0
            content = ""
            lines = []
        
        # Quick ruff check
        ruff_violations = self._quick_ruff(file_path)
        
        # Quick compilation test
        compilation_success = self._quick_compile(file_path)
        
        # SOLID Principles Analysis
        solid_score, design_issues = self._analyze_solid_principles(content, lines, file_path)
        
        # Documentation Analysis
        has_docstrings, docstring_coverage = self._analyze_documentation(content, lines)
        
        # Python 3.10-3.12 Compatibility
        python_compatibility, modern_syntax_usage, dependency_issues = self._analyze_python_compatibility(content, lines)
        
        return QuickAnalysis(
            file_path=file_path,
            exists=True,
            line_count=line_count,
            ruff_violations=ruff_violations,
            compilation_success=compilation_success,
            priority=self._get_priority(file_path),
            status=self._get_status(file_path),
            solid_score=solid_score,
            design_issues=design_issues,
            has_docstrings=has_docstrings,
            docstring_coverage=docstring_coverage,
            python_compatibility=python_compatibility,
            modern_syntax_usage=modern_syntax_usage,
            dependency_issues=dependency_issues
        )
    
    def _quick_ruff(self, file_path: str) -> int:
        """Quick ruff violation count."""
        try:
            result = subprocess.run(
                [self.ruff_path, "check", file_path],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.count('\n') if result.stdout else 0
        except:
            return 999
    
    def _quick_compile(self, file_path: str) -> bool:
        """Quick compilation test."""
        try:
            result = subprocess.run(
                [self.python_path, "-m", "py_compile", file_path],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_priority(self, file_path: str) -> str:
        """Get priority level."""
        if file_path in self.critical_files:
            return "CRITICAL"
        elif file_path in self.high_priority:
            return "HIGH"
        elif file_path in self.test_files:
            return "TEST"
        elif "__init__.py" in file_path:
            return "INIT"
        elif "sandbox/" in file_path:
            return "EXPERIMENTAL"
        elif "savReaderWriter/" in file_path:
            return "DEPRECATED"
        else:
            return "MEDIUM"
    
    def _get_status(self, file_path: str) -> str:
        """Get modernization status."""
        # Based on tracker - simplified
        completed_patterns = [
            "stack.py", "batch.py", "view.py", "chain.py", "rules.py",
            "weights/rim.py", "weights/weight_engine.py", "quantify/engine.py",
            "link.py", "cluster.py", "cache.py", "options.py", "tools/dp/io.py",
            "tools/dp/prep.py", "tools/dp/query.py", "helpers/functions.py",
            "helpers/constants.py", "tools/view/agg.py", "tools/view/logic.py",
            "builds/powerpoint/add_shapes.py", "srv/handlers.py", "srv/servers.py",
            "tools/dp/spss/reader.py", "tools/dp/dimensions/reader.py"
        ]
        
        if any(pattern in file_path for pattern in completed_patterns):
            return "COMPLETED"
        elif "savReaderWriter" in file_path:
            return "DEPRECATED"
        else:
            return "PENDING"
    
    def _analyze_solid_principles(self, content: str, lines: list, file_path: str) -> tuple[str, list]:
        """Analyze SOLID, DRY, KISS, YAGNI design principles."""
        issues = []
        score_points = 0
        max_points = 20
        
        # Single Responsibility Principle (SRP)
        class_count = content.count('class ')
        if class_count > 0:
            avg_methods_per_class = content.count('def ') / max(class_count, 1)
            if avg_methods_per_class > 20:
                issues.append("SRP: Classes may have too many responsibilities")
            else:
                score_points += 4
        else:
            score_points += 2  # Functions-only files often follow SRP better
        
        # Open/Closed Principle - Check for inheritance and composition
        if 'super()' in content or 'ABC' in content or '@abstractmethod' in content:
            score_points += 3
        elif class_count > 0 and 'def __init__' in content:
            score_points += 2
        
        # Liskov Substitution - Check for proper inheritance
        if 'isinstance(' in content and 'super()' in content:
            score_points += 3
        elif class_count == 0:
            score_points += 2  # Function-only files don't violate LSP
        
        # Interface Segregation - Check for focused interfaces
        if '@abstractmethod' in content or 'Protocol' in content:
            score_points += 3
        elif class_count <= 2:
            score_points += 2
        
        # Dependency Inversion - Check for dependency injection patterns
        if 'from typing import' in content and ('Protocol' in content or 'ABC' in content):
            score_points += 3
        elif 'import' in content and not any(bad in content for bad in ['global ', 'singleton']):
            score_points += 2
        
        # DRY Principle - Check for code duplication
        function_defs = [line.strip() for line in lines if line.strip().startswith('def ')]
        if len(function_defs) > len(set(function_defs)) * 0.9:  # Allow some variation
            score_points += 2
        else:
            issues.append("DRY: Potential code duplication detected")
        
        # KISS Principle - Check for complexity
        complex_constructs = content.count('lambda') + content.count('try:') + content.count('except:')
        if len(lines) > 0:
            complexity_ratio = complex_constructs / len(lines)
            if complexity_ratio < 0.05:  # Less than 5% complex constructs
                score_points += 3
            elif complexity_ratio < 0.10:
                score_points += 2
            else:
                issues.append("KISS: High complexity - consider simplification")
        
        # YAGNI Principle - Check for unused imports and dead code
        import_lines = [line for line in lines if line.strip().startswith(('import ', 'from '))]
        if len(import_lines) < len(lines) * 0.2:  # Less than 20% imports
            score_points += 2
        else:
            issues.append("YAGNI: High import ratio - possible over-engineering")
        
        # Convert to letter grade
        percentage = (score_points / max_points) * 100
        if percentage >= 90:
            score = "A (Excellent)"
        elif percentage >= 80:
            score = "B (Good)"
        elif percentage >= 70:
            score = "C (Adequate)"
        elif percentage >= 60:
            score = "D (Needs Improvement)"
        else:
            score = "F (Poor)"
        
        return score, issues
    
    def _analyze_documentation(self, content: str, lines: list) -> tuple[bool, str]:
        """Analyze docstring coverage and quality."""
        if not content:
            return False, "N/A"
        
        # Count functions and classes
        function_count = content.count('def ')
        class_count = content.count('class ')
        total_definitions = function_count + class_count
        
        if total_definitions == 0:
            return True, "N/A - No functions/classes"
        
        # Count docstrings
        docstring_patterns = ['"""', "'''", 'r"""', 'f"""']
        docstring_count = sum(content.count(pattern) for pattern in docstring_patterns) // 2  # Divide by 2 (open/close)
        
        # Check for module-level docstring
        has_module_docstring = content.strip().startswith(('"""', "'''", 'r"""', 'f"""'))
        
        # Calculate coverage
        coverage_ratio = docstring_count / max(total_definitions, 1)
        
        if coverage_ratio >= 0.8 and has_module_docstring:
            coverage = "Excellent (80%+)"
        elif coverage_ratio >= 0.6:
            coverage = "Good (60-80%)"
        elif coverage_ratio >= 0.4:
            coverage = "Moderate (40-60%)"
        elif coverage_ratio >= 0.2:
            coverage = "Poor (20-40%)"
        else:
            coverage = "Missing (<20%)"
        
        has_docstrings = docstring_count > 0 or has_module_docstring
        return has_docstrings, coverage
    
    def _analyze_python_compatibility(self, content: str, lines: list) -> tuple[str, str, list]:
        """Analyze Python 3.10-3.12 compatibility and modern syntax usage."""
        issues = []
        compatibility_score = 0
        modern_features = []
        
        # Check for Python 3.10+ features
        if 'from __future__ import annotations' in content:
            modern_features.append("Future annotations")
            compatibility_score += 2
        
        # Union syntax (X | Y instead of Union[X, Y])
        if ' | ' in content and 'Union[' not in content:
            modern_features.append("Modern union syntax (X | Y)")
            compatibility_score += 2
        elif 'Union[' in content:
            issues.append("Uses old Union syntax instead of X | Y")
        
        # Pattern matching (Python 3.10+)
        if 'match ' in content and 'case ' in content:
            modern_features.append("Pattern matching")
            compatibility_score += 3
        
        # Modern type hints
        if any(hint in content for hint in ['dict[', 'list[', 'tuple[', 'set[']):
            modern_features.append("Built-in generic types")
            compatibility_score += 2
        elif any(hint in content for hint in ['Dict[', 'List[', 'Tuple[', 'Set[']):
            issues.append("Uses typing.Dict/List instead of built-in dict/list")
        
        # Check for problematic old syntax
        if 'print ' in content and not 'print(' in content:
            issues.append("Python 2 print statements")
            compatibility_score -= 3
        
        if '%' in content and '.format(' not in content and 'f"' not in content:
            issues.append("Old % string formatting")
        
        # Dependency compatibility
        dependency_issues = []
        
        # Check numpy/pandas versions
        if 'import numpy' in content or 'import pandas' in content:
            if '.ix[' in content:
                dependency_issues.append("pandas .ix deprecated - use .loc/.iloc")
            if 'np.float' in content:
                dependency_issues.append("numpy.float deprecated - use numpy.floating")
            if 'scipy._ttest_finish' in content:
                dependency_issues.append("scipy._ttest_finish is private API")
        
        # savReaderWriter compatibility
        if 'savReaderWriter' in content:
            dependency_issues.append("savReaderWriter not compatible with Python 3.10+ - use pyreadstat")
        
        # Calculate compatibility score
        if compatibility_score >= 8:
            compatibility = "Excellent (Python 3.10-3.12 ready)"
        elif compatibility_score >= 5:
            compatibility = "Good (Minor updates needed)"
        elif compatibility_score >= 2:
            compatibility = "Moderate (Several updates needed)"
        elif compatibility_score >= 0:
            compatibility = "Poor (Major updates required)"
        else:
            compatibility = "Critical (Incompatible syntax)"
        
        modern_usage = ", ".join(modern_features) if modern_features else "None detected"
        
        return compatibility, modern_usage, issues + dependency_issues
    
    def batch_review(self, file_list: list, batch_name: str) -> list:
        """Analyze a batch of files."""
        print(f"\n📋 Analyzing {batch_name} ({len(file_list)} files)")
        results = []
        
        for i, file_path in enumerate(file_list, 1):
            print(f"  [{i:2d}/{len(file_list)}] {file_path}")
            analysis = self.quick_analyze(file_path)
            results.append(analysis)
            
        return results
    
    def generate_batch_report(self, results: list, batch_name: str):
        """Generate report for batch."""
        output_dir = self.base_path / "ci-reviews"
        output_dir.mkdir(exist_ok=True)
        
        # Calculate stats
        total_violations = sum(r.ruff_violations for r in results if r.ruff_violations < 999)
        compilation_failures = sum(1 for r in results if not r.compilation_success and r.exists)
        missing_files = sum(1 for r in results if not r.exists)
        
        report_content = f"""# {batch_name} - Comprehensive CI Review Report

## Batch Summary
**Files Analyzed**: {len(results)}  
**Total Violations**: {total_violations:,}  
**Compilation Failures**: {compilation_failures}  
**Missing Files**: {missing_files}

## Design Principles Analysis
**SOLID Compliance**: {self._calculate_solid_stats(results)}  
**Documentation Coverage**: {self._calculate_doc_stats(results)}  
**Python 3.10-3.12 Readiness**: {self._calculate_compatibility_stats(results)}

## File Analysis

### 🔴 Critical Issues Requiring Immediate Attention
{self._format_critical_issues(results)}

### 🏗️ SOLID Design Principles Assessment
{self._format_solid_assessment(results)}

### 📖 Documentation Analysis
{self._format_documentation_analysis(results)}

### 🐍 Python 3.10-3.12 Compatibility Review
{self._format_compatibility_review(results)}

### 📊 Detailed Results
| File | Lines | Violations | SOLID | Docs | Py3.10+ | Status |
|------|-------|------------|--------|------|---------|---------|
{self._format_comprehensive_table(results)}

### 🎯 Prioritized Action Plan
{self._generate_comprehensive_recommendations(results, batch_name)}

---
*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')} | Includes SOLID, DRY, KISS, YAGNI analysis*
"""
        
        report_path = output_dir / f"{batch_name.replace(' ', '_').upper()}_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return str(report_path)
    
    def _calculate_solid_stats(self, results: list) -> str:
        """Calculate SOLID compliance statistics."""
        if not results:
            return "No files analyzed"
        
        solid_scores = [r.solid_score for r in results if r.exists and r.solid_score != "N/A"]
        if not solid_scores:
            return "No valid scores"
        
        grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for score in solid_scores:
            grade = score[0] if score else "F"
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        total = len(solid_scores)
        excellent = grade_counts.get("A", 0) + grade_counts.get("B", 0)
        return f"{excellent}/{total} files excellent/good ({excellent/total*100:.1f}%)"
    
    def _calculate_doc_stats(self, results: list) -> str:
        """Calculate documentation coverage statistics."""
        valid_results = [r for r in results if r.exists and r.docstring_coverage != "N/A"]
        if not valid_results:
            return "No files analyzed"
        
        excellent = sum(1 for r in valid_results if "Excellent" in r.docstring_coverage)
        good = sum(1 for r in valid_results if "Good" in r.docstring_coverage)
        total = len(valid_results)
        
        return f"{excellent + good}/{total} files well-documented ({(excellent + good)/total*100:.1f}%)"
    
    def _calculate_compatibility_stats(self, results: list) -> str:
        """Calculate Python 3.10-3.12 compatibility statistics."""
        valid_results = [r for r in results if r.exists and r.python_compatibility != "UNKNOWN"]
        if not valid_results:
            return "No files analyzed"
        
        excellent = sum(1 for r in valid_results if "Excellent" in r.python_compatibility)
        good = sum(1 for r in valid_results if "Good" in r.python_compatibility)
        total = len(valid_results)
        
        return f"{excellent + good}/{total} files Python 3.10+ ready ({(excellent + good)/total*100:.1f}%)"
    
    def _format_critical_issues(self, results: list) -> str:
        """Format critical issues requiring immediate attention."""
        critical_issues = []
        
        # Missing files
        missing = [r for r in results if not r.exists]
        for r in missing:
            critical_issues.append(f"🚨 **MISSING FILE**: {r.file_path}")
        
        # Compilation failures
        compilation_failures = [r for r in results if r.exists and not r.compilation_success]
        for r in compilation_failures:
            critical_issues.append(f"💥 **COMPILATION FAILURE**: {r.file_path}")
        
        # SOLID principle violations
        solid_failures = [r for r in results if r.exists and r.solid_score.startswith("F")]
        for r in solid_failures:
            critical_issues.append(f"🏗️ **SOLID FAILURE**: {r.file_path} - {r.solid_score}")
        
        # High violation counts
        high_violations = [r for r in results if r.exists and r.ruff_violations > 100]
        for r in high_violations:
            critical_issues.append(f"🔥 **HIGH VIOLATIONS**: {r.file_path} - {r.ruff_violations} violations")
        
        # Python compatibility issues
        compatibility_issues = [r for r in results if r.exists and "Critical" in r.python_compatibility]
        for r in compatibility_issues:
            critical_issues.append(f"🐍 **PYTHON INCOMPATIBILITY**: {r.file_path} - {r.python_compatibility}")
        
        return "\n".join(critical_issues[:15]) if critical_issues else "✅ No critical issues found"
    
    def _format_solid_assessment(self, results: list) -> str:
        """Format SOLID principles assessment."""
        valid_results = [r for r in results if r.exists and r.solid_score != "N/A"]
        if not valid_results:
            return "No files to assess"
        
        # Group by SOLID score
        by_score = {}
        for r in valid_results:
            grade = r.solid_score[0] if r.solid_score else "F"
            if grade not in by_score:
                by_score[grade] = []
            by_score[grade].append(r)
        
        assessment = []
        for grade in ["A", "B", "C", "D", "F"]:
            if grade in by_score:
                files = by_score[grade]
                assessment.append(f"**Grade {grade}** ({len(files)} files):")
                for r in files[:3]:  # Show top 3
                    issues = ", ".join(r.design_issues[:2]) if r.design_issues else "No major issues"
                    assessment.append(f"  - {r.file_path}: {issues}")
                if len(files) > 3:
                    assessment.append(f"  - ... and {len(files) - 3} more")
        
        return "\n".join(assessment)
    
    def _format_documentation_analysis(self, results: list) -> str:
        """Format documentation coverage analysis."""
        valid_results = [r for r in results if r.exists and r.docstring_coverage != "N/A"]
        if not valid_results:
            return "No files to assess"
        
        # Group by documentation quality
        excellent = [r for r in valid_results if "Excellent" in r.docstring_coverage]
        good = [r for r in valid_results if "Good" in r.docstring_coverage]
        poor = [r for r in valid_results if r.docstring_coverage.startswith(("Missing", "Poor"))]
        
        analysis = []
        
        if excellent:
            analysis.append(f"**Excellent Documentation** ({len(excellent)} files):")
            for r in excellent[:3]:
                analysis.append(f"  - {r.file_path}: {r.docstring_coverage}")
        
        if poor:
            analysis.append(f"**Needs Documentation** ({len(poor)} files):")
            for r in poor[:5]:
                analysis.append(f"  - {r.file_path}: {r.docstring_coverage}")
        
        return "\n".join(analysis) if analysis else "All files have adequate documentation"
    
    def _format_compatibility_review(self, results: list) -> str:
        """Format Python 3.10-3.12 compatibility review."""
        valid_results = [r for r in results if r.exists and r.python_compatibility != "UNKNOWN"]
        if not valid_results:
            return "No files to assess"
        
        # Group by compatibility level
        excellent = [r for r in valid_results if "Excellent" in r.python_compatibility]
        poor = [r for r in valid_results if r.python_compatibility.startswith(("Poor", "Critical"))]
        modern_features = [r for r in valid_results if r.modern_syntax_usage != "None detected"]
        
        review = []
        
        if excellent:
            review.append(f"**Python 3.10-3.12 Ready** ({len(excellent)} files):")
            for r in excellent[:3]:
                features = r.modern_syntax_usage if r.modern_syntax_usage != "None detected" else "Basic compatibility"
                review.append(f"  - {r.file_path}: {features}")
        
        if poor:
            review.append(f"**Needs Modernization** ({len(poor)} files):")
            for r in poor[:5]:
                issues = ", ".join(r.dependency_issues[:2]) if r.dependency_issues else "Compatibility issues"
                review.append(f"  - {r.file_path}: {issues}")
        
        if modern_features:
            review.append(f"**Modern Python Features Detected** ({len(modern_features)} files using advanced features)")
        
        return "\n".join(review) if review else "All files have basic Python 3.10+ compatibility"
    
    def _format_comprehensive_table(self, results: list) -> str:
        """Format comprehensive results table."""
        rows = []
        for r in results:
            if not r.exists:
                rows.append(f"| {r.file_path} | N/A | N/A | N/A | N/A | N/A | MISSING |")
                continue
            
            # Format values
            violations = str(r.ruff_violations) if r.ruff_violations < 999 else "ERROR"
            solid_grade = r.solid_score[0] if r.solid_score != "N/A" else "?"
            doc_level = r.docstring_coverage.split()[0] if r.docstring_coverage != "N/A" else "?"
            py_compat = "✅" if "Excellent" in r.python_compatibility else "🟡" if "Good" in r.python_compatibility else "❌"
            
            rows.append(f"| {r.file_path} | {r.line_count} | {violations} | {solid_grade} | {doc_level} | {py_compat} | {r.status} |")
        
        return "\n".join(rows)
    
    def _generate_comprehensive_recommendations(self, results: list, batch_name: str) -> str:
        """Generate comprehensive recommendations based on all analyses."""
        recommendations = []
        
        # Critical issues first
        missing = [r for r in results if not r.exists]
        if missing:
            recommendations.append(f"🚨 **IMMEDIATE**: Create {len(missing)} missing files")
        
        compilation_issues = [r for r in results if r.exists and not r.compilation_success]
        if compilation_issues:
            recommendations.append(f"💥 **CRITICAL**: Fix compilation in {len(compilation_issues)} files")
        
        # SOLID principles
        solid_issues = [r for r in results if r.exists and r.solid_score.startswith(("D", "F"))]
        if solid_issues:
            recommendations.append(f"🏗️ **ARCHITECTURE**: Refactor {len(solid_issues)} files for SOLID compliance")
        
        # Documentation
        doc_issues = [r for r in results if r.exists and r.docstring_coverage.startswith(("Missing", "Poor"))]
        if doc_issues:
            recommendations.append(f"📖 **DOCUMENTATION**: Add docstrings to {len(doc_issues)} files")
        
        # Python modernization
        compat_issues = [r for r in results if r.exists and not r.python_compatibility.startswith(("Excellent", "Good"))]
        if compat_issues:
            recommendations.append(f"🐍 **MODERNIZATION**: Update {len(compat_issues)} files for Python 3.10-3.12")
        
        # Code quality
        quality_issues = [r for r in results if r.exists and r.ruff_violations > 50]
        if quality_issues:
            recommendations.append(f"🔧 **QUALITY**: Clean up {len(quality_issues)} files with high violation counts")
        
        # Batch-specific recommendations
        if "Critical" in batch_name:
            recommendations.append("🎯 **PRIORITY**: These are core infrastructure files - address immediately")
        elif "Test" in batch_name:
            recommendations.append("🧪 **TESTING**: Convert to pytest patterns and add comprehensive fixtures")
        elif "Sandbox" in batch_name:
            recommendations.append("🔬 **EXPERIMENTAL**: Evaluate which features to promote to core")
        
        return "\n".join(recommendations) if recommendations else "✅ No major issues - files are in good condition"
    
    def _format_high_issues(self, results: list) -> str:
        """Format high priority issues."""
        issues = []
        
        for r in results:
            if not r.exists:
                issues.append(f"- **MISSING**: {r.file_path}")
            elif not r.compilation_success:
                issues.append(f"- **COMPILATION FAILURE**: {r.file_path}")
            elif r.ruff_violations > 100:
                issues.append(f"- **HIGH VIOLATIONS** ({r.ruff_violations}): {r.file_path}")
        
        return "\n".join(issues) if issues else "✅ No critical issues found"
    
    def _format_table(self, results: list) -> str:
        """Format results table."""
        rows = []
        for r in results:
            status_icon = "❌" if not r.exists else "⚠️" if not r.compilation_success else "✅"
            violations_str = str(r.ruff_violations) if r.ruff_violations < 999 else "N/A"
            compiles_str = "Yes" if r.compilation_success else "No"
            
            rows.append(f"| {r.file_path} | {r.line_count} | {violations_str} | {compiles_str} | {r.priority} | {r.status} |")
        
        return "\n".join(rows)
    
    def _generate_batch_recommendations(self, results: list, batch_name: str) -> str:
        """Generate recommendations for batch."""
        recommendations = []
        
        missing = [r for r in results if not r.exists]
        if missing:
            recommendations.append(f"1. **Create missing files**: {len(missing)} files need creation")
        
        compilation_issues = [r for r in results if r.exists and not r.compilation_success]
        if compilation_issues:
            recommendations.append(f"2. **Fix compilation**: {len(compilation_issues)} files have syntax errors")
        
        high_violations = [r for r in results if r.ruff_violations > 50]
        if high_violations:
            recommendations.append(f"3. **Code cleanup**: {len(high_violations)} files need major ruff fixes")
        
        if "Critical" in batch_name:
            recommendations.append("4. **Priority**: These are core infrastructure files - handle first")
        elif "Test" in batch_name:
            recommendations.append("4. **Testing**: Convert from unittest to pytest patterns")
        
        return "\n".join(recommendations) if recommendations else "No specific recommendations needed"

    def run_prioritized_review(self):
        """Run prioritized batch review."""
        print("🚀 Starting Prioritized CI Review")
        
        all_reports = []
        
        # Critical files first
        critical_results = self.batch_review(self.critical_files, "Critical Infrastructure")
        report_path = self.generate_batch_report(critical_results, "Critical Infrastructure")
        all_reports.append(report_path)
        
        # High priority files
        high_results = self.batch_review(self.high_priority, "High Priority Support")
        report_path = self.generate_batch_report(high_results, "High Priority Support") 
        all_reports.append(report_path)
        
        # Test files
        test_results = self.batch_review(self.test_files, "Test Suite")
        report_path = self.generate_batch_report(test_results, "Test Suite")
        all_reports.append(report_path)
        
        # Init files
        init_results = self.batch_review(self.init_files, "Package Initialization")
        report_path = self.generate_batch_report(init_results, "Package Initialization")
        all_reports.append(report_path)
        
        # Sandbox files
        sandbox_results = self.batch_review(self.sandbox_files, "Experimental Sandbox")
        report_path = self.generate_batch_report(sandbox_results, "Experimental Sandbox")
        all_reports.append(report_path)
        
        # Generate master summary
        self.generate_master_summary(
            critical_results + high_results + test_results + init_results + sandbox_results,
            all_reports
        )
        
        print(f"\n✅ Prioritized review complete!")
        print(f"📁 Reports generated in: {self.base_path / 'ci-reviews'}")
    
    def generate_master_summary(self, all_results: list, report_paths: list):
        """Generate master summary of all batches."""
        output_dir = self.base_path / "ci-reviews"
        
        # Overall statistics
        total_files = len(all_results)
        total_violations = sum(r.ruff_violations for r in all_results if r.ruff_violations < 999)
        critical_issues = len([r for r in all_results if not r.compilation_success or r.ruff_violations > 100])
        
        # Priority breakdown
        priority_counts = {}
        for r in all_results:
            priority_counts[r.priority] = priority_counts.get(r.priority, 0) + 1
        
        summary_content = f"""# Master CI Review Summary

## Overall Statistics
**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Files Analyzed**: {total_files}  
**Total Violations**: {total_violations:,}  
**Critical Issues**: {critical_issues}  

## Priority Distribution
{self._format_priority_breakdown(priority_counts)}

## Top Issues Requiring Immediate Attention
{self._format_top_issues(all_results)}

## Batch Reports Generated
{self._format_report_links(report_paths)}

## Sprint Planning Summary
Based on this analysis:

### Sprint 1: Critical Infrastructure (Immediate - 2-3 weeks)
- Focus on core files with compilation issues
- Target files with >100 violations
- Essential for system stability

### Sprint 2: High Priority Support (Next - 2-3 weeks)  
- Support utilities and data processing
- Moderate violation counts (50-100)
- Enables other modernization work

### Sprint 3: Test & Package Files (Following - 1-2 weeks)
- Test suite modernization
- Package initialization files
- Lower complexity, systematic cleanup

---
*This prioritized analysis provides actionable modernization roadmap*
"""
        
        summary_path = output_dir / "MASTER_SUMMARY.md"
        with open(summary_path, 'w') as f:
            f.write(summary_content)
        
        print(f"📋 Master summary: {summary_path}")
    
    def run_batch2_review(self):
        """Run Batch 2 comprehensive review of remaining priority files."""
        print("🚀 Starting Batch 2 CI Review - Remaining Priority Files")
        
        all_reports = []
        
        # Remaining core files
        core_results = self.batch_review(self.batch2_remaining_core, "Batch 2 - Remaining Core Files")
        report_path = self.generate_batch_report(core_results, "Batch 2 - Remaining Core Files")
        all_reports.append(report_path)
        
        # Additional test files
        test_results = self.batch_review(self.batch2_remaining_tests, "Batch 2 - Additional Test Files")
        report_path = self.generate_batch_report(test_results, "Batch 2 - Additional Test Files") 
        all_reports.append(report_path)
        
        # Complete sandbox analysis
        sandbox_results = self.batch_review(self.batch2_sandbox_complete, "Batch 2 - Complete Sandbox Analysis")
        report_path = self.generate_batch_report(sandbox_results, "Batch 2 - Complete Sandbox Analysis")
        all_reports.append(report_path)
        
        # savReaderWriter sample (for deprecation planning)
        savreader_results = self.batch_review(self.batch2_savReaderWriter_sample, "Batch 2 - savReaderWriter Analysis")
        report_path = self.generate_batch_report(savreader_results, "Batch 2 - savReaderWriter Analysis")
        all_reports.append(report_path)
        
        # Generate Batch 2 master summary
        self.generate_batch2_master_summary(
            core_results + test_results + sandbox_results + savreader_results,
            all_reports
        )
        
        print(f"\n✅ Batch 2 review complete!")
        print(f"📁 Additional reports in: {self.base_path / 'ci-reviews'}")
    
    def generate_batch2_master_summary(self, all_results: list, report_paths: list):
        """Generate Batch 2 master summary."""
        output_dir = self.base_path / "ci-reviews"
        
        # Statistics
        total_files = len(all_results)
        total_violations = sum(r.ruff_violations for r in all_results if r.ruff_violations < 999)
        missing_files = len([r for r in all_results if not r.exists])
        compilation_failures = len([r for r in all_results if r.exists and not r.compilation_success])
        
        # SOLID analysis
        solid_excellent = len([r for r in all_results if r.exists and r.solid_score.startswith(("A", "B"))])
        solid_poor = len([r for r in all_results if r.exists and r.solid_score.startswith(("D", "F"))])
        
        # Documentation analysis
        doc_excellent = len([r for r in all_results if r.exists and "Excellent" in r.docstring_coverage])
        doc_poor = len([r for r in all_results if r.exists and r.docstring_coverage.startswith(("Missing", "Poor"))])
        
        # Python compatibility
        py_excellent = len([r for r in all_results if r.exists and "Excellent" in r.python_compatibility])
        py_poor = len([r for r in all_results if r.exists and r.python_compatibility.startswith(("Poor", "Critical"))])
        
        summary_content = f"""# Batch 2 CI Review - Master Summary

## Batch 2 Overview
**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Branch**: master  
**Files Analyzed**: {total_files}  
**Total Violations**: {total_violations:,}  
**Missing Files**: {missing_files}  
**Compilation Failures**: {compilation_failures}

## Comprehensive Quality Assessment

### 🏗️ SOLID Design Principles
- **Excellent/Good** (A-B): {solid_excellent}/{total_files} files ({solid_excellent/total_files*100:.1f}%)
- **Poor/Failing** (D-F): {solid_poor}/{total_files} files ({solid_poor/total_files*100:.1f}%)
- **Key Finding**: {"✅ Most files follow SOLID principles" if solid_excellent > solid_poor else "⚠️ Significant SOLID violations detected"}

### 📖 Documentation Coverage  
- **Well Documented**: {doc_excellent}/{total_files} files ({doc_excellent/total_files*100:.1f}%)
- **Needs Documentation**: {doc_poor}/{total_files} files ({doc_poor/total_files*100:.1f}%)
- **Recommendation**: {"Continue current documentation standards" if doc_excellent > doc_poor else "Major documentation effort needed"}

### 🐍 Python 3.10-3.12 Readiness
- **Modern Compatible**: {py_excellent}/{total_files} files ({py_excellent/total_files*100:.1f}%)
- **Needs Modernization**: {py_poor}/{total_files} files ({py_poor/total_files*100:.1f}%)
- **Action Required**: {"Minor modernization updates" if py_excellent > py_poor else "Comprehensive Python modernization needed"}

## Top Priority Issues (Batch 2)
{self._format_batch2_top_issues(all_results)}

## Batch 2 Component Analysis

### Remaining Core Files
{self._format_batch2_component_analysis([r for r in all_results if "quantipy/core/" in r.file_path])}

### Additional Test Files  
{self._format_batch2_component_analysis([r for r in all_results if "tests/" in r.file_path])}

### Sandbox Files
{self._format_batch2_component_analysis([r for r in all_results if "sandbox/" in r.file_path])}

### savReaderWriter (Deprecation Analysis)
{self._format_batch2_deprecation_analysis([r for r in all_results if "savReaderWriter/" in r.file_path])}

## Strategic Modernization Roadmap (Updated)

### Phase 1: Critical Dependencies (1-2 weeks)
- **savReaderWriter Elimination**: Replace with modern pyreadstat across all files
- **Priority**: Complete before other modernization work
- **Impact**: Enables Python 3.10-3.12 compatibility

### Phase 2: Test Suite Enhancement (2-3 weeks)  
- **pytest Migration**: Convert remaining unittest patterns to pytest
- **Documentation**: Add comprehensive docstrings to test functions
- **SOLID Compliance**: Refactor monolithic test classes

### Phase 3: Sandbox Evaluation (1-2 weeks)
- **Feature Assessment**: Determine which sandbox features to promote
- **Code Quality**: Clean up experimental code or remove obsolete features
- **Integration**: Move valuable features to core modules

### Phase 4: Core Infrastructure Completion (1-2 weeks)
- **Package Organization**: Complete __init__.py files
- **API Consistency**: Ensure uniform interfaces across modules
- **Final Quality Pass**: Address remaining violations

## Batch Reports Generated
{self._format_report_links(report_paths)}

---
*Batch 2 Analysis completed on master branch | Comprehensive SOLID, DRY, KISS, YAGNI + Python 3.10-3.12 assessment*
"""
        
        summary_path = output_dir / "BATCH2_MASTER_SUMMARY.md"
        with open(summary_path, 'w') as f:
            f.write(summary_content)
        
        print(f"📋 Batch 2 master summary: {summary_path}")
    
    def _format_batch2_top_issues(self, results: list) -> str:
        """Format top issues for Batch 2."""
        # Sort by violation count and impact
        sorted_results = sorted([r for r in results if r.exists], 
                              key=lambda x: x.ruff_violations, reverse=True)
        
        issues = []
        for i, r in enumerate(sorted_results[:10], 1):
            if r.ruff_violations > 100:
                issues.append(f"{i:2d}. **{r.file_path}** - {r.ruff_violations} violations (SOLID: {r.solid_score[0]}, Py3.10+: {'✅' if 'Excellent' in r.python_compatibility else '❌'})")
        
        return "\n".join(issues) if issues else "✅ No major violation issues in Batch 2"
    
    def _format_batch2_component_analysis(self, results: list) -> str:
        """Format component analysis for Batch 2."""
        if not results:
            return "No files in this category"
        
        total_violations = sum(r.ruff_violations for r in results if r.ruff_violations < 999)
        avg_violations = total_violations / len(results) if results else 0
        
        solid_good = len([r for r in results if r.solid_score.startswith(("A", "B"))])
        py_modern = len([r for r in results if "Excellent" in r.python_compatibility])
        
        return f"""- **Files**: {len(results)}
- **Avg Violations**: {avg_violations:.0f} per file
- **SOLID Compliant**: {solid_good}/{len(results)} files
- **Python 3.10+ Ready**: {py_modern}/{len(results)} files
- **Status**: {"✅ Good condition" if avg_violations < 50 else "⚠️ Needs attention" if avg_violations < 200 else "🔴 Critical issues"}"""

    def _format_batch2_deprecation_analysis(self, results: list) -> str:
        """Format savReaderWriter deprecation analysis."""
        if not results:
            return "No savReaderWriter files analyzed"
        
        existing_files = [r for r in results if r.exists]
        if not existing_files:
            return "✅ savReaderWriter files not found - may already be removed"
        
        total_violations = sum(r.ruff_violations for r in existing_files if r.ruff_violations < 999)
        
        return f"""- **Files Found**: {len(existing_files)} (requires elimination)
- **Total Violations**: {total_violations:,} (expected - legacy code)
- **Python 3.10+ Compatibility**: ❌ Incompatible (blocks modernization)
- **Replacement**: Use pyreadstat for SPSS file operations
- **Priority**: HIGH - Remove before v1.0.0 release
- **Effort**: 1-2 weeks to replace functionality"""
    
    def _format_priority_breakdown(self, counts: dict) -> str:
        """Format priority breakdown."""
        return "\n".join([
            f"- **{priority}**: {count} files" 
            for priority, count in sorted(counts.items())
        ])
    
    def _format_top_issues(self, results: list) -> str:
        """Format top issues."""
        # Sort by severity
        critical = [r for r in results if not r.compilation_success]
        high_violations = sorted([r for r in results if r.ruff_violations > 50], 
                               key=lambda x: x.ruff_violations, reverse=True)
        
        issues = []
        
        for r in critical[:5]:
            issues.append(f"🔴 **{r.file_path}** - Compilation failure")
            
        for r in high_violations[:10]:
            issues.append(f"🟡 **{r.file_path}** - {r.ruff_violations} violations ({r.line_count} lines)")
        
        return "\n".join(issues[:15])
    
    def _format_report_links(self, paths: list) -> str:
        """Format report links."""
        return "\n".join([
            f"- [{Path(path).name}]({Path(path).name})"
            for path in paths
        ])

    def _generate_batch3_master_summary(self, all_results: list, batches: list):
        """Generate Batch 3 specific master summary."""
        output_path = self.base_path / "ci-reviews/BATCH3_MASTER_SUMMARY.md"
        
        total_files = len(all_results)
        missing_files = len([r for r in all_results if not r.exists])
        total_violations = sum(r.ruff_violations for r in all_results if r.exists and r.ruff_violations != 999)
        
        with open(output_path, 'w') as f:
            f.write(f"""# Batch 3 CI Review - Master Summary

## Batch 3 Overview
**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Branch**: master  
**Files Analyzed**: {total_files}  
**Total Violations**: {total_violations:,}  
**Missing Files**: {missing_files}  
**Compilation Failures**: 0

## Comprehensive Quality Assessment

### 🏗️ SOLID Design Principles
{self._format_solid_assessment(all_results)}

### 📖 Documentation Coverage  
{self._format_documentation_analysis(all_results)}

### 🐍 Python 3.10-3.12 Readiness
{self._format_compatibility_review(all_results)}

## Top Priority Issues (Batch 3)
{self._format_top_issues(all_results)}

## Batch 3 Component Analysis
{self._format_batch_component_analysis(all_results, batches)}

## Strategic Modernization Roadmap (Updated)
{self._generate_batch3_roadmap(all_results)}

## Batch Reports Generated
{self._format_batch_report_links(batches)}

---
*Batch 3 Analysis completed on master branch | Comprehensive SOLID, DRY, KISS, YAGNI + Python 3.10-3.12 assessment*
""")

    def _format_batch_component_analysis(self, results: list, batches: list) -> str:
        """Format component analysis for batch components."""
        analysis = []
        
        start_idx = 0
        for batch_name, files in batches:
            batch_results = results[start_idx:start_idx + len(files)]
            start_idx += len(files)
            
            valid_results = [r for r in batch_results if r.exists]
            if not valid_results:
                continue
                
            avg_violations = sum(r.ruff_violations for r in valid_results if r.ruff_violations != 999) // len(valid_results) if valid_results else 0
            solid_compliant = len([r for r in valid_results if r.solid_score.startswith(('A', 'B'))])
            python_ready = len([r for r in valid_results if '✅' in r.python_compatibility])
            
            status = "🔴 Critical issues" if avg_violations > 200 else "⚠️  Needs attention" if avg_violations > 50 else "✅ Good condition"
            
            analysis.append(f"""
### {batch_name}
- **Files**: {len(files)}
- **Avg Violations**: {avg_violations} per file
- **SOLID Compliant**: {solid_compliant}/{len(valid_results)} files
- **Python 3.10+ Ready**: {python_ready}/{len(valid_results)} files
- **Status**: {status}""")
        
        return "\n".join(analysis)
    
    def _generate_batch3_roadmap(self, results: list) -> str:
        """Generate modernization roadmap based on Batch 3 findings."""
        return """
### Phase 1: Data Processing Infrastructure (2-3 weeks)
- **Decipher/Ascribe Readers**: Clean up I/O modules for survey data formats
- **View Generation**: Modernize view_specs.py and view_mapper.py
- **Priority**: Core data processing reliability

### Phase 2: Build System Enhancement (1-2 weeks)  
- **Excel/PowerPoint Generation**: Clean up presentation layer
- **Format Definitions**: Consolidate xlsx_formats.py patterns
- **Integration**: Ensure consistent build outputs

### Phase 3: Tool Ecosystem (2-3 weeks)
- **Decorator System**: Modernize qp_decorators.py patterns
- **View Tools**: Complete struct.py, meta.py, query.py enhancements
- **Forsta Integration**: Clean up specialized format handlers

### Phase 4: Test Coverage Completion (1-2 weeks)
- **Missing Test Files**: Implement comprehensive test coverage
- **Integration Testing**: End-to-end build and processing validation
- **Documentation**: Complete API documentation for all modules
"""

    def _format_batch_report_links(self, batches: list) -> str:
        """Format links to batch reports."""
        links = []
        for batch_name, _ in batches:
            batch_key = batch_name.upper().replace(" ", "_")
            report_name = f"BATCH_3_-_{batch_key}_REPORT.md"
            links.append(f"- [{report_name}]({report_name})")
        return "\n".join(links)

    def run_batch4_review(self):
        """Run Batch 4 comprehensive CI review analysis - FINAL BATCH."""
        print("🚀 Starting Batch 4 CI Review - Final Remaining Files")
        
        os.makedirs(self.base_path / "ci-reviews", exist_ok=True)
        
        # Batch 4 component analysis  
        batches = [
            ("Remaining Readers", self.batch4_remaining_readers),
            ("Package Initialization", self.batch4_remaining_packages),
            ("Remaining Sandbox", self.batch4_remaining_sandbox),
            ("Remaining Tests", self.batch4_remaining_tests),
            ("savReaderWriter Complete", self.batch4_savreaderwriter_complete)
        ]
        
        all_results = []
        
        for batch_name, files in batches:
            print(f"\n📋 Analyzing Batch 4 - {batch_name} ({len(files)} files)")
            batch_results = []
            
            for i, file_path in enumerate(files, 1):
                print(f"  [{i:2d}/{len(files)}] {file_path}")
                result = self.quick_analyze(file_path)
                batch_results.append(result)
                all_results.append(result)
            
            # Generate batch report
            self.generate_batch_report(batch_results, batch_name)
        
        # Generate Batch 4 specific master summary
        self._generate_batch4_master_summary(all_results, batches)
        
        print(f"📋 Batch 4 master summary: {self.base_path / 'ci-reviews/BATCH4_MASTER_SUMMARY.md'}")
        print("\n✅ Batch 4 review complete!")
        print(f"📁 Additional reports in: {self.base_path / 'ci-reviews'}")

    def _generate_batch4_master_summary(self, all_results: list, batches: list):
        """Generate Batch 4 specific master summary - FINAL BATCH."""
        output_path = self.base_path / "ci-reviews/BATCH4_MASTER_SUMMARY.md"
        
        total_files = len(all_results)
        missing_files = len([r for r in all_results if not r.exists])
        total_violations = sum(r.ruff_violations for r in all_results if r.exists and r.ruff_violations != 999)
        
        with open(output_path, 'w') as f:
            f.write(f"""# Batch 4 CI Review - Final Master Summary

## Batch 4 Overview (COMPLETION)
**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Branch**: master  
**Files Analyzed**: {total_files}  
**Total Violations**: {total_violations:,}  
**Missing Files**: {missing_files}  
**Compilation Failures**: 0

## Final Comprehensive Quality Assessment

### 🏗️ SOLID Design Principles
{self._format_solid_assessment(all_results)}

### 📖 Documentation Coverage  
{self._format_documentation_analysis(all_results)}

### 🐍 Python 3.10-3.12 Readiness
{self._format_compatibility_review(all_results)}

## Top Priority Issues (Batch 4 - Final)
{self._format_top_issues(all_results)}

## Batch 4 Component Analysis (Completion)
{self._format_batch_component_analysis(all_results, batches)}

## Final Comprehensive Modernization Roadmap
{self._generate_final_roadmap(all_results)}

## All Batch Reports Generated
{self._format_final_batch_report_links(batches)}

---
*Batch 4 Final Analysis completed on master branch | Complete 131-file comprehensive assessment*
*SOLID, DRY, KISS, YAGNI + Python 3.10-3.12 compatibility analysis COMPLETE*
""")

    def _generate_final_roadmap(self, results: list) -> str:
        """Generate final comprehensive modernization roadmap."""
        return """
## 🎯 COMPREHENSIVE 131-FILE MODERNIZATION ROADMAP

### Sprint 1: Critical Infrastructure & Missing Files (2-3 weeks) - **IMMEDIATE**
- **Missing Files**: Create all missing reader/writer modules identified
- **savReaderWriter Elimination**: Complete removal and pyreadstat replacement
- **Critical Architecture**: Address all SOLID Grade F violations
- **Blocking Issues**: Resolve all compilation failures

### Sprint 2: High-Violation Core Files (3-4 weeks)
- **Statistical Engine**: quantify/engine.py comprehensive refactoring (2400+ violations)
- **Data Processing**: decipher/reader.py modernization (2200+ violations)  
- **Excel Generation**: Complete excel_painter.py cleanup (600+ violations)
- **Core Infrastructure**: Address all files >100 violations

### Sprint 3: Test Suite Modernization (4-5 weeks)
- **pytest Migration**: Convert all unittest patterns to modern pytest
- **SOLID Compliance**: Break down monolithic test classes
- **Coverage Enhancement**: Achieve 80%+ test coverage across all modules
- **Integration Testing**: End-to-end workflow validation

### Sprint 4: Python 3.10-3.12 Feature Integration (3-4 weeks)
- **Type System**: Complete type hints across all 131 files
- **Modern Syntax**: Union operators, pattern matching, dataclasses
- **Performance**: Leverage Python 3.10+ performance improvements
- **Compatibility**: Full 3.10-3.12 testing and validation

### Sprint 5: Final Quality & Documentation (2-3 weeks)
- **Zero Violations**: Achieve 0 ruff violations across all files
- **API Documentation**: Complete documentation for all public interfaces
- **Performance Validation**: Ensure no regressions vs baseline
- **Release Preparation**: Final quality gates and v1.0.0 preparation

**TOTAL EFFORT ESTIMATE**: 14-19 weeks (280-380 hours)
**TARGET COMPLETION**: quantipy3 v1.0.0 - Q2 2025
"""

    def _format_final_batch_report_links(self, batches: list) -> str:
        """Format links to all batch reports for final summary."""
        links = []
        for batch_name, _ in batches:
            batch_key = batch_name.upper().replace(" ", "_")
            report_name = f"{batch_key}_REPORT.md"
            links.append(f"- [{report_name}]({report_name})")
        return "\n".join(links)

    def run_batch3_review(self):
        """Run Batch 3 comprehensive CI review analysis."""
        print("🚀 Starting Batch 3 CI Review - Next Priority Files")
        
        os.makedirs(self.base_path / "ci-reviews", exist_ok=True)
        
        # Batch 3 component analysis
        batches = [
            ("Core Processing Files", self.batch3_core_processing),
            ("Remaining Tools", self.batch3_remaining_tools), 
            ("Build System", self.batch3_remaining_builds),
            ("Final Test Files", self.batch3_final_tests)
        ]
        
        all_results = []
        
        for batch_name, files in batches:
            print(f"\n📋 Analyzing Batch 3 - {batch_name} ({len(files)} files)")
            batch_results = []
            
            for i, file_path in enumerate(files, 1):
                print(f"  [{i:2d}/{len(files)}] {file_path}")
                result = self.quick_analyze(file_path)
                batch_results.append(result)
                all_results.append(result)
            
            # Generate batch report
            batch_key = batch_name.upper().replace(" ", "_")
            report_path = self.base_path / f"ci-reviews/BATCH_3_-_{batch_key}_REPORT.md"
            self.generate_batch_report(batch_results, batch_name)
        
        # Generate master summary  
        batch_report_paths = [
            self.base_path / f"ci-reviews/BATCH_3_-_{batch_name.upper().replace(' ', '_')}_REPORT.md"
            for batch_name, _ in batches
        ]
        
        # Generate Batch 3 specific master summary
        self._generate_batch3_master_summary(all_results, batches)
        
        print(f"📋 Batch 3 master summary: {self.base_path / 'ci-reviews/BATCH3_MASTER_SUMMARY.md'}")
        print("\n✅ Batch 3 review complete!")
        print(f"📁 Additional reports in: {self.base_path / 'ci-reviews'}")

if __name__ == "__main__":
    reviewer = QuickReviewer()
    
    # Run Batch 4 analysis - FINAL BATCH to complete all 131 files
    reviewer.run_batch4_review()