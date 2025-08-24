"""
DataTransformer - Handles all data transformation operations for DataSet

This module provides a focused, SOLID-compliant implementation of data
transformation functionality extracted from the monolithic DataSet class.

Following Single Responsibility Principle, this module handles:
- Data recoding and derivation operations
- Variable type conversions  
- Data banding and grouping
- Value mapping and transformation
- In-place and copy-based transformations
"""

import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Tuple
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

if TYPE_CHECKING:
    from quantipy.core.dataset import DataSet

# Import transformation utility functions
from quantipy.core.tools.dp.prep import recode as _recode


class TransformationStrategy(ABC):
    """Abstract base class for transformation operations following Strategy pattern."""

    @abstractmethod
    def transform(
        self, 
        dataset: "DataSet", 
        target: str, 
        *args, 
        **kwargs
    ) -> Union[pd.Series, None]:
        """
        Execute transformation on target variable.

        Args:
            dataset: DataSet instance to transform
            target: Target variable name
            *args: Strategy-specific positional arguments
            **kwargs: Strategy-specific keyword arguments

        Returns:
            Transformed series or None for in-place operations
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this transformation strategy."""
        pass


class RecodeStrategy(TransformationStrategy):
    """Strategy for data recoding operations."""

    def transform(
        self, 
        dataset: "DataSet", 
        target: str, 
        mapper: Dict[Any, Any],
        default: Optional[str] = None,
        append: bool = False,
        intersect: Optional[Any] = None,
        initialize: Optional[str] = None,
        fillna: Optional[Any] = None,
        inplace: bool = True
    ) -> Union[pd.Series, None]:
        """Execute recode transformation."""
        meta = dataset._meta
        data = dataset._data
        
        recode_series = _recode(
            meta, data, target, mapper, default, append, intersect, initialize, fillna
        )
        
        if inplace:
            dataset._data[target] = recode_series
            if not dataset._is_numeric(target):
                dataset._verify_data_vs_meta_codes(target)
            return None
        else:
            return recode_series

    def get_strategy_name(self) -> str:
        return "recode"


class DeriveStrategy(TransformationStrategy):
    """Strategy for derived variable creation operations."""

    def transform(
        self, 
        dataset: "DataSet", 
        name: str,
        qtype: str,
        label: str,
        cond_map: List[Tuple[Any, ...]],
        text_key: Optional[str] = None
    ) -> None:
        """Execute derive transformation."""
        if not text_key:
            text_key = dataset.text_key
            
        append = qtype == 'delimited set'
        err_msg = (
            "'cond_map' structure not understood. Must pass a list "
            "of 2 (code, logic) / (text, logic) or 3 (code, text label, "
            "logic) element tuples!"
        )
        
        if all(len(cond) == 3 for cond in cond_map):
            categories = [(cond[0], cond[1]) for cond in cond_map]
            idx_mapper = {cond[0]: cond[-1] for cond in cond_map}
        elif all(len(cond) == 2 for cond in cond_map):
            all_int = all(isinstance(cond[0], int) for cond in cond_map)
            all_str = all(isinstance(cond[0], str) for cond in cond_map)
            
            if all_int:
                # Use codes as provided, generate labels
                categories = [(cond[0], str(cond[0])) for cond in cond_map]
                idx_mapper = {cond[0]: cond[-1] for cond in cond_map}
            elif all_str:
                # Use strings as labels, generate codes
                categories = [(i+1, cond[0]) for i, cond in enumerate(cond_map)]
                idx_mapper = {i+1: cond[-1] for i, cond in enumerate(cond_map)}
            else:
                raise ValueError(err_msg)
        else:
            raise ValueError(err_msg)

        # Add meta for the new derived variable
        dataset.add_meta(name, qtype, label, categories, text_key=text_key)
        
        # Perform the recode operation
        dataset.recode(name, idx_mapper, append=append, initialize=np.nan)
        
        return None

    def get_strategy_name(self) -> str:
        return "derive"


class ConversionStrategy(TransformationStrategy):
    """Strategy for variable type conversion operations."""

    def transform(
        self, 
        dataset: "DataSet", 
        name: str,
        to: str
    ) -> None:
        """Execute type conversion transformation."""
        valid_types = ['int', 'float', 'single', 'delimited set', 'string']
        if to not in valid_types:
            raise TypeError(f"Cannot convert to type {to}!")
            
        if to == 'int':
            self._as_int(dataset, name)
        elif to == 'float':
            self._as_float(dataset, name)
        elif to == 'single':
            self._as_single(dataset, name)
        elif to == 'delimited set':
            self._as_delimited_set(dataset, name)
        elif to == 'string':
            self._as_string(dataset, name)
            
        if dataset._is_array_item(name):
            mask_name = dataset._maskname_from_item(name)
            dataset._meta['masks'][mask_name]['subtype'] = to
            
        return None

    def _as_int(self, dataset: "DataSet", name: str) -> None:
        """Convert variable to int type."""
        org_type = dataset._get_type(name)
        if org_type == 'int':
            msg = f"Variable '{name}' is already of type 'int'."
            warnings.warn(msg)
            return None
        
        if org_type not in ['single', 'float']:
            msg = f"Cannot convert from type '{org_type}' to 'int'!"
            raise TypeError(msg)
        
        # Convert data
        dataset._data[name] = dataset._data[name].astype('int64')
        
        # Update metadata
        dataset._meta['columns'][name]['type'] = 'int'
        if 'values' in dataset._meta['columns'][name]:
            del dataset._meta['columns'][name]['values']

    def _as_float(self, dataset: "DataSet", name: str) -> None:
        """Convert variable to float type."""
        org_type = dataset._get_type(name)
        if org_type == 'float':
            msg = f"Variable '{name}' is already of type 'float'."
            warnings.warn(msg)
            return None
            
        if org_type not in ['single', 'int']:
            msg = f"Cannot convert from type '{org_type}' to 'float'!"
            raise TypeError(msg)
        
        # Convert data
        dataset._data[name] = dataset._data[name].astype('float64')
        
        # Update metadata
        dataset._meta['columns'][name]['type'] = 'float'
        if 'values' in dataset._meta['columns'][name]:
            del dataset._meta['columns'][name]['values']

    def _as_single(self, dataset: "DataSet", name: str) -> None:
        """Convert variable to single type."""
        org_type = dataset._get_type(name)
        if org_type == 'single':
            msg = f"Variable '{name}' is already of type 'single'."
            warnings.warn(msg)
            return None
            
        if org_type not in ['int', 'float', 'delimited set']:
            msg = f"Cannot convert from type '{org_type}' to 'single'!"
            raise TypeError(msg)
            
        # Update metadata
        dataset._meta['columns'][name]['type'] = 'single'
        
        # Ensure values exist for single type
        if 'values' not in dataset._meta['columns'][name]:
            # Generate values from unique data values
            unique_vals = dataset._data[name].dropna().unique()
            values = []
            for val in sorted(unique_vals):
                values.append({
                    'value': int(val),
                    'text': {'main': str(int(val))}
                })
            dataset._meta['columns'][name]['values'] = values

    def _as_delimited_set(self, dataset: "DataSet", name: str) -> None:
        """Convert variable to delimited set type."""
        org_type = dataset._get_type(name)
        if org_type == 'delimited set':
            msg = f"Variable '{name}' is already of type 'delimited set'."
            warnings.warn(msg)
            return None
            
        if org_type != 'single':
            msg = f"Cannot convert from type '{org_type}' to 'delimited set'!"
            raise TypeError(msg)
            
        # Update metadata
        dataset._meta['columns'][name]['type'] = 'delimited set'

    def _as_string(self, dataset: "DataSet", name: str) -> None:
        """Convert variable to string type."""
        org_type = dataset._get_type(name)
        if org_type == 'string':
            msg = f"Variable '{name}' is already of type 'string'."
            warnings.warn(msg)
            return None
            
        # Convert data to string
        dataset._data[name] = dataset._data[name].astype('str')
        
        # Update metadata
        dataset._meta['columns'][name]['type'] = 'string'
        if 'values' in dataset._meta['columns'][name]:
            del dataset._meta['columns'][name]['values']

    def get_strategy_name(self) -> str:
        return "conversion"


class BandingStrategy(TransformationStrategy):
    """Strategy for numeric data banding operations."""

    def transform(
        self, 
        dataset: "DataSet", 
        name: str,
        bands: Union[List[Any], Dict[str, Any]],
        new_name: Optional[str] = None,
        label: Optional[str] = None,
        text_key: Optional[str] = None
    ) -> None:
        """Execute banding transformation."""
        if not dataset._is_numeric(name):
            msg = f"Can only band numeric typed data! {name} is {dataset._get_type(name)}."
            raise TypeError(msg)
            
        if not text_key:
            text_key = dataset.text_key
        if not new_name:
            new_name = f'{name}_banded'
        if not label:
            label = dataset.text(name, False, text_key)
            
        franges = []
        labels = []
        
        # Process band definitions
        for i, band in enumerate(bands):
            if isinstance(band, dict):
                # Custom label mapping
                for custom_label, band_def in band.items():
                    franges.append(band_def)
                    labels.append(custom_label)
            else:
                # Auto-generate labels
                franges.append(band)
                if isinstance(band, tuple):
                    labels.append(f"{band[0]}-{band[1]}")
                else:
                    labels.append(str(band))
        
        # Create condition mapping for derive
        cond_map = []
        for i, (frange, band_label) in enumerate(zip(franges, labels)):
            if isinstance(frange, tuple):
                # Range condition
                logic = f"{name} >= {frange[0]} and {name} <= {frange[1]}"
            else:
                # Single value condition
                logic = f"{name} == {frange}"
            
            cond_map.append((i + 1, band_label, {name: [logic]}))
        
        # Use derive to create the banded variable
        dataset.derive(new_name, 'single', label, cond_map, text_key=text_key)
        
        return None

    def get_strategy_name(self) -> str:
        return "banding"


class DataTransformer:
    """
    Handles all data transformation operations following Single Responsibility Principle.

    This class manages:
    - Data recoding and derivation operations
    - Variable type conversions
    - Data banding and grouping  
    - Value mapping and transformation
    - Strategy-based transformation dispatch

    Uses Strategy pattern for extensible transformation support.
    """

    def __init__(self, dataset: "DataSet") -> None:
        """Initialize DataTransformer with reference to parent DataSet."""
        self._dataset = dataset
        self._strategies: Dict[str, TransformationStrategy] = {}
        self._initialize_strategies()

    def _initialize_strategies(self) -> None:
        """Initialize all available transformation strategies."""
        self._strategies = {
            "recode": RecodeStrategy(),
            "derive": DeriveStrategy(),
            "conversion": ConversionStrategy(),
            "banding": BandingStrategy(),
        }

    def get_supported_transformations(self) -> List[str]:
        """Get list of supported transformation types."""
        return list(self._strategies.keys())

    def recode(
        self,
        target: str,
        mapper: Dict[Any, Any],
        default: Optional[str] = None,
        append: bool = False,
        intersect: Optional[Any] = None,
        initialize: Optional[str] = None,
        fillna: Optional[Any] = None,
        inplace: bool = True
    ) -> Union[pd.Series, None]:
        """
        Create a new or copied series from data, recoded using a mapper.

        Args:
            target: The column variable name for recoding
            mapper: A mapper of {key: logic} entries
            default: Column name to default to for unattended lists
            append: Whether to append to existing values
            intersect: Logical statement for intersection
            initialize: Initialize target with column data or NaN
            fillna: Value to use for fillna operation
            inplace: Whether to modify dataset in place

        Returns:
            None if inplace, otherwise recoded pandas Series
        """
        if target not in self._dataset._meta.get('columns', {}):
            raise KeyError(f"Variable '{target}' not found in dataset metadata")

        strategy = self._strategies["recode"]
        return strategy.transform(
            self._dataset, target, mapper, default, append, 
            intersect, initialize, fillna, inplace
        )

    def derive(
        self, 
        name: str, 
        qtype: str, 
        label: str, 
        cond_map: List[Tuple[Any, ...]], 
        text_key: Optional[str] = None
    ) -> None:
        """
        Create meta and recode case data by specifying derived category logics.

        Args:
            name: The column variable name
            qtype: Variable type (int, float, single, delimited set)
            label: Text label information
            cond_map: List of condition tuples
            text_key: Text key for label information

        Returns:
            None - DataSet is modified inplace
        """
        strategy = self._strategies["derive"]
        return strategy.transform(
            self._dataset, name, qtype, label, cond_map, text_key
        )

    def convert(self, name: str, to: str) -> None:
        """
        Convert meta and case data between compatible variable types.

        Args:
            name: The column variable name to convert
            to: Target variable type (int, float, single, delimited set, string)

        Returns:
            None - DataSet is modified inplace
        """
        if name not in self._dataset._meta.get('columns', {}):
            raise KeyError(f"Variable '{name}' not found in dataset metadata")

        strategy = self._strategies["conversion"]
        return strategy.transform(self._dataset, name, to)

    def band(
        self, 
        name: str, 
        bands: Union[List[Any], Dict[str, Any]], 
        new_name: Optional[str] = None, 
        label: Optional[str] = None, 
        text_key: Optional[str] = None
    ) -> None:
        """
        Group numeric data with band definitions treated as group text labels.

        Args:
            name: The column variable name to band
            bands: Band definitions (list or dict mapping)
            new_name: Name for banded variable
            label: Label for banded variable
            text_key: Text key for label information

        Returns:
            None - DataSet is modified inplace
        """
        if name not in self._dataset._meta.get('columns', {}):
            raise KeyError(f"Variable '{name}' not found in dataset metadata")

        strategy = self._strategies["banding"]
        return strategy.transform(
            self._dataset, name, bands, new_name, label, text_key
        )

    def uncode(
        self, 
        target: str, 
        mapper: Dict[Any, Any], 
        default: Optional[str] = None, 
        intersect: Optional[Any] = None, 
        inplace: bool = True
    ) -> Union[pd.Series, None]:
        """
        Create a new or copied series from data, uncoded using a mapper.

        Args:
            target: The variable name to uncode
            mapper: A mapper of {key: logic} entries
            default: Column name to default to for unattended lists
            intersect: Logical statement for intersection
            inplace: Whether to modify dataset in place

        Returns:
            None if inplace, otherwise uncoded pandas Series
        """
        if target in self._dataset._meta.get('masks', {}):
            # Handle mask uncoding
            items = self._dataset._get_items(target)
            for item in items:
                self.recode(item, mapper, default=default, 
                           intersect=intersect, inplace=inplace)
        else:
            # Handle column uncoding
            return self.recode(target, mapper, default=default, 
                             intersect=intersect, inplace=inplace)
        
        return None

    def transform_custom(
        self, 
        strategy_name: str, 
        target: str, 
        *args, 
        **kwargs
    ) -> Union[pd.Series, None]:
        """
        Execute custom transformation using specified strategy.

        Args:
            strategy_name: Name of transformation strategy to use
            target: Target variable name
            *args: Strategy-specific arguments
            **kwargs: Strategy-specific keyword arguments

        Returns:
            Strategy-dependent return value
        """
        if strategy_name not in self._strategies:
            raise ValueError(f"Unknown transformation strategy: {strategy_name}")

        strategy = self._strategies[strategy_name]
        return strategy.transform(self._dataset, target, *args, **kwargs)

    def get_transformation_info(self) -> Dict[str, Any]:
        """Get information about available transformations."""
        return {
            "supported_strategies": self.get_supported_transformations(),
            "dataset_name": self._dataset.name,
            "available_variables": list(self._dataset._data.columns) if self._dataset._data is not None else [],
            "transformation_count": len(self._strategies)
        }