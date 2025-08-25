"""SPSS file reader for quantipy3.

This module provides functionality for reading and parsing SPSS .sav files,
extracting both data and metadata to create quantipy-compatible data structures
with support for multiple response sets and dichotomous variables.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pyreadstat

# savReaderWriter import removed - using pyreadstat exclusively
from quantipy.core.tools.dp.prep import condense_dichotomous_set, start_meta
from quantipy.core.tools.dp.spss.modern_io import read_sav as modern_read_sav


def parse_sav_file(filename, path=None, name="", io_locale="en_US.UTF-8", io_utf8=True, dichot=None,
                   dates_as_strings=False, text_key="en-GB", engine='pyreadstat'):
    """ Parses a .sav file and returns a touple of Data and Meta

        Parameters
        ----------
        filename : str, name of sav file
            path : str, the path to the sav file
            name : str, a name for the sav (stored in the meta)
        ioLocale : str, the locale that SavReaderWriter uses
          ioUtf8 : bool, Boolean that indicates the mode in which text
                         communicated to or from the I/O Module will be.
          dichot : dicit, default=None
                   The values to use for True/False in dichotomous sets
dates_as_strings : bool, default=False
                   If True then all dates from the input SAV will be treated as
                   Quantipy strings.
        text_key : str, default="main"
                   The text_key that all labels should be stored under.

        Returns
        -------
        (data, meta) : The data is a Pandas Dataframe
                     : The meta is a JSON dictionary
    """
    filepath="{}{}".format(path or '', filename)
    filepath = os.path.abspath(filepath)

    # Always use modern pyreadstat implementation
    meta, data = modern_read_sav(
        filepath=filepath,
        name=name,
        ioLocale=io_locale,
        ioUtf8=io_utf8,
        dichot=dichot,
        dates_as_strings=dates_as_strings,
        text_key=text_key
    )
    return (meta, data)

def extract_sav_data(sav_file, io_locale='en_US.UTF-8', io_utf8=True, engine='pyreadstat'):
    """
    Extract data from SPSS file.

    Note: This function now always uses pyreadstat regardless of engine parameter
    for Python 3.10+ compatibility. The engine parameter is kept for backward
    compatibility but is ignored.
    """
    # Always use pyreadstat for modern Python compatibility
    encoding = io_locale.split(".")[-1] if "." in io_locale else "UTF-8"
    df, meta = pyreadstat.read_sav(sav_file, encoding=encoding if io_utf8 else None)

    # Process string columns
    for column in df.columns:
        if df[column].dtype == object:
            values = df[column].dropna().values
            if len(values) > 0 and isinstance(values[0], str):
                df[column] = df[column].str.strip()

    return df

def extract_sav_meta(sav_file, name="", data=None, io_locale='en_US.UTF-8',
                     io_utf8=True, dichot=None, dates_as_strings=False,
                     text_key="en-GB", engine='pyreadstat'):
    """
    Extract metadata from SPSS file.

    Note: This function now always uses pyreadstat. The engine parameter
    is kept for backward compatibility but is ignored.
    """
    # Always use pyreadstat - engine parameter ignored
    if True:  # Keeping indentation for minimal changes
        df, metadata = pyreadstat.read_sav(sav_file, encoding=io_locale.split(".")[-1], metadataonly=True)
        meta = start_meta(text_key=text_key)

        meta['info']['text'] = f'Converted from SAV file {name}.'
        meta['info']['from_source'] = {'pandas_reader':'sav'}
        meta['sets']['data file']['items'] = [
            f'columns@{varName}'
            for varName in metadata.column_names]

        for index, column in enumerate(metadata.column_names):
            meta['columns'][column] = {}
            meta['columns'][column]['name'] = column
            meta['columns'][column]['parent'] = {}
            if column in metadata.variable_value_labels:
                meta['columns'][column]['values'] = []
                meta['columns'][column]['type'] = "single"
                for value, text in metadata.variable_value_labels[column].items():
                    values = {'text': {text_key: str(text)},
                            'value': int(value)}
                    meta['columns'][column]['values'].append(values)
                    # if user has stored single answer data as a string rather than number
                    # we convert it to floats and store non convertables as nan (with coerce)
                    if column in data.columns and data[column].dtype == 'O':
                        data[column] = pd.to_numeric(data[column], errors='coerce', downcast='float')
            elif column in metadata.original_variable_types:
                f = metadata.original_variable_types[column]
                if 'DATETIME' in f:
                    if dates_as_strings:
                        # DATETIME fields from SPSS are currently
                        # being read in as strings because there's an
                        # as-yet undetermined discrepancy between the
                        # input and output dates if datetime64 is used
                        meta['columns'][column]['type'] = 'string'
                    else:
                        meta['columns'][column]['type'] = 'date'
                        data[column] = pd.to_datetime(data[column])
                elif f.startswith('A'):
                    meta['columns'][column]['type'] = 'string'
                elif '.' in f:
                    meta['columns'][column]['type'] = "float"
                else:
                    meta['columns'][column]['type'] = "int"

            # add the variable label to the meta
            meta['columns'][column]['text'] = {text_key : metadata.column_labels[index]}

        # Note: The deprecated savReaderWriter code block has been removed.
        # All SPSS operations now use pyreadstat exclusively for Python 3.10+ compatibility.

        for mrset in metadata.multRespDefs:
            # meta['masks'][mrset] = {}
            # 'D' is "multiple dichotomy sets" in SPSS
            # 'C' is "multiple category sets" in SPSS
            var_names = list(metadata.multRespDefs[mrset]['varNames'])
            # Find the index where there delimited set should be inserted
            # into data, which is immediately prior to the start of the
            # dichotomous set columns
            dls_idx = data.columns.tolist().index(var_names[0])
            if metadata.multRespDefs[mrset]['setType'] == 'C':
                # Raise if value object of columns is not equal
                if not all(meta['columns'][v]['values'] == meta['columns'][var_names[0]]['values']
                        for v in var_names):
                    msg = 'Columns must have equal values to be combined in a set: {}'
                    raise ValueError(msg.format(var_names))
                # Concatenate columns to set
                df_str = data[var_names].astype('str')
                dls = df_str.apply(lambda x: ';'.join([
                    v.replace('.0', '') for v in x.tolist()
                    if v not in ['nan', 'None']]),
                    axis=1) + ';'
                dls.replace({';': np.NaN}, inplace=True)
                # Get value object
                values = meta['columns'][varNames[0]]['values']

            elif metadata.multRespDefs[mrset]['setType'] == 'D':
                # Generate the delimited set from the dichotomous set
                dls = condense_dichotomous_set(data[varNames], values_from_labels=False, **dichot)
                # Get value object
                values = [{
                            'text': {text_key: metadata.varLabels[varName]},
                            'value': int(v)
                        }
                        for v, varName in enumerate(varNames, start=1)]
            else:
                continue
            # Insert the delimited set into data
            data.insert(dls_idx, mrset, dls)
            # Generate the column meta for the new delimited set
            meta['columns'][mrset] = {
                'name': mrset,
                'type': 'delimited set',
                'text': {text_key: metadata.multRespDefs[mrset]['label']},
                'parent': {},
                'values': values}
            # Add the new delimited set to the 'data file' set
            df_items = meta['sets']['data file']['items']
            df_items.insert(
                df_items.index(f'columns@{varNames[0]}'),
                f'columns@{mrset}')

            data = data.drop(varNames, axis=1)
            for varName in varNames:
                df_items.remove(f'columns@{varName}')
                del meta['columns'][varName]

        return meta, data
    return None
