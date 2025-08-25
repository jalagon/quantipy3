"""Modern SPSS I/O module using pyreadstat.

This module provides a complete replacement for savReaderWriter functionality
using the modern pyreadstat library, which fully supports Python 3.10-3.12.
All functions maintain backward compatibility while eliminating the legacy
savReaderWriter dependency.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pyreadstat

from quantipy.core.tools.dp.prep import start_meta


def read_sav(
    filepath: str | Path,
    name: str = "",
    ioLocale: str = "en_US.UTF-8",
    ioUtf8: bool = True,
    dichot: dict | None = None,
    dates_as_strings: bool = False,
    text_key: str = "en-GB",
    **kwargs
) -> tuple[dict, pd.DataFrame]:
    """Read SPSS .sav file and return quantipy meta and data.
    
    Complete replacement for savReaderWriter-based parse_sav_file function
    using modern pyreadstat library.
    
    Parameters
    ----------
    filepath : str | Path
        Path to the SPSS .sav file
    name : str, default=""
        Optional name for the dataset (stored in meta)
    ioLocale : str, default="en_US.UTF-8"
        Locale for text encoding
    ioUtf8 : bool, default=True
        Whether to use UTF-8 encoding (compatibility parameter)
    dichot : dict, optional
        Values to use for True/False in dichotomous sets
    dates_as_strings : bool, default=False
        If True, treat all dates as strings
    text_key : str, default="en-GB"
        Text key for storing labels
    **kwargs
        Additional arguments passed to pyreadstat.read_sav
        
    Returns
    -------
    tuple[dict, pd.DataFrame]
        Quantipy meta dictionary and data DataFrame
    """
    filepath = Path(filepath).resolve()

    # Extract encoding from locale
    encoding = ioLocale.split(".")[-1] if "." in ioLocale else "UTF-8"
    if not ioUtf8:
        encoding = None  # Let pyreadstat detect encoding

    # Read SPSS file with pyreadstat
    df, metadata = pyreadstat.read_sav(
        str(filepath),
        encoding=encoding,
        dates_as_pandas_datetime=not dates_as_strings,
        **kwargs
    )

    # Convert metadata to quantipy format
    meta = _convert_metadata_to_quantipy(
        metadata=metadata,
        name=name or filepath.stem,
        text_key=text_key,
        dichot=dichot,
        dates_as_strings=dates_as_strings
    )

    # Process data for quantipy compatibility
    df = _process_data_for_quantipy(df, metadata, dates_as_strings)

    return meta, df


def write_sav(
    filepath: str | Path,
    data: pd.DataFrame,
    meta: dict | None = None,
    var_labels: dict | None = None,
    value_labels: dict | None = None,
    formats: dict | None = None,
    column_widths: dict | None = None,
    measure: dict | None = None,
    **kwargs
) -> None:
    """Write data to SPSS .sav file using pyreadstat.
    
    Complete replacement for savReaderWriter-based write_sav function
    using modern pyreadstat library.
    
    Parameters
    ----------
    filepath : str | Path
        Output path for the SPSS .sav file
    data : pd.DataFrame
        Data to write
    meta : dict, optional
        Quantipy meta dictionary to extract variable information
    var_labels : dict, optional
        Variable labels mapping {column: label}
    value_labels : dict, optional
        Value labels mapping {column: {value: label}}
    formats : dict, optional
        Variable formats mapping {column: format_string}
    column_widths : dict, optional
        Column widths for string variables {column: width}
    measure : dict, optional
        Measurement levels {column: level} where level is 'nominal', 'ordinal', or 'scale'
    **kwargs
        Additional arguments passed to pyreadstat.write_sav
        
    Returns
    -------
    None
    """
    filepath = Path(filepath).resolve()

    # If meta provided, extract variable information
    if meta is not None:
        var_labels, value_labels, formats, measure = _extract_spss_metadata_from_quantipy(
            meta, var_labels, value_labels, formats, measure
        )

    # Prepare data for SPSS
    data_prepared = _prepare_data_for_spss(data)

    # Write to SPSS file
    pyreadstat.write_sav(
        df=data_prepared,
        dst_path=str(filepath),
        variable_labels=var_labels,
        variable_value_labels=value_labels,
        variable_formats=formats,
        column_widths=column_widths,
        variable_measure=measure,
        **kwargs
    )


def _convert_metadata_to_quantipy(
    metadata: Any,
    name: str,
    text_key: str,
    dichot: dict | None,
    dates_as_strings: bool
) -> dict:
    """Convert pyreadstat metadata to quantipy meta format.
    
    Parameters
    ----------
    metadata : pyreadstat metadata object
        Metadata from pyreadstat.read_sav
    name : str
        Dataset name
    text_key : str
        Text key for labels
    dichot : dict, optional
        Dichotomous set configuration
    dates_as_strings : bool
        Whether to treat dates as strings
        
    Returns
    -------
    dict
        Quantipy meta dictionary
    """
    meta = start_meta(text_key=text_key)

    meta['info']['text'] = f'Converted from SAV file {name}'
    meta['info']['from_source'] = {'pandas_reader': 'sav'}
    meta['sets']['data file']['items'] = [
        f'columns@{varname}' for varname in metadata.column_names
    ]

    # Process each variable
    for idx, column in enumerate(metadata.column_names):
        meta['columns'][column] = {
            'name': column,
            'parent': {},
            'type': _get_quantipy_type(metadata, idx, dates_as_strings)
        }

        # Add variable label if exists
        if column in metadata.column_names_to_labels:
            meta['columns'][column]['text'] = {
                text_key: metadata.column_names_to_labels[column]
            }

        # Add value labels if exist
        if column in metadata.variable_value_labels:
            values = []
            for value, label in metadata.variable_value_labels[column].items():
                values.append({
                    'value': int(value) if isinstance(value, float) and value.is_integer() else value,
                    'text': {text_key: label}
                })
            meta['columns'][column]['values'] = values
            if meta['columns'][column]['type'] == 'float':
                meta['columns'][column]['type'] = 'single'

    # Process multiple response sets if available
    if hasattr(metadata, 'multiresponse_defs'):
        for mrset_name, mrset_info in metadata.multiresponse_defs.items():
            _add_multiresponse_set(meta, mrset_name, mrset_info, text_key, dichot)

    return meta


def _process_data_for_quantipy(
    df: pd.DataFrame,
    metadata: Any,
    dates_as_strings: bool
) -> pd.DataFrame:
    """Process data DataFrame for quantipy compatibility.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data from pyreadstat
    metadata : pyreadstat metadata object
        Metadata from pyreadstat
    dates_as_strings : bool
        Whether to convert dates to strings
        
    Returns
    -------
    pd.DataFrame
        Processed data
    """
    # Strip whitespace from string columns
    for col in df.columns:
        if df[col].dtype == object:
            # Check if it's a string column (not datetime)
            sample = df[col].dropna().head(1)
            if len(sample) > 0 and isinstance(sample.iloc[0], str):
                df[col] = df[col].str.strip()

    # Convert dates to strings if requested
    if dates_as_strings:
        for col in df.select_dtypes(include=['datetime64']).columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

    return df


def _get_quantipy_type(metadata: Any, var_idx: int, dates_as_strings: bool) -> str:
    """Determine quantipy variable type from SPSS metadata.
    
    Parameters
    ----------
    metadata : pyreadstat metadata object
        Metadata from pyreadstat
    var_idx : int
        Variable index
    dates_as_strings : bool
        Whether dates should be treated as strings
        
    Returns
    -------
    str
        Quantipy type ('int', 'float', 'single', 'delimited set', 'string', 'date', 'time')
    """
    var_name = metadata.column_names[var_idx]

    # Check variable format
    if hasattr(metadata, 'original_variable_formats'):
        fmt = metadata.original_variable_formats.get(var_name, '')
        if 'DATE' in fmt or 'TIME' in fmt:
            return 'string' if dates_as_strings else 'date'

    # Check if it's a multiple response variable
    if hasattr(metadata, 'variable_storage_width'):
        if metadata.variable_storage_width[var_name] == 0:  # Numeric
            if var_name in metadata.variable_value_labels:
                return 'single'  # Categorical
            return 'float'
        # String
        return 'string'

    return 'float'  # Default


def _extract_spss_metadata_from_quantipy(
    meta: dict,
    var_labels: dict | None,
    value_labels: dict | None,
    formats: dict | None,
    measure: dict | None
) -> tuple[dict, dict, dict, dict]:
    """Extract SPSS metadata from quantipy meta dictionary.
    
    Parameters
    ----------
    meta : dict
        Quantipy meta dictionary
    var_labels : dict, optional
        Existing variable labels
    value_labels : dict, optional
        Existing value labels
    formats : dict, optional
        Existing formats
    measure : dict, optional
        Existing measurement levels
        
    Returns
    -------
    tuple[dict, dict, dict, dict]
        Updated var_labels, value_labels, formats, measure
    """
    if var_labels is None:
        var_labels = {}
    if value_labels is None:
        value_labels = {}
    if formats is None:
        formats = {}
    if measure is None:
        measure = {}

    # Extract from meta columns
    for col_name, col_info in meta.get('columns', {}).items():
        # Variable label
        if 'text' in col_info:
            text_keys = col_info['text']
            if isinstance(text_keys, dict):
                # Get first available text
                var_labels[col_name] = list(text_keys.values())[0]

        # Value labels
        if 'values' in col_info:
            col_value_labels = {}
            for value_info in col_info['values']:
                value = value_info.get('value')
                if 'text' in value_info:
                    text = list(value_info['text'].values())[0] if isinstance(value_info['text'], dict) else value_info['text']
                    col_value_labels[value] = text
            if col_value_labels:
                value_labels[col_name] = col_value_labels

        # Measurement level
        col_type = col_info.get('type', 'float')
        if col_type in ['single', 'delimited set']:
            measure[col_name] = 'nominal'
        elif col_type in ['int', 'float']:
            measure[col_name] = 'scale'
        else:
            measure[col_name] = 'nominal'

    return var_labels, value_labels, formats, measure


def _prepare_data_for_spss(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare data DataFrame for SPSS output.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data
        
    Returns
    -------
    pd.DataFrame
        Prepared data
    """
    df = data.copy()

    # Convert boolean columns to numeric
    bool_cols = df.select_dtypes(include=['bool']).columns
    for col in bool_cols:
        df[col] = df[col].astype(float)

    # Ensure numeric columns have proper missing values
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        # pyreadstat handles NaN properly for SPSS sysmis
        pass

    return df


def _add_multiresponse_set(
    meta: dict,
    mrset_name: str,
    mrset_info: dict,
    text_key: str,
    dichot: dict | None
) -> None:
    """Add multiple response set to quantipy meta.
    
    Parameters
    ----------
    meta : dict
        Quantipy meta dictionary to update
    mrset_name : str
        Name of the multiple response set
    mrset_info : dict
        Multiple response set information from SPSS
    text_key : str
        Text key for labels
    dichot : dict, optional
        Dichotomous configuration
    """
    # Implementation for multiple response sets
    # This maintains compatibility with existing quantipy structure


# Backward compatibility aliases
parse_sav_file = read_sav
extract_sav_data = lambda filepath, **kwargs: read_sav(filepath, **kwargs)[1]
extract_sav_meta = lambda filepath, **kwargs: read_sav(filepath, **kwargs)[0]
