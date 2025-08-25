"""Constants for quantipy data type mappings and patterns.

This module provides constant mappings between quantipy types and pandas dtypes,
as well as regular expression patterns used throughout the library.
"""
from __future__ import annotations

# Type mapping from quantipy types to pandas dtypes
DTYPE_MAP: dict[str, list[str]] = {
    "float": ["float64", "float32", "float16"],
    "int": ["int64", "int32", "int16", "int8", "int0", "float64", "float32", "float16"],
    "string": ["object"],
    "date": ["datetime64"],
    "time": ["timedelta64"],
    "bool": ["bool"],
    "single": ["int64", "int32", "int16", "int8", "int0", "float64", "float32", "float16"],
    "dichotomous set": [],
    "categorical set": [],
    "delimited set": ["object"],
    "grid": []
}

# Regular expression pattern for mapped variable names
MAPPED_PATTERN: str = "^[^@].*[@].*[^@]$"
