#!/usr/bin/env python3
"""
Comprehensive CI Tooling Review for quantipy3 Modernization

This script analyzes all 131 Python files listed in COMPLETE_MODERNIZATION_TRACKER.md
using our modern CI tooling stack (ruff, mypy, compilation tests) to generate
individual quality reports for each file.

Usage:
    python comprehensive_ci_review.py

Output:
    - Individual reports in ci-reviews/ directory
    - Summary report with prioritization matrix
    - Sprint planning recommendations
"""

import os
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
import time

@dataclass
class FileAnalysis:
    """Analysis results for a single Python file."""
    file_path: str
    line_count: int
    ruff_violations: int
    ruff_details: List[str]
    mypy_errors: int
    mypy_details: List[str]
    compilation_success: bool
    compilation_error: Optional[str]
    complexity_score: str
    priority_level: str
    modernization_status: str

class ComprehensiveReviewer:
    """Comprehensive CI tooling reviewer for quantipy3 files."""
    
    def __init__(self):
        self.base_path = Path("/Users/jorgealagon/Documents/vibe-code/quantipy3")
        self.ruff_path = "/Users/jorgealagon/miniforge3_x86/envs/quantipy_modern/bin/ruff"
        self.mypy_path = "/Users/jorgealagon/miniforge3_x86/envs/quantipy_modern/bin/mypy"
        self.python_path = "/Users/jorgealagon/miniforge3_x86/envs/quantipy_py311/bin/python"
        self.output_dir = self.base_path / "ci-reviews"
        self.output_dir.mkdir(exist_ok=True)
        
        # File lists from tracker
        self.all_files = self._get_all_python_files()
        self.completed_files = self._get_completed_files()
        self.pending_files = self._get_pending_files()
        
    def _get_all_python_files(self) -> List[str]:
        """Get all 131 Python files from the tracker."""
        return [
            # Phase 1-11 COMPLETED (17 files)
            "quantipy/core/metadata.py",
            "quantipy/core/io_manager.py", 
            "quantipy/core/data_validator.py",
            "quantipy/core/data_transformer.py",
            "quantipy/core/filtering_engine.py",
            "quantipy/core/statistical_processor.py",
            "quantipy/core/array_manager.py",
            "quantipy/core/export_manager.py",
            "quantipy/core/cache_manager.py",
            "quantipy/core/stack.py",
            "quantipy/core/batch.py",
            "quantipy/core/view.py",
            "quantipy/core/chain.py",
            "quantipy/core/rules.py",
            "quantipy/core/weights/rim.py",
            "quantipy/core/weights/weight_engine.py",
            "quantipy/core/quantify/engine.py",
            
            # Phase 12+ files - Core Infrastructure
            "quantipy/core/dataset.py",
            "quantipy/core/link.py",
            "quantipy/core/cluster.py", 
            "quantipy/core/cache.py",
            "quantipy/core/options.py",
            "quantipy/core/__init__.py",
            "quantipy/core/tools/dp/io.py",
            
            # Support Files
            "quantipy/core/tools/dp/prep.py",
            "quantipy/core/tools/dp/query.py",
            "quantipy/core/helpers/functions.py",
            "quantipy/core/helpers/constants.py",
            "quantipy/core/tools/view/agg.py",
            "quantipy/core/tools/view/logic.py",
            "quantipy/core/tools/view/meta.py",
            "quantipy/core/tools/view/query.py",
            "quantipy/core/tools/view/struct.py",
            "quantipy/core/tools/qp_decorators.py",
            "quantipy/core/tools/audit.py",
            "quantipy/core/view_generators/view_mapper.py",
            "quantipy/core/view_generators/view_maps.py",
            "quantipy/core/view_generators/view_specs.py",
            "quantipy/core/srv/core.py",
            
            # Specialized Modules (Batch 10 completed + remaining)
            "quantipy/core/builds/excel/excel_painter.py",
            "quantipy/core/builds/excel/formats/xlsx_formats.py",
            "quantipy/core/builds/powerpoint/pptx_painter.py",
            "quantipy/core/builds/powerpoint/add_shapes.py",
            "quantipy/core/builds/powerpoint/helpers.py",
            "quantipy/core/builds/powerpoint/transformations.py", 
            "quantipy/core/builds/powerpoint/visual_editor.py",
            "quantipy/core/srv/handlers.py",
            "quantipy/core/srv/servers.py",
            "quantipy/core/tools/dp/spss/reader.py",
            "quantipy/core/tools/dp/spss/writer.py",
            "quantipy/core/tools/dp/dimensions/reader.py",
            "quantipy/core/tools/dp/dimensions/writer.py",
            "quantipy/core/tools/dp/dimensions/dimlabels.py",
            "quantipy/core/tools/dp/forsta/reader.py",
            "quantipy/core/tools/dp/forsta/writer.py",
            "quantipy/core/tools/dp/forsta/api_requests.py",
            "quantipy/core/tools/dp/forsta/helpers.py",
            "quantipy/core/tools/dp/forsta/languages_file.py",
            "quantipy/core/tools/dp/ascribe/reader.py",
            "quantipy/core/tools/dp/decipher/reader.py",
            
            # Package __init__.py files
            "quantipy/core/builds/__init__.py",
            "quantipy/core/builds/excel/__init__.py", 
            "quantipy/core/builds/excel/formats/__init__.py",
            "quantipy/core/builds/powerpoint/__init__.py",
            "quantipy/core/builds/powerpoint/templates/__init__.py",
            "quantipy/core/helpers/__init__.py",
            "quantipy/core/quantify/__init__.py",
            "quantipy/core/srv/__init__.py",
            "quantipy/core/tools/__init__.py",
            "quantipy/core/tools/dp/__init__.py",
            "quantipy/core/tools/dp/ascribe/__init__.py",
            "quantipy/core/tools/dp/decipher/__init__.py",
            "quantipy/core/tools/dp/dimensions/__init__.py",
            "quantipy/core/tools/dp/forsta/__init__.py", 
            "quantipy/core/tools/dp/spss/__init__.py",
            "quantipy/core/tools/view/__init__.py",
            "quantipy/core/view_generators/__init__.py",
            "quantipy/core/weights/__init__.py",
            
            # Sandbox files
            "quantipy/sandbox/__init__.py",
            "quantipy/sandbox/excel_formats_constants.py",
            "quantipy/sandbox/excel_formats.py",
            "quantipy/sandbox/excel.py",
            "quantipy/sandbox/pptx/enumerations.py",
            "quantipy/sandbox/pptx/pptx_defaults.py",
            "quantipy/sandbox/pptx/PptxChainClass.py",
            "quantipy/sandbox/pptx/PptxDefaultsClass.py",
            "quantipy/sandbox/pptx/PptxPainterClass.py",
            "quantipy/sandbox/pptx/__init__.py",
            "quantipy/sandbox/sandbox.py",
            
            # Test files
            "tests/__init__.py",
            "tests/test_ci_smoke.py",
            "tests/test_dataset.py",
            "tests/test_stack.py",
            "tests/test_view.py",
            "tests/test_chain.py",
            "tests/test_batch.py",
            "tests/test_cluster.py",
            "tests/test_link.py",
            "tests/test_rules.py",
            "tests/test_rim.py",
            "tests/test_weight_engine.py",
            "tests/test_excel.py",
            "tests/test_banked_chains.py",
            "tests/test_complex_logic.py",
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
            "tests/test_chain_old.py",
            
            # savReaderWriter (deprecation target)
            "savReaderWriter/__init__.py",
            "savReaderWriter/debug.py",
            "savReaderWriter/error.py",
            "savReaderWriter/generic.py",
            "savReaderWriter/header.py",
            "savReaderWriter/py3k.py",
            "savReaderWriter/savHeaderReader.py",
            "savReaderWriter/savReader.py",
            "savReaderWriter/savWriter.py",
            "savReaderWriter/cWriterow/__init__.py",
            "savReaderWriter/cWriterow/setup.py",
            "savReaderWriter/documentation/conf.py"
        ]
    
    def _get_completed_files(self) -> List[str]:
        """Get list of completed files from tracker."""
        # Based on tracker status - 59 completed files
        completed = []
        for file_path in self.all_files:
            if any(pattern in file_path for pattern in [
                "metadata.py", "io_manager.py", "data_validator.py", "data_transformer.py",
                "filtering_engine.py", "statistical_processor.py", "array_manager.py", 
                "export_manager.py", "cache_manager.py", "stack.py", "batch.py", "view.py",
                "chain.py", "rules.py", "weights/rim.py", "weights/weight_engine.py", 
                "quantify/engine.py", "link.py", "cluster.py", "cache.py", "options.py",
                "tools/dp/io.py", "tools/dp/prep.py", "tools/dp/query.py", "helpers/functions.py",
                "helpers/constants.py", "tools/view/agg.py", "tools/view/logic.py",
                "tools/view/meta.py", "tools/view/query.py", "tools/view/struct.py",
                "tools/qp_decorators.py", "tools/audit.py", "view_generators/view_mapper.py",
                "view_generators/view_maps.py", "view_generators/view_specs.py", "srv/core.py",
                "builds/excel/excel_painter.py", "builds/excel/formats/xlsx_formats.py",
                "builds/powerpoint/pptx_painter.py", "builds/powerpoint/add_shapes.py",
                "builds/powerpoint/helpers.py", "builds/powerpoint/transformations.py",
                "builds/powerpoint/visual_editor.py", "srv/handlers.py", "srv/servers.py",
                "tools/dp/spss/reader.py", "tools/dp/spss/writer.py", 
                "tools/dp/dimensions/reader.py", "tools/dp/dimensions/writer.py",
                "tools/dp/forsta/writer.py", "tools/dp/forsta/helpers.py", 
                "tools/dp/forsta/languages_file.py", "tools/__init__.py", "tools/dp/__init__.py",
                "tools/view/__init__.py", "core/__init__.py"
            ]):
                completed.append(file_path)
        return completed
    
    def _get_pending_files(self) -> List[str]:
        """Get list of pending files."""
        return [f for f in self.all_files if f not in self.completed_files]
    
    def analyze_file(self, file_path: str) -> FileAnalysis:
        """Perform comprehensive analysis of a single file."""
        full_path = self.base_path / file_path
        
        # Check if file exists
        if not full_path.exists():
            return FileAnalysis(
                file_path=file_path,
                line_count=0,
                ruff_violations=999,
                ruff_details=["File does not exist"],
                mypy_errors=999,
                mypy_details=["File does not exist"],
                compilation_success=False,
                compilation_error="File does not exist",
                complexity_score="N/A",
                priority_level="MISSING",
                modernization_status="MISSING"
            )
        
        # Get line count
        try:
            with open(full_path, 'r') as f:
                line_count = len(f.readlines())
        except Exception:
            line_count = 0
        
        # Ruff analysis
        ruff_violations, ruff_details = self._run_ruff(file_path)
        
        # MyPy analysis
        mypy_errors, mypy_details = self._run_mypy(file_path)
        
        # Compilation test
        compilation_success, compilation_error = self._test_compilation(file_path)
        
        # Calculate complexity and priority
        complexity_score = self._calculate_complexity(line_count, ruff_violations)
        priority_level = self._calculate_priority(file_path, ruff_violations, line_count)
        modernization_status = self._get_modernization_status(file_path)
        
        return FileAnalysis(
            file_path=file_path,
            line_count=line_count,
            ruff_violations=ruff_violations,
            ruff_details=ruff_details,
            mypy_errors=mypy_errors,
            mypy_details=mypy_details,
            compilation_success=compilation_success,
            compilation_error=compilation_error,
            complexity_score=complexity_score,
            priority_level=priority_level,
            modernization_status=modernization_status
        )
    
    def _run_ruff(self, file_path: str) -> tuple[int, List[str]]:
        """Run ruff analysis on file."""
        try:
            result = subprocess.run(
                [self.ruff_path, "check", file_path],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            violations = result.stdout.count('\n') if result.stdout else 0
            details = result.stdout.split('\n')[:10] if result.stdout else []
            return violations, details
        except Exception as e:
            return 999, [f"Ruff analysis failed: {str(e)}"]
    
    def _run_mypy(self, file_path: str) -> tuple[int, List[str]]:
        """Run mypy analysis on file."""
        try:
            result = subprocess.run(
                [self.mypy_path, file_path, "--ignore-missing-imports", "--no-error-summary"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            errors = result.stdout.count('\n') if result.stdout else 0
            details = result.stdout.split('\n')[:5] if result.stdout else []
            return errors, details
        except Exception as e:
            return 999, [f"MyPy analysis failed: {str(e)}"]
    
    def _test_compilation(self, file_path: str) -> tuple[bool, Optional[str]]:
        """Test file compilation."""
        try:
            result = subprocess.run(
                [self.python_path, "-m", "py_compile", file_path],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.returncode == 0, result.stderr if result.stderr else None
        except Exception as e:
            return False, str(e)
    
    def _calculate_complexity(self, lines: int, violations: int) -> str:
        """Calculate complexity score based on size and violations."""
        if lines < 100:
            return "SIMPLE"
        elif lines < 500:
            return "MODERATE" 
        elif lines < 1500:
            return "COMPLEX"
        else:
            return "VERY_COMPLEX"
    
    def _calculate_priority(self, file_path: str, violations: int, lines: int) -> str:
        """Calculate priority level for modernization."""
        # Critical core files
        if any(critical in file_path for critical in [
            "dataset.py", "stack.py", "view.py", "chain.py", "batch.py"
        ]):
            return "CRITICAL"
        
        # High violation count
        if violations > 100:
            return "HIGH"
        elif violations > 50:
            return "MEDIUM"
        elif violations > 10:
            return "LOW"
        else:
            return "MAINTENANCE"
    
    def _get_modernization_status(self, file_path: str) -> str:
        """Get current modernization status."""
        if file_path in self.completed_files:
            return "COMPLETED"
        elif "savReaderWriter" in file_path:
            return "DEPRECATED"
        elif "tests/" in file_path:
            return "TEST_PENDING"
        elif "sandbox/" in file_path:
            return "EXPERIMENTAL"
        else:
            return "PENDING"
    
    def generate_file_report(self, analysis: FileAnalysis) -> str:
        """Generate individual file report in code-review-modern format."""
        return f"""# CI Tooling Review: {analysis.file_path}

## File Overview
- **File Path**: `{analysis.file_path}`
- **Lines of Code**: {analysis.line_count}
- **Modernization Status**: {analysis.modernization_status}
- **Complexity Score**: {analysis.complexity_score}
- **Priority Level**: {analysis.priority_level}

## Quality Analysis

### Ruff Linting Results
- **Total Violations**: {analysis.ruff_violations}
- **Status**: {"🔴 NEEDS WORK" if analysis.ruff_violations > 10 else "🟡 MINOR ISSUES" if analysis.ruff_violations > 0 else "🟢 EXCELLENT"}

#### Top Violation Types:
```
{chr(10).join(analysis.ruff_details[:10])}
```

### MyPy Type Checking Results  
- **Type Errors**: {analysis.mypy_errors}
- **Status**: {"🔴 NO TYPE SAFETY" if analysis.mypy_errors > 20 else "🟡 PARTIAL TYPES" if analysis.mypy_errors > 0 else "🟢 TYPE SAFE"}

#### Type Issues:
```
{chr(10).join(analysis.mypy_details[:5])}
```

### Compilation Test
- **Compilation Success**: {"✅ PASSES" if analysis.compilation_success else "❌ FAILS"}
- **Error Details**: {analysis.compilation_error or "None"}

## Modernization Assessment

### Current State
- **Python 3.10+ Ready**: {"Yes" if analysis.ruff_violations < 10 and analysis.compilation_success else "No"}
- **Type Hints**: {"Complete" if analysis.mypy_errors == 0 else "Partial" if analysis.mypy_errors < 10 else "Missing"}
- **Code Quality**: {"Excellent" if analysis.ruff_violations == 0 else "Good" if analysis.ruff_violations < 10 else "Needs Work"}

### Recommended Actions
{self._generate_recommendations(analysis)}

## Sprint Planning Data
- **Estimated Effort**: {self._estimate_effort(analysis)}
- **Dependencies**: {self._identify_dependencies(analysis)}
- **Risk Level**: {self._assess_risk(analysis)}

---
*Generated by comprehensive CI tooling review on {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""

    def _generate_recommendations(self, analysis: FileAnalysis) -> str:
        """Generate specific recommendations based on analysis."""
        recommendations = []
        
        if analysis.ruff_violations > 50:
            recommendations.append("1. **Critical**: Run automated ruff fixes to reduce violations")
        elif analysis.ruff_violations > 10:
            recommendations.append("1. **High**: Address major ruff violations before type hints")
        elif analysis.ruff_violations > 0:
            recommendations.append("1. **Medium**: Clean up remaining style violations")
        else:
            recommendations.append("1. **Maintenance**: Code quality is excellent")
            
        if analysis.mypy_errors > 20:
            recommendations.append("2. **Type Safety**: Add comprehensive type hints")
        elif analysis.mypy_errors > 0:
            recommendations.append("2. **Type Safety**: Complete partial type annotations")
        else:
            recommendations.append("2. **Type Safety**: Type system is complete")
            
        if not analysis.compilation_success:
            recommendations.append("3. **Critical**: Fix compilation errors before other work")
        
        if analysis.complexity_score in ["COMPLEX", "VERY_COMPLEX"]:
            recommendations.append("4. **Architecture**: Consider SOLID refactoring")
            
        return "\n".join(recommendations) if recommendations else "No specific recommendations - file is in good condition"
    
    def _estimate_effort(self, analysis: FileAnalysis) -> str:
        """Estimate modernization effort."""
        base_hours = 0
        
        # Violation-based effort
        if analysis.ruff_violations > 100:
            base_hours += 8
        elif analysis.ruff_violations > 50:
            base_hours += 4
        elif analysis.ruff_violations > 10:
            base_hours += 2
        else:
            base_hours += 0.5
            
        # Complexity multiplier
        if analysis.complexity_score == "VERY_COMPLEX":
            base_hours *= 2
        elif analysis.complexity_score == "COMPLEX":
            base_hours *= 1.5
            
        # Type work
        if analysis.mypy_errors > 20:
            base_hours += 4
        elif analysis.mypy_errors > 0:
            base_hours += 2
            
        if base_hours < 1:
            return "0.5-1 hours"
        elif base_hours < 4:
            return "2-4 hours" 
        elif base_hours < 8:
            return "4-8 hours"
        else:
            return "8+ hours"
    
    def _identify_dependencies(self, analysis: FileAnalysis) -> str:
        """Identify modernization dependencies."""
        deps = []
        
        if "dataset.py" in analysis.file_path:
            deps.append("SOLID architecture completion")
        elif "test_" in analysis.file_path:
            deps.append("Core module modernization")
        elif "savReaderWriter" in analysis.file_path:
            deps.append("pyreadstat migration")
        elif any(pkg in analysis.file_path for pkg in ["builds/", "tools/dp/"]):
            deps.append("Core infrastructure completion")
            
        return ", ".join(deps) if deps else "None"
    
    def _assess_risk(self, analysis: FileAnalysis) -> str:
        """Assess modernization risk level."""
        if not analysis.compilation_success:
            return "HIGH - Compilation issues"
        elif analysis.complexity_score == "VERY_COMPLEX" and analysis.ruff_violations > 100:
            return "HIGH - Complex + many violations"
        elif analysis.ruff_violations > 200:
            return "MEDIUM - Many violations"
        else:
            return "LOW - Manageable scope"

    def run_comprehensive_review(self):
        """Run comprehensive review of all 131 files."""
        print(f"🚀 Starting comprehensive CI review of {len(self.all_files)} files...")
        print(f"📊 Status: {len(self.completed_files)} completed, {len(self.pending_files)} pending")
        
        all_analyses = []
        
        for i, file_path in enumerate(self.all_files, 1):
            print(f"[{i:3d}/131] Analyzing {file_path}")
            
            analysis = self.analyze_file(file_path)
            all_analyses.append(analysis)
            
            # Generate individual report
            report_content = self.generate_file_report(analysis)
            report_filename = file_path.replace("/", "_").replace(".py", "_review.md")
            report_path = self.output_dir / report_filename
            
            with open(report_path, 'w') as f:
                f.write(report_content)
        
        # Generate summary report
        self.generate_summary_report(all_analyses)
        
        print(f"✅ Comprehensive review complete!")
        print(f"📁 Individual reports: {self.output_dir}/")
        print(f"📋 Summary report: {self.output_dir}/COMPREHENSIVE_SUMMARY.md")

    def generate_summary_report(self, analyses: List[FileAnalysis]):
        """Generate comprehensive summary report."""
        
        # Calculate statistics
        total_files = len(analyses)
        total_violations = sum(a.ruff_violations for a in analyses if a.ruff_violations < 999)
        total_mypy_errors = sum(a.mypy_errors for a in analyses if a.mypy_errors < 999)
        compilation_failures = sum(1 for a in analyses if not a.compilation_success)
        
        # Categorize by priority
        critical_files = [a for a in analyses if a.priority_level == "CRITICAL"]
        high_files = [a for a in analyses if a.priority_level == "HIGH"]
        medium_files = [a for a in analyses if a.priority_level == "MEDIUM"]
        low_files = [a for a in analyses if a.priority_level == "LOW"]
        
        # Top violators
        worst_files = sorted(analyses, key=lambda x: x.ruff_violations, reverse=True)[:10]
        
        summary_content = f"""# Comprehensive CI Tooling Review Summary

## Executive Summary
**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Files Analyzed**: {total_files}  
**Total Ruff Violations**: {total_violations:,}  
**Total MyPy Errors**: {total_mypy_errors:,}  
**Compilation Failures**: {compilation_failures}  

## Current Modernization Status
- **✅ Completed**: {len(self.completed_files)} files (45%)
- **⏳ Pending**: {len(self.pending_files)} files (55%)

## Priority Distribution
- **🔴 Critical**: {len(critical_files)} files
- **🟡 High**: {len(high_files)} files  
- **🟠 Medium**: {len(medium_files)} files
- **🟢 Low**: {len(low_files)} files

## Top Priority Files for Next Sprint

### Critical Priority Files
{self._format_file_list(critical_files[:5])}

### High Priority Files
{self._format_file_list(high_files[:10])}

## Quality Analysis

### Worst Code Quality (Top 10)
{self._format_violation_list(worst_files)}

### Files Needing Type Safety
{self._format_mypy_list(sorted(analyses, key=lambda x: x.mypy_errors, reverse=True)[:10])}

### Compilation Issues
{self._format_compilation_issues([a for a in analyses if not a.compilation_success])}

## Sprint Planning Recommendations

### Sprint 1: Critical Infrastructure (2-3 weeks)
{self._format_sprint_recommendation(critical_files + high_files[:5])}

### Sprint 2: Quality Improvements (2-3 weeks)  
{self._format_sprint_recommendation(high_files[5:] + medium_files[:10])}

### Sprint 3: Remaining Modernization (3-4 weeks)
{self._format_sprint_recommendation(medium_files[10:] + low_files)}

## Risk Assessment
- **High Risk Files**: {len([a for a in analyses if "HIGH" in self._assess_risk(a)])}
- **Medium Risk Files**: {len([a for a in analyses if "MEDIUM" in self._assess_risk(a)])}
- **Low Risk Files**: {len([a for a in analyses if "LOW" in self._assess_risk(a)])}

## Technology Debt Summary
- **Average Violations per File**: {total_violations / total_files:.1f}
- **Files with >100 Violations**: {len([a for a in analyses if a.ruff_violations > 100])}
- **Files with 0 Violations**: {len([a for a in analyses if a.ruff_violations == 0])}
- **Type Coverage**: {len([a for a in analyses if a.mypy_errors == 0]) / total_files * 100:.1f}%

---
*This comprehensive review provides the foundation for systematic modernization planning*
"""

        summary_path = self.output_dir / "COMPREHENSIVE_SUMMARY.md"
        with open(summary_path, 'w') as f:
            f.write(summary_content)

    def _format_file_list(self, files: List[FileAnalysis]) -> str:
        """Format list of files for report."""
        if not files:
            return "None"
        return "\n".join([
            f"- **{f.file_path}** ({f.ruff_violations} violations, {f.line_count} lines)"
            for f in files
        ])
    
    def _format_violation_list(self, files: List[FileAnalysis]) -> str:
        """Format violation list."""
        return "\n".join([
            f"{i+1:2d}. **{f.file_path}** - {f.ruff_violations} violations ({f.complexity_score})"
            for i, f in enumerate(files)
        ])
    
    def _format_mypy_list(self, files: List[FileAnalysis]) -> str:
        """Format MyPy error list."""
        return "\n".join([
            f"- **{f.file_path}** - {f.mypy_errors} type errors"
            for f in files if f.mypy_errors > 0
        ][:10])
    
    def _format_compilation_issues(self, files: List[FileAnalysis]) -> str:
        """Format compilation issues."""
        if not files:
            return "✅ All files compile successfully"
        return "\n".join([
            f"- **{f.file_path}** - {f.compilation_error}"
            for f in files
        ])
    
    def _format_sprint_recommendation(self, files: List[FileAnalysis]) -> str:
        """Format sprint planning recommendations."""
        if not files:
            return "No files in this category"
            
        total_effort = sum(self._effort_to_hours(self._estimate_effort(f)) for f in files)
        return f"""
**Files**: {len(files)}  
**Estimated Effort**: {total_effort:.1f} hours  
**Focus**: {self._get_sprint_focus(files)}

**Key Files**:
{self._format_file_list(files[:8])}
"""
    
    def _effort_to_hours(self, effort_str: str) -> float:
        """Convert effort string to hours for calculation."""
        if "0.5-1" in effort_str:
            return 0.75
        elif "2-4" in effort_str:
            return 3
        elif "4-8" in effort_str:
            return 6
        elif "8+" in effort_str:
            return 10
        else:
            return 2
    
    def _get_sprint_focus(self, files: List[FileAnalysis]) -> str:
        """Determine sprint focus based on files."""
        if any("dataset.py" in f.file_path for f in files):
            return "Core architecture and critical infrastructure"
        elif any("test_" in f.file_path for f in files):
            return "Test suite modernization and coverage"
        elif any("builds/" in f.file_path for f in files):
            return "Export and reporting functionality"
        else:
            return "Support utilities and quality improvements"

if __name__ == "__main__":
    reviewer = ComprehensiveReviewer()
    reviewer.run_comprehensive_review()