"""
quantipy.core.weights - Statistical weighting functionality.

This package provides RIM weighting algorithms and weight management
utilities for survey data analysis.
"""

from .rim import Rim
from .weight_engine import WeightEngine

__all__ = ['Rim', 'WeightEngine']
