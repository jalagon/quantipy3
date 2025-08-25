"""
quantipy.core.tools.dp.spss - SPSS file I/O functionality.

This module provides reading and writing capabilities for SPSS .sav files
using the modern pyreadstat library, with full backward compatibility
for existing quantipy code.
"""

from .reader import parse_sav_file, extract_sav_data, extract_sav_meta
from .writer import write_sav
from .modern_io import read_sav, write_sav as modern_write_sav

__all__ = [
    'parse_sav_file', 'extract_sav_data', 'extract_sav_meta',
    'write_sav', 'read_sav', 'modern_write_sav'
]