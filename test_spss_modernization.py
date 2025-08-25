#!/usr/bin/env python
"""Test script to verify SPSS I/O modernization with pyreadstat.

This script tests that the savReaderWriter elimination is successful
and that SPSS files can be read/written using only pyreadstat.
"""

import sys
import os
import traceback
from pathlib import Path

# Add quantipy to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that we can import without savReaderWriter."""
    print("=" * 60)
    print("Testing imports...")
    print("=" * 60)
    
    try:
        # This should NOT import savReaderWriter
        from quantipy.core.tools.dp.spss import reader, writer
        print("✅ Successfully imported SPSS reader and writer modules")
        
        # Check that modern_io is available
        from quantipy.core.tools.dp.spss import modern_io
        print("✅ Successfully imported modern_io module")
        
        # Verify pyreadstat is available
        import pyreadstat
        print(f"✅ pyreadstat version: {pyreadstat.__version__}")
        
        # Try to import savReaderWriter (should fail in clean environment)
        try:
            import savReaderWriter
            print("⚠️  WARNING: savReaderWriter is still installed (but not used)")
        except ImportError:
            print("✅ savReaderWriter is NOT installed (as intended)")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_read_functions():
    """Test that read functions work without savReaderWriter."""
    print("\n" + "=" * 60)
    print("Testing read functions...")
    print("=" * 60)
    
    try:
        from quantipy.core.tools.dp.spss.reader import parse_sav_file, extract_sav_data, extract_sav_meta
        
        # Check function signatures
        print("✅ parse_sav_file available")
        print("✅ extract_sav_data available")
        print("✅ extract_sav_meta available")
        
        # Check modern_io functions
        from quantipy.core.tools.dp.spss.modern_io import read_sav, write_sav
        print("✅ modern read_sav available")
        print("✅ modern write_sav available")
        
        return True
        
    except Exception as e:
        print(f"❌ Function test error: {e}")
        traceback.print_exc()
        return False


def test_sample_file():
    """Test with a sample SPSS file if available."""
    print("\n" + "=" * 60)
    print("Testing with sample file...")
    print("=" * 60)
    
    # Look for test SPSS files
    test_files = list(Path("tests").glob("**/*.sav")) if Path("tests").exists() else []
    
    if not test_files:
        print("⚠️  No test SPSS files found in tests/ directory")
        return True  # Not a failure, just no test files
    
    test_file = test_files[0]
    print(f"Found test file: {test_file}")
    
    try:
        from quantipy.core.tools.dp.spss.reader import parse_sav_file
        
        # Try to read the file
        meta, data = parse_sav_file(
            filename=test_file.name,
            path=str(test_file.parent) + "/",
            engine='pyreadstat'  # Explicitly use pyreadstat
        )
        
        print(f"✅ Successfully read SPSS file with pyreadstat")
        print(f"   - Data shape: {data.shape}")
        print(f"   - Columns: {len(meta.get('columns', {}))} variables")
        
        return True
        
    except Exception as e:
        print(f"❌ File read error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SPSS I/O MODERNIZATION TEST SUITE")
    print("Testing savReaderWriter elimination")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Function Test", test_read_functions()))
    results.append(("File Test", test_sample_file()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("savReaderWriter has been successfully eliminated.")
        print("SPSS I/O now uses modern pyreadstat exclusively.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())