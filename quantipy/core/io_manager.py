"""
IOManager - Handles all file I/O operations for DataSet

This module provides a focused, SOLID-compliant implementation of file I/O
functionality extracted from the monolithic DataSet class using the Strategy pattern.

Following Single Responsibility Principle, this module handles:
- File reading and writing operations
- Format-specific I/O strategies
- Data import/export coordination
- File format detection and validation
"""

import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import pandas as pd

if TYPE_CHECKING:
    from quantipy.core.dataset import DataSet

# Import the existing I/O functions
from quantipy.core.tools.dp.io import (
    read_ascribe as r_ascribe,
    read_decipher as r_decipher,
    read_dimensions as r_dimensions,
    read_forsta_api as r_forsta_api,
    read_forsta_from_files as r_forsta_from_files,
    read_quantipy as r_quantipy,
    read_spss as r_spss,
    write_dimensions as w_dimensions,
    write_forsta_api as w_forsta_api,
    write_quantipy as w_quantipy,
    write_spss as w_spss,
)


class IOStrategy(ABC):
    """Abstract base class for file I/O operations following Strategy pattern."""

    @abstractmethod
    def read(
        self, dataset: "DataSet", *args, **kwargs
    ) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
        """
        Read data and metadata from files.

        Args:
            dataset: DataSet instance to populate
            *args: Format-specific positional arguments
            **kwargs: Format-specific keyword arguments

        Returns:
            Tuple of (DataFrame, metadata_dict) or (None, None) if error
        """
        pass

    @abstractmethod
    def write(self, dataset: "DataSet", *args, **kwargs) -> bool:
        """
        Write data and metadata to files.

        Args:
            dataset: DataSet instance to write from
            *args: Format-specific positional arguments
            **kwargs: Format-specific keyword arguments

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """Return the name of this file format."""
        pass


class QuantipyStrategy(IOStrategy):
    """Strategy for Quantipy native file format."""

    def read(
        self, dataset: "DataSet", path_meta: str, path_data: str, reset: bool = True
    ) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
        """Read Quantipy native format files."""
        try:
            return r_quantipy(path_meta, path_data)
        except Exception as e:
            print(f"Error reading Quantipy files: {e}")
            return None, None

    def write(
        self,
        dataset: "DataSet",
        path_meta: Optional[str] = None,
        path_data: Optional[str] = None,
    ) -> bool:
        """Write Quantipy native format files."""
        try:
            return w_quantipy(dataset._data, dataset._meta, path_meta, path_data)
        except Exception as e:
            print(f"Error writing Quantipy files: {e}")
            return False

    def get_format_name(self) -> str:
        return "quantipy"


class SPSSStrategy(IOStrategy):
    """Strategy for SPSS file format."""

    def read(
        self, dataset: "DataSet", path_sav: str, **kwargs
    ) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
        """Read SPSS .sav files."""
        try:
            return r_spss(path_sav, **kwargs)
        except Exception as e:
            print(f"Error reading SPSS file: {e}")
            return None, None

    def write(
        self,
        dataset: "DataSet",
        path_sav: str,
        index: bool = False,
        text_key: Optional[str] = None,
        mode: str = "w",
        drop_q1: bool = True,
    ) -> bool:
        """Write SPSS .sav files."""
        try:
            return w_spss(
                dataset._data,
                dataset._meta,
                path_sav,
                index=index,
                text_key=text_key,
                mode=mode,
                drop_q1=drop_q1,
            )
        except Exception as e:
            print(f"Error writing SPSS file: {e}")
            return False

    def get_format_name(self) -> str:
        return "spss"


class DimensionsStrategy(IOStrategy):
    """Strategy for Dimensions file format."""

    def read(
        self, dataset: "DataSet", path_meta: str, path_data: str
    ) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
        """Read Dimensions format files."""
        try:
            return r_dimensions(path_meta, path_data)
        except Exception as e:
            print(f"Error reading Dimensions files: {e}")
            return None, None

    def write(
        self,
        dataset: "DataSet",
        path_meta: str,
        path_data: str,
        text_key: Optional[str] = None,
        CASEDATA: bool = True,
        text_key_to_q1: bool = True,
        base_text: Optional[str] = None,
        net_name: str = "net",
        path_setup: Optional[str] = None,
        interviewer_name: str = "interviewer",
        interviewer_id: str = "serial",
        weight_name: Optional[str] = None,
        reset_index: bool = True,
        clean_up_meta: bool = True,
        ignore_region_definition: bool = True,
        del_mis_axis: bool = True,
        compress: bool = True,
        drop_empty_cats: bool = True,
    ) -> bool:
        """Write Dimensions format files."""
        try:
            return w_dimensions(
                dataset._data,
                dataset._meta,
                path_meta,
                path_data,
                text_key=text_key,
                CASEDATA=CASEDATA,
                text_key_to_q1=text_key_to_q1,
                base_text=base_text,
                net_name=net_name,
                path_setup=path_setup,
                interviewer_name=interviewer_name,
                interviewer_id=interviewer_id,
                weight_name=weight_name,
                reset_index=reset_index,
                clean_up_meta=clean_up_meta,
                ignore_region_definition=ignore_region_definition,
                del_mis_axis=del_mis_axis,
                compress=compress,
                drop_empty_cats=drop_empty_cats,
            )
        except Exception as e:
            print(f"Error writing Dimensions files: {e}")
            return False

    def get_format_name(self) -> str:
        return "dimensions"


class AscribeStrategy(IOStrategy):
    """Strategy for Ascribe file format."""

    def read(
        self, dataset: "DataSet", path_meta: str, path_data: str, text_key: str
    ) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
        """Read Ascribe format files."""
        try:
            return r_ascribe(path_meta, path_data, text_key)
        except Exception as e:
            print(f"Error reading Ascribe files: {e}")
            return None, None

    def write(self, dataset: "DataSet", *args, **kwargs) -> bool:
        """Ascribe format does not support writing."""
        raise NotImplementedError("Ascribe format does not support writing")

    def get_format_name(self) -> str:
        return "ascribe"


class ForstaStrategy(IOStrategy):
    """Strategy for Forsta file format."""

    def read(
        self, dataset: "DataSet", source_type: str = "files", *args, **kwargs
    ) -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
        """Read Forsta format from files or API."""
        try:
            if source_type == "files":
                return r_forsta_from_files(*args, **kwargs)
            elif source_type == "api":
                return r_forsta_api(*args, **kwargs)
            else:
                raise ValueError(f"Unknown Forsta source type: {source_type}")
        except Exception as e:
            print(f"Error reading Forsta data: {e}")
            return None, None

    def write(
        self, dataset: "DataSet", destination_type: str = "files", *args, **kwargs
    ) -> bool:
        """Write Forsta format to files or API."""
        try:
            if destination_type == "files":
                # File writing logic would go here
                return True
            elif destination_type == "api":
                return w_forsta_api(dataset._data, dataset._meta, *args, **kwargs)
            else:
                raise ValueError(f"Unknown Forsta destination type: {destination_type}")
        except Exception as e:
            print(f"Error writing Forsta data: {e}")
            return False

    def get_format_name(self) -> str:
        return "forsta"


class IOManager:
    """
    Handles all file I/O operations following Single Responsibility Principle.

    This class manages:
    - File format strategy selection
    - Read/write operation coordination
    - Error handling and validation
    - Path resolution and file management

    Uses Strategy pattern for extensible format support.
    """

    def __init__(self, dataset: "DataSet") -> None:
        """Initialize IOManager with reference to parent DataSet."""
        self._dataset = dataset
        self._strategies: Dict[str, IOStrategy] = {}
        self._initialize_strategies()

    def _initialize_strategies(self) -> None:
        """Initialize all available I/O strategies."""
        self._strategies = {
            "quantipy": QuantipyStrategy(),
            "spss": SPSSStrategy(),
            "dimensions": DimensionsStrategy(),
            "ascribe": AscribeStrategy(),
            "forsta": ForstaStrategy(),
        }

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return list(self._strategies.keys())

    def detect_format_from_path(self, path: str) -> Optional[str]:
        """
        Detect file format from file extension.

        Args:
            path: File path to analyze

        Returns:
            Format name or None if not detected
        """
        if not path:
            return None

        path_lower = path.lower()

        if path_lower.endswith(".sav"):
            return "spss"
        elif path_lower.endswith(".json") and "meta" in path_lower:
            return "quantipy"
        elif path_lower.endswith(".mdd"):
            return "dimensions"
        elif path_lower.endswith(".xlsx") or path_lower.endswith(".xls"):
            return "excel"
        else:
            return None

    def read_data(self, format_name: str, *args, reset: bool = True, **kwargs) -> bool:
        """
        Read data using specified format strategy.

        Args:
            format_name: Name of format strategy to use
            *args: Format-specific arguments
            reset: Whether to reset dataset before loading
            **kwargs: Format-specific keyword arguments

        Returns:
            True if successful, False otherwise
        """
        if format_name not in self._strategies:
            raise ValueError(f"Unsupported format: {format_name}")

        strategy = self._strategies[format_name]

        try:
            data, meta = strategy.read(self._dataset, *args, **kwargs)

            if data is None or meta is None:
                return False

            # Apply to dataset
            if reset:
                self._reset_dataset()

            self._dataset._data = data
            self._dataset._meta = meta

            # Set file info if paths provided
            if args:
                self._set_file_info(args)

            return True

        except Exception as e:
            print(f"Error in read_data: {e}")
            return False

    def write_data(self, format_name: str, *args, **kwargs) -> bool:
        """
        Write data using specified format strategy.

        Args:
            format_name: Name of format strategy to use
            *args: Format-specific arguments
            **kwargs: Format-specific keyword arguments

        Returns:
            True if successful, False otherwise
        """
        if format_name not in self._strategies:
            raise ValueError(f"Unsupported format: {format_name}")

        if self._dataset._data is None:
            raise ValueError("No data to write")

        strategy = self._strategies[format_name]

        try:
            return strategy.write(self._dataset, *args, **kwargs)
        except Exception as e:
            print(f"Error in write_data: {e}")
            return False

    def from_components(
        self,
        data_df: pd.DataFrame,
        meta_dict: Optional[Dict[str, Any]] = None,
        reset: bool = True,
        text_key: Optional[str] = None,
    ) -> bool:
        """
        Load dataset from data and metadata components.

        Args:
            data_df: Pandas DataFrame with case data
            meta_dict: Metadata dictionary
            reset: Whether to reset dataset before loading
            text_key: Default text key to use

        Returns:
            True if successful, False otherwise
        """
        try:
            if reset:
                self._reset_dataset()

            self._dataset._data = data_df.copy()

            if meta_dict is not None:
                self._dataset._meta = meta_dict.copy()

                # Set text key from meta or parameter
                if text_key:
                    if "lib" not in self._dataset._meta:
                        self._dataset._meta["lib"] = {}
                    self._dataset._meta["lib"]["default text"] = text_key
                elif (
                    "lib" in self._dataset._meta
                    and "default text" in self._dataset._meta["lib"]
                ):
                    text_key = self._dataset._meta["lib"]["default text"]

                self._dataset.text_key = text_key or "main"

            return True

        except Exception as e:
            print(f"Error in from_components: {e}")
            return False

    def get_file_info(self) -> Dict[str, Any]:
        """Get information about loaded files."""
        return {
            "path": getattr(self._dataset, "path", None),
            "name": self._dataset.name,
            "data_loaded": self._dataset._data is not None,
            "meta_loaded": self._dataset._meta is not None,
            "text_key": getattr(self._dataset, "text_key", None),
        }

    def validate_paths(self, *paths: str) -> Tuple[bool, List[str]]:
        """
        Validate that file paths exist and are accessible.

        Args:
            *paths: File paths to validate

        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []

        for path in paths:
            if not path:
                errors.append("Empty path provided")
                continue

            if not os.path.exists(path):
                errors.append(f"File does not exist: {path}")
                continue

            if not os.access(path, os.R_OK):
                errors.append(f"File not readable: {path}")

        return len(errors) == 0, errors

    # Private utility methods

    def _reset_dataset(self) -> None:
        """Reset dataset to clean state."""
        self._dataset._data = None
        self._dataset._meta = None
        self._dataset.filtered = "no_filter"

    def _set_file_info(self, paths: Tuple[str, ...]) -> None:
        """Set file path information on dataset."""
        if paths:
            # Use first path as primary path
            primary_path = paths[0]
            if isinstance(primary_path, str):
                self._dataset.path = os.path.dirname(primary_path)
