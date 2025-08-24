"""
ArrayManager - Handles all array and mask operations for DataSet

This module provides a focused, SOLID-compliant implementation of array
and mask management functionality extracted from the monolithic DataSet class.

Following Single Responsibility Principle, this module handles:
- Array creation and combination operations
- Array item management (add, remove, reorder, extend)
- Array inspection and metadata queries
- Array maintenance and text operations
- Array analysis and validation
"""

import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Tuple
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

if TYPE_CHECKING:
    from quantipy.core.dataset import DataSet

# Import array utility functions
from quantipy.core.helpers.functions import verify_variable_name


class ArrayStrategy(ABC):
    """Abstract base class for array operations following Strategy pattern."""

    @abstractmethod
    def execute(
        self, 
        dataset: "DataSet", 
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute array operation on dataset.

        Args:
            dataset: DataSet instance to operate on
            *args: Strategy-specific positional arguments
            **kwargs: Strategy-specific keyword arguments

        Returns:
            Strategy-dependent return value
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this array strategy."""
        pass


class ArrayCreationStrategy(ArrayStrategy):
    """Strategy for array creation and combination operations."""

    def execute(
        self, 
        dataset: "DataSet", 
        operation: str,
        name: str,
        **kwargs
    ) -> Any:
        """Execute array creation operations."""
        if operation == "create_array":
            return self._create_array(dataset, name, **kwargs)
        elif operation == "to_array":
            return self._to_array(dataset, name, **kwargs)
        elif operation == "copy_array_data":
            return self._copy_array_data(dataset, name, **kwargs)
        else:
            raise ValueError(f"Unknown array creation operation: {operation}")

    def _create_array(
        self, 
        dataset: "DataSet",
        name: str,
        qtype: str,
        label: str,
        items: List[Union[str, Tuple[int, str]]],
        categories: Optional[List[Dict[str, Any]]] = None,
        text_key: Optional[str] = None
    ) -> None:
        """Create a new array from scratch."""
        if not text_key:
            text_key = dataset.text_key

        dataset._add_array(name, qtype, label, items, categories, text_key)
        return None

    def _to_array(
        self, 
        dataset: "DataSet",
        name: str,
        variables: List[Union[str, Dict[str, str]]],
        label: str,
        safe: bool = True
    ) -> None:
        """Combine existing variables into an array."""
        meta = dataset._meta
        newname = dataset._dims_compat_arr_name(name)
        
        if dataset.var_exists(newname):
            if safe:
                raise ValueError(f'{name} does already exist.')
            dataset.drop(newname, ignore_items=True)

        var_list = [list(v.keys())[0] if isinstance(v, dict) else v for v in variables]
        
        if not all(dataset.var_exists(v) for v in var_list):
            raise KeyError("'variables' must be included in DataSet.")
        elif not len(set(var_list)) == len(var_list):
            raise ValueError("'variables' contains duplicates!")

        to_comb = {
            list(v.keys())[0]: list(v.values())[0]
            for v in variables
            if isinstance(v, dict)
        }
        
        for var in var_list:
            if var not in to_comb:
                to_comb[var] = dataset.text(var)

        first = var_list[0]
        subtype = dataset._get_type(var_list[0])
        
        if dataset._has_categorical_data(var_list[0]):
            categorical = True
            if not all(dataset.codes(var) == dataset.codes(first) for var in var_list):
                raise ValueError("Variables must have same 'codes' in meta.")
        else:
            categorical = False

        # Create the array
        items = [(i+1, to_comb[var]) for i, var in enumerate(var_list)]
        categories = dataset.values(first) if categorical else None
        
        dataset._add_array(newname, subtype, label, items, categories, dataset.text_key)
        
        # Copy data from original variables to array items
        array_items = dataset._get_itemmap(newname, 'items')
        for orig_var, array_item in zip(var_list, array_items):
            if orig_var in dataset._data.columns:
                dataset._data[array_item] = dataset._data[orig_var].copy()

        return None

    def _copy_array_data(
        self,
        dataset: "DataSet", 
        source: str,
        target: str,
        source_items: Optional[List[str]] = None,
        target_items: Optional[List[str]] = None,
        slicer: Optional[Any] = None
    ) -> None:
        """Copy data between array items."""
        dataset._verify_same_value_codes_meta(source, target)
        
        all_source_items = dataset._get_itemmap(source, non_mapped='items')
        all_target_items = dataset._get_itemmap(target, non_mapped='items')
        
        if source_items is None:
            source_items = all_source_items
        if target_items is None:
            target_items = all_target_items

        if len(source_items) != len(target_items):
            raise ValueError("Source and target items must have same length")

        for s_item, t_item in zip(source_items, target_items):
            if s_item not in all_source_items:
                raise KeyError(f"'{s_item}' not found in source array '{source}'")
            if t_item not in all_target_items:
                raise KeyError(f"'{t_item}' not found in target array '{target}'")

            if slicer is not None:
                dataset._data.loc[slicer, t_item] = dataset._data.loc[slicer, s_item]
            else:
                dataset._data[t_item] = dataset._data[s_item].copy()

        return None

    def get_strategy_name(self) -> str:
        return "array_creation"


class ItemManagementStrategy(ArrayStrategy):
    """Strategy for array item management operations."""

    def execute(
        self, 
        dataset: "DataSet", 
        operation: str,
        name: str,
        **kwargs
    ) -> Any:
        """Execute item management operations."""
        if operation == "remove_items":
            return self._remove_items(dataset, name, **kwargs)
        elif operation == "extend_items":
            return self._extend_items(dataset, name, **kwargs)
        elif operation == "reorder_items":
            return self._reorder_items(dataset, name, **kwargs)
        elif operation == "set_item_texts":
            return self._set_item_texts(dataset, name, **kwargs)
        else:
            raise ValueError(f"Unknown item management operation: {operation}")

    def _remove_items(
        self, 
        dataset: "DataSet",
        name: str,
        remove: Union[int, List[int]]
    ) -> None:
        """Remove items from an array."""
        if isinstance(remove, int):
            remove = [remove]

        items = dataset._get_itemmap(name, 'items')
        drop_item_names = [
            item for idx, item in enumerate(items, start=1) if idx in remove
        ]
        keep_item_idxs = [
            idx for idx, item in enumerate(items, start=1) if idx not in remove
        ]
        
        # Update mask metadata
        new_items = dataset._meta['masks'][name]['items']
        new_items = [
            item for idx, item in enumerate(new_items, start=1) if idx in keep_item_idxs
        ]
        dataset._meta['masks'][name]['items'] = new_items
        
        # Remove from data and metadata
        for drop_item_name in drop_item_names:
            if drop_item_name in dataset._data.columns:
                dataset._data.drop(drop_item_name, axis=1, inplace=True)
            if drop_item_name in dataset._meta['columns']:
                del dataset._meta['columns'][drop_item_name]
            
            col_ref = f'columns@{drop_item_name}'
            if col_ref in dataset._meta['sets']['data file']['items']:
                dataset._meta['sets']['data file']['items'].remove(col_ref)
            if col_ref in dataset._meta['sets'][name]['items']:
                dataset._meta['sets'][name]['items'].remove(col_ref)

        return None

    def _extend_items(
        self, 
        dataset: "DataSet",
        name: str,
        ext_items: List[Union[str, Dict[str, str]]],
        text_key: Optional[str] = None
    ) -> None:
        """Extend array with new items."""
        if not text_key:
            text_key = dataset.text_key

        existing_items = dataset._get_itemmap(name, 'items')
        current_max = len(existing_items)
        
        # Process extension items
        if isinstance(ext_items[0], str):
            ext_items = [(i + current_max + 1, item) for i, item in enumerate(ext_items)]
        elif isinstance(ext_items[0], dict):
            ext_items = [(i + current_max + 1, list(item.values())[0]) 
                        for i, item in enumerate(ext_items)]

        # Get array metadata
        array_meta = dataset._meta['masks'][name]
        subtype = array_meta['subtype']
        array_label = array_meta['text'][text_key]
        
        # Get values reference for categorical arrays
        if dataset._has_categorical_data(name):
            categories = dataset.values(name)
        else:
            categories = None

        # Add new items
        for item_no, item_text in ext_items:
            item_name = f'{dataset._dims_free_arr_name(name)}_{item_no}'
            item_obj = dataset._item(item_name, text_key, item_text)
            
            # Add to items list
            array_meta['items'].append(item_obj)
            
            # Add column metadata
            column_label = f'{array_label} - {item_text}'
            dataset.add_meta(
                name=item_name,
                qtype=subtype,
                label=column_label,
                categories=categories,
                text_key=text_key
            )
            
            # Set up parent relationship
            parent_spec = {f'masks@{name}': {'type': 'array'}}
            dataset._meta['columns'][item_name]['parent'] = parent_spec
            
            # Update sets
            col_ref = f'columns@{item_name}'
            if col_ref in dataset._meta['sets']['data file']['items']:
                dataset._meta['sets']['data file']['items'].remove(col_ref)
            dataset._meta['sets'][name]['items'].append(col_ref)
            
            # Initialize data column
            if item_name not in dataset._data.columns:
                dataset._data[item_name] = np.nan

        return None

    def _reorder_items(
        self, 
        dataset: "DataSet",
        name: str,
        new_order: List[int]
    ) -> None:
        """Reorder array items."""
        items = dataset._meta['masks'][name]['items']
        
        if len(new_order) != len(items):
            raise ValueError("New order must include all existing items")
        if set(new_order) != set(range(1, len(items) + 1)):
            raise ValueError("New order must contain all item indices (1-based)")

        # Reorder items metadata
        reordered_items = [items[i - 1] for i in new_order]
        dataset._meta['masks'][name]['items'] = reordered_items
        
        # Reorder columns in data if needed
        item_names = dataset._get_itemmap(name, 'items')
        reordered_names = [dataset._get_itemmap(name, 'items')[i - 1] for i in new_order]
        
        # Reorder data columns to match
        remaining_cols = [col for col in dataset._data.columns if col not in item_names]
        new_col_order = remaining_cols + reordered_names
        dataset._data = dataset._data[new_col_order]

        return None

    def _set_item_texts(
        self, 
        dataset: "DataSet",
        name: str,
        renamed_items: Dict[Union[str, int], str],
        text_key: Optional[str] = None,
        axis_edit: Optional[str] = None
    ) -> None:
        """Set or rename item texts."""
        if not text_key:
            text_key = dataset.text_key

        items = dataset._meta['masks'][name]['items']
        item_names = dataset._get_itemmap(name, 'items')
        
        for key, new_text in renamed_items.items():
            if isinstance(key, int):
                # Item number (1-based)
                if key < 1 or key > len(items):
                    raise ValueError(f"Item index {key} out of range")
                item_idx = key - 1
                item_name = item_names[item_idx]
            else:
                # Item name
                if key not in item_names:
                    raise KeyError(f"Item '{key}' not found in array '{name}'")
                item_idx = item_names.index(key)
                item_name = key

            # Update item text in mask metadata
            items[item_idx]['text'][text_key] = new_text
            
            # Update column text metadata
            if item_name in dataset._meta['columns']:
                dataset._meta['columns'][item_name]['text'][text_key] = new_text

        return None

    def get_strategy_name(self) -> str:
        return "item_management"


class ArrayInspectionStrategy(ArrayStrategy):
    """Strategy for array inspection and metadata queries."""

    def execute(
        self, 
        dataset: "DataSet", 
        operation: str,
        name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Execute array inspection operations."""
        if operation == "items":
            return self._get_items(dataset, name, **kwargs)
        elif operation == "item_texts":
            return self._get_item_texts(dataset, name, **kwargs)
        elif operation == "item_no":
            return self._get_item_no(dataset, name, **kwargs)
        elif operation == "sources":
            return self._get_sources(dataset, name)
        elif operation == "is_array":
            return self._is_array(dataset, name)
        elif operation == "is_array_item":
            return self._is_array_item(dataset, name)
        elif operation == "maskname_from_item":
            return self._maskname_from_item(dataset, name)
        else:
            raise ValueError(f"Unknown array inspection operation: {operation}")

    def _get_items(
        self, 
        dataset: "DataSet",
        name: str,
        text_key: Optional[str] = None,
        axis_edit: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """Get array items with names and texts."""
        if not text_key:
            text_key = dataset.text_key

        itemmap = dataset._get_itemmap(name, text_key=text_key, axis_edit=axis_edit)
        return list(itemmap.items())

    def _get_item_texts(
        self, 
        dataset: "DataSet",
        name: str,
        text_key: Optional[str] = None,
        axis_edit: Optional[str] = None
    ) -> List[str]:
        """Get item text labels only."""
        if not text_key:
            text_key = dataset.text_key

        itemmap = dataset._get_itemmap(name, non_mapped='texts', text_key=text_key, axis_edit=axis_edit)
        return itemmap

    def _get_item_no(
        self, 
        dataset: "DataSet",
        name: str
    ) -> int:
        """Get item position number for array item."""
        if not dataset._is_array_item(name):
            raise ValueError(f"'{name}' is not an array item")

        mask_name = dataset._maskname_from_item(name)
        item_names = dataset._get_itemmap(mask_name, 'items')
        
        try:
            return item_names.index(name) + 1
        except ValueError:
            raise KeyError(f"Item '{name}' not found in array")

    def _get_sources(
        self, 
        dataset: "DataSet",
        name: str
    ) -> List[str]:
        """Get column names for array mask."""
        if not dataset.is_array(name):
            raise ValueError(f"'{name}' is not an array")

        return dataset._get_itemmap(name, 'items')

    def _is_array(
        self, 
        dataset: "DataSet",
        name: str
    ) -> bool:
        """Check if variable is an array."""
        return dataset._get_type(name) == 'array'

    def _is_array_item(
        self, 
        dataset: "DataSet",
        name: str
    ) -> bool:
        """Check if variable is an array item."""
        return dataset._meta['columns'].get(name, {}).get('parent', False)

    def _maskname_from_item(
        self, 
        dataset: "DataSet",
        item_name: str
    ) -> str:
        """Get mask name from array item."""
        parents = dataset.parents(item_name)
        if not parents:
            raise ValueError(f"'{item_name}' has no parent array")
        return parents[0].split('@')[-1]

    def get_strategy_name(self) -> str:
        return "array_inspection"


class ArrayMaintenanceStrategy(ArrayStrategy):
    """Strategy for array maintenance and text operations."""

    def execute(
        self, 
        dataset: "DataSet", 
        operation: str,
        **kwargs
    ) -> Any:
        """Execute array maintenance operations."""
        if operation == "restore_item_texts":
            return self._restore_item_texts(dataset, **kwargs)
        elif operation == "cut_item_texts":
            return self._cut_item_texts(dataset, **kwargs)
        elif operation == "fix_array_meta":
            return self._fix_array_meta(dataset)
        elif operation == "fix_array_item_vals":
            return self._fix_array_item_vals(dataset)
        else:
            raise ValueError(f"Unknown array maintenance operation: {operation}")

    def _restore_item_texts(
        self, 
        dataset: "DataSet",
        arrays: Optional[List[str]] = None
    ) -> None:
        """Restore array item texts from array labels."""
        if arrays is None:
            arrays = dataset.masks()

        for array in arrays:
            if not dataset.is_array(array):
                continue

            array_label = dataset.text(array)
            items = dataset._get_itemmap(array, 'items')
            item_texts = dataset._get_itemmap(array, 'texts')
            
            # Check if items need restoration
            needs_restoration = any(
                item_text == array_label for item_text in item_texts
            )
            
            if needs_restoration:
                # Generate new item texts
                new_texts = {}
                for i, item_name in enumerate(items, 1):
                    new_texts[i] = f"{array_label} - Item {i}"
                
                dataset._array_manager.set_item_texts(array, new_texts)

        return None

    def _cut_item_texts(
        self, 
        dataset: "DataSet",
        arrays: Optional[List[str]] = None
    ) -> None:
        """Remove array text prefix from item texts."""
        if arrays is None:
            arrays = dataset.masks()

        for array in arrays:
            if not dataset.is_array(array):
                continue

            array_label = dataset.text(array)
            items = dataset._meta['masks'][array]['items']
            
            for item in items:
                item_text = item['text'].get(dataset.text_key, '')
                if item_text.startswith(f"{array_label} - "):
                    new_text = item_text.replace(f"{array_label} - ", "", 1)
                    item['text'][dataset.text_key] = new_text

        return None

    def _fix_array_meta(self, dataset: "DataSet") -> None:
        """Fix array metadata inconsistencies."""
        # Insert missing 'parent' entries
        for col_name in dataset.columns():
            col_meta = dataset._meta['columns'][col_name]
            if 'parent' not in col_meta:
                # Check if this should be an array item
                for mask_name in dataset.masks():
                    items = dataset._get_itemmap(mask_name, 'items')
                    if col_name in items:
                        parent_def = {f'masks@{mask_name}': {'type': 'array'}}
                        col_meta['parent'] = parent_def
                        break

        return None

    def _fix_array_item_vals(self, dataset: "DataSet") -> None:
        """Fix array item value references."""
        for mask_name in dataset.masks():
            if dataset._has_categorical_data(mask_name):
                value_ref = f'lib@values@{mask_name}'
                items = dataset._get_itemmap(mask_name, 'items')
                
                for item_name in items:
                    if item_name in dataset._meta['columns']:
                        dataset._meta['columns'][item_name]['values'] = value_ref

        return None

    def get_strategy_name(self) -> str:
        return "array_maintenance"


class ArrayAnalysisStrategy(ArrayStrategy):
    """Strategy for array analysis and validation operations."""

    def execute(
        self, 
        dataset: "DataSet", 
        operation: str,
        name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Execute array analysis operations."""
        if operation == "empty_items":
            return self._empty_items(dataset, name, **kwargs)
        elif operation == "hide_empty_items":
            return self._hide_empty_items(dataset, **kwargs)
        elif operation == "fully_hidden_arrays":
            return self._fully_hidden_arrays(dataset)
        else:
            raise ValueError(f"Unknown array analysis operation: {operation}")

    def _empty_items(
        self, 
        dataset: "DataSet",
        name: str,
        condition: Optional[Any] = None,
        by_name: bool = True
    ) -> Union[List[str], List[int]]:
        """Find empty array items."""
        if not dataset.is_array(name):
            raise ValueError(f"'{name}' is not an array")

        items = dataset._get_itemmap(name, 'items')
        empty_items = []
        
        for i, item_name in enumerate(items, 1):
            if item_name not in dataset._data.columns:
                empty_items.append(item_name if by_name else i)
                continue
                
            item_data = dataset._data[item_name]
            
            if condition is not None:
                # Apply condition filter first
                filtered_data = dataset.take(condition)
                if item_name in filtered_data._data.columns:
                    item_data = filtered_data._data[item_name]
                else:
                    empty_items.append(item_name if by_name else i)
                    continue
            
            # Check if item is empty (all NaN or zeros)
            is_empty = item_data.isna().all() or (item_data == 0).all()
            if is_empty:
                empty_items.append(item_name if by_name else i)

        return empty_items

    def _hide_empty_items(
        self, 
        dataset: "DataSet",
        condition: Optional[Any] = None,
        arrays: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """Hide empty items in arrays."""
        if arrays is None:
            arrays = dataset.masks()

        hidden_items = {}
        
        for array in arrays:
            if not dataset.is_array(array):
                continue

            empty_items = self._empty_items(dataset, array, condition, by_name=True)
            
            if empty_items:
                hidden_items[array] = empty_items
                
                # Apply hide rules
                if 'rules' not in dataset._meta['masks'][array]:
                    dataset._meta['masks'][array]['rules'] = {}
                
                hide_rule = {
                    'hide': [f'columns@{item}' for item in empty_items]
                }
                dataset._meta['masks'][array]['rules'].update(hide_rule)

        return hidden_items

    def _fully_hidden_arrays(self, dataset: "DataSet") -> List[str]:
        """Find arrays where all items are hidden."""
        fully_hidden = []
        
        for array in dataset.masks():
            items = dataset._get_itemmap(array, 'items')
            rules = dataset._meta['masks'][array].get('rules', {})
            hidden = rules.get('hide', [])
            
            # Check if all items are hidden
            hidden_items = [rule.split('@')[-1] for rule in hidden if '@' in rule]
            if set(hidden_items) >= set(items):
                fully_hidden.append(array)

        return fully_hidden

    def get_strategy_name(self) -> str:
        return "array_analysis"


class ArrayManager:
    """
    Handles all array and mask operations following Single Responsibility Principle.

    This class manages:
    - Array creation and combination operations
    - Array item management (add, remove, reorder, extend)
    - Array inspection and metadata queries
    - Array maintenance and text operations
    - Array analysis and validation

    Uses Strategy pattern for extensible array operation support.
    """

    def __init__(self, dataset: "DataSet") -> None:
        """Initialize ArrayManager with reference to parent DataSet."""
        self._dataset = dataset
        self._strategies: Dict[str, ArrayStrategy] = {}
        self._initialize_strategies()

    def _initialize_strategies(self) -> None:
        """Initialize all available array strategies."""
        self._strategies = {
            "array_creation": ArrayCreationStrategy(),
            "item_management": ItemManagementStrategy(),
            "array_inspection": ArrayInspectionStrategy(),
            "array_maintenance": ArrayMaintenanceStrategy(),
            "array_analysis": ArrayAnalysisStrategy(),
        }

    def get_supported_operations(self) -> List[str]:
        """Get list of supported array operation types."""
        return list(self._strategies.keys())

    # Array Creation Operations
    def create_array(
        self,
        name: str,
        qtype: str,
        label: str,
        items: List[Union[str, Tuple[int, str]]],
        categories: Optional[List[Dict[str, Any]]] = None,
        text_key: Optional[str] = None
    ) -> None:
        """
        Create a new array from scratch.

        Args:
            name: Array name
            qtype: Variable type (single, delimited set, etc.)
            label: Array label
            items: List of item definitions
            categories: Value categories for categorical arrays
            text_key: Text key for labels

        Returns:
            None - DataSet is modified inplace
        """
        if name in self._dataset._meta.get('masks', {}):
            raise ValueError(f"Array '{name}' already exists")

        strategy = self._strategies["array_creation"]
        return strategy.execute(
            self._dataset, "create_array", name, 
            qtype=qtype, label=label, items=items, 
            categories=categories, text_key=text_key
        )

    def to_array(
        self,
        name: str,
        variables: List[Union[str, Dict[str, str]]],
        label: str,
        safe: bool = True
    ) -> None:
        """
        Combine existing variables into an array.

        Args:
            name: New array name
            variables: Variables to combine
            label: Array label
            safe: Whether to check for existing variables

        Returns:
            None - DataSet is modified inplace
        """
        strategy = self._strategies["array_creation"]
        return strategy.execute(
            self._dataset, "to_array", name,
            variables=variables, label=label, safe=safe
        )

    def copy_array_data(
        self,
        source: str,
        target: str,
        source_items: Optional[List[str]] = None,
        target_items: Optional[List[str]] = None,
        slicer: Optional[Any] = None
    ) -> None:
        """
        Copy data between array items.

        Args:
            source: Source array name
            target: Target array name
            source_items: Specific source items (default: all)
            target_items: Specific target items (default: all)
            slicer: Data slicer for partial copying

        Returns:
            None - DataSet is modified inplace
        """
        for array_name in [source, target]:
            if not self.is_array(array_name):
                raise ValueError(f"'{array_name}' is not an array")

        strategy = self._strategies["array_creation"]
        return strategy.execute(
            self._dataset, "copy_array_data", source,
            target=target, source_items=source_items,
            target_items=target_items, slicer=slicer
        )

    # Item Management Operations
    def remove_items(
        self,
        name: str,
        remove: Union[int, List[int]]
    ) -> None:
        """
        Remove items from an array.

        Args:
            name: Array name
            remove: Item indices to remove (1-based)

        Returns:
            None - DataSet is modified inplace
        """
        if not self.is_array(name):
            raise ValueError(f"'{name}' is not an array")

        strategy = self._strategies["item_management"]
        return strategy.execute(
            self._dataset, "remove_items", name, remove=remove
        )

    def extend_items(
        self,
        name: str,
        ext_items: List[Union[str, Dict[str, str]]],
        text_key: Optional[str] = None
    ) -> None:
        """
        Extend array with new items.

        Args:
            name: Array name
            ext_items: New items to add
            text_key: Text key for labels

        Returns:
            None - DataSet is modified inplace
        """
        if not self.is_array(name):
            raise ValueError(f"'{name}' is not an array")

        strategy = self._strategies["item_management"]
        return strategy.execute(
            self._dataset, "extend_items", name,
            ext_items=ext_items, text_key=text_key
        )

    def reorder_items(
        self,
        name: str,
        new_order: List[int]
    ) -> None:
        """
        Reorder array items.

        Args:
            name: Array name
            new_order: New item order (1-based indices)

        Returns:
            None - DataSet is modified inplace
        """
        if not self.is_array(name):
            raise ValueError(f"'{name}' is not an array")

        strategy = self._strategies["item_management"]
        return strategy.execute(
            self._dataset, "reorder_items", name, new_order=new_order
        )

    def set_item_texts(
        self,
        name: str,
        renamed_items: Dict[Union[str, int], str],
        text_key: Optional[str] = None,
        axis_edit: Optional[str] = None
    ) -> None:
        """
        Set or rename item texts.

        Args:
            name: Array name
            renamed_items: Mapping of item identifiers to new texts
            text_key: Text key for labels
            axis_edit: Axis editing parameter

        Returns:
            None - DataSet is modified inplace
        """
        if not self.is_array(name):
            raise ValueError(f"'{name}' is not an array")

        strategy = self._strategies["item_management"]
        return strategy.execute(
            self._dataset, "set_item_texts", name,
            renamed_items=renamed_items, text_key=text_key, axis_edit=axis_edit
        )

    # Array Inspection Operations
    def items(
        self,
        name: str,
        text_key: Optional[str] = None,
        axis_edit: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """
        Get array items with names and texts.

        Args:
            name: Array name
            text_key: Text key for labels
            axis_edit: Axis editing parameter

        Returns:
            List of (item_name, item_text) tuples
        """
        if not self.is_array(name):
            raise ValueError(f"'{name}' is not an array")

        strategy = self._strategies["array_inspection"]
        return strategy.execute(
            self._dataset, "items", name,
            text_key=text_key, axis_edit=axis_edit
        )

    def item_texts(
        self,
        name: str,
        text_key: Optional[str] = None,
        axis_edit: Optional[str] = None
    ) -> List[str]:
        """
        Get item text labels only.

        Args:
            name: Array name
            text_key: Text key for labels
            axis_edit: Axis editing parameter

        Returns:
            List of item text labels
        """
        if not self.is_array(name):
            raise ValueError(f"'{name}' is not an array")

        strategy = self._strategies["array_inspection"]
        return strategy.execute(
            self._dataset, "item_texts", name,
            text_key=text_key, axis_edit=axis_edit
        )

    def item_no(self, name: str) -> int:
        """
        Get item position number for array item.

        Args:
            name: Array item name

        Returns:
            Item position number (1-based)
        """
        strategy = self._strategies["array_inspection"]
        return strategy.execute(self._dataset, "item_no", name)

    def sources(self, name: str) -> List[str]:
        """
        Get column names for array mask.

        Args:
            name: Array name

        Returns:
            List of item column names
        """
        strategy = self._strategies["array_inspection"]
        return strategy.execute(self._dataset, "sources", name)

    def is_array(self, name: str) -> bool:
        """
        Check if variable is an array.

        Args:
            name: Variable name

        Returns:
            True if variable is an array
        """
        strategy = self._strategies["array_inspection"]
        return strategy.execute(self._dataset, "is_array", name)

    def is_array_item(self, name: str) -> bool:
        """
        Check if variable is an array item.

        Args:
            name: Variable name

        Returns:
            True if variable is an array item
        """
        strategy = self._strategies["array_inspection"]
        return strategy.execute(self._dataset, "is_array_item", name)

    def maskname_from_item(self, item_name: str) -> str:
        """
        Get mask name from array item.

        Args:
            item_name: Array item name

        Returns:
            Parent array name
        """
        strategy = self._strategies["array_inspection"]
        return strategy.execute(self._dataset, "maskname_from_item", item_name)

    # Array Maintenance Operations
    def restore_item_texts(
        self,
        arrays: Optional[List[str]] = None
    ) -> None:
        """
        Restore array item texts from array labels.

        Args:
            arrays: Specific arrays to restore (default: all)

        Returns:
            None - DataSet is modified inplace
        """
        strategy = self._strategies["array_maintenance"]
        return strategy.execute(
            self._dataset, "restore_item_texts", arrays=arrays
        )

    def cut_item_texts(
        self,
        arrays: Optional[List[str]] = None
    ) -> None:
        """
        Remove array text prefix from item texts.

        Args:
            arrays: Specific arrays to process (default: all)

        Returns:
            None - DataSet is modified inplace
        """
        strategy = self._strategies["array_maintenance"]
        return strategy.execute(
            self._dataset, "cut_item_texts", arrays=arrays
        )

    def fix_array_meta(self) -> None:
        """
        Fix array metadata inconsistencies.

        Returns:
            None - DataSet is modified inplace
        """
        strategy = self._strategies["array_maintenance"]
        return strategy.execute(self._dataset, "fix_array_meta")

    def fix_array_item_vals(self) -> None:
        """
        Fix array item value references.

        Returns:
            None - DataSet is modified inplace
        """
        strategy = self._strategies["array_maintenance"]
        return strategy.execute(self._dataset, "fix_array_item_vals")

    # Array Analysis Operations
    def empty_items(
        self,
        name: str,
        condition: Optional[Any] = None,
        by_name: bool = True
    ) -> Union[List[str], List[int]]:
        """
        Find empty array items.

        Args:
            name: Array name
            condition: Optional condition to filter data
            by_name: Return item names (True) or indices (False)

        Returns:
            List of empty item names or indices
        """
        strategy = self._strategies["array_analysis"]
        return strategy.execute(
            self._dataset, "empty_items", name,
            condition=condition, by_name=by_name
        )

    def hide_empty_items(
        self,
        condition: Optional[Any] = None,
        arrays: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Hide empty items in arrays.

        Args:
            condition: Optional condition to filter data
            arrays: Specific arrays to process (default: all)

        Returns:
            Dictionary mapping arrays to hidden items
        """
        strategy = self._strategies["array_analysis"]
        return strategy.execute(
            self._dataset, "hide_empty_items",
            condition=condition, arrays=arrays
        )

    def fully_hidden_arrays(self) -> List[str]:
        """
        Find arrays where all items are hidden.

        Returns:
            List of fully hidden array names
        """
        strategy = self._strategies["array_analysis"]
        return strategy.execute(self._dataset, "fully_hidden_arrays")

    def get_array_info(self) -> Dict[str, Any]:
        """Get information about array management capabilities."""
        return {
            "supported_strategies": self.get_supported_operations(),
            "dataset_name": self._dataset.name,
            "available_arrays": self._dataset.masks() if hasattr(self._dataset, 'masks') else [],
            "total_array_count": len(self._dataset.masks()) if hasattr(self._dataset, 'masks') else 0,
            "strategy_count": len(self._strategies)
        }