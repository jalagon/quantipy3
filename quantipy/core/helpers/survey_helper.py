"""
Survey Helper Module - Simplified interface for quantipy survey analysis.

This module provides a user-friendly wrapper around quantipy's core functionality,
making it easier to perform common survey analysis tasks like crosstabs, frequency
tables, and data loading.
"""
from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quantipy.core.dataset import DataSet


class SurveyHelper:
    """
    Simplified helper wrapper for common Quantipy survey analysis operations.
    
    This class provides an easy-to-use interface for:
    - Loading CSV data
    - Converting categorical variables
    - Creating crosstabs with various percentage options
    - Auto-detecting survey question types
    
    Examples:
    ---------
    >>> # Load data from CSV
    >>> helper = SurveyHelper.from_csv('survey_data.csv')
    >>> helper.info()
    
    >>> # Auto-detect and convert categorical variables
    >>> helper.auto_categorize()
    
    >>> # Create frequency table
    >>> helper.crosstab('gender', pct=True)
    
    >>> # Create crosstab with column percentages
    >>> helper.crosstab('gender', 'age_group', pct=True, pct_type='column')
    """
    
    def __init__(self, df: pd.DataFrame | None = None, name: str = "survey_data"):
        """
        Initialize with a DataFrame and auto-create a DataSet.
        Can be initialized empty and loaded later with load_csv().
        
        Parameters:
        -----------
        df : pd.DataFrame, optional
            Source DataFrame with survey data
        name : str
            Dataset name for identification
        """
        self.name = name
        self.value_labels: dict[str, dict[int, str]] = {}  # Store value labels for display
        self.df = None
        self.ds = None
        
        if df is not None:
            self._setup_dataset(df, name)
    
    def _setup_dataset(self, df: pd.DataFrame, name: str) -> None:
        """Setup the dataset with lazy import to avoid circular imports."""
        from quantipy.core.dataset import DataSet
        self.df = df.copy()
        self.ds = DataSet(name)
        self.ds.from_components(self.df)
    
    @classmethod
    def from_csv(cls, csv_path: str, name: str | None = None, encoding: str = 'utf-8', **kwargs) -> 'SurveyHelper':
        """
        Create a SurveyHelper by loading data from a CSV file.
        
        Parameters:
        -----------
        csv_path : str
            Path to the CSV file
        name : str, optional
            Dataset name (defaults to filename without extension)
        encoding : str
            File encoding (default: 'utf-8')
        **kwargs : dict
            Additional arguments passed to pd.read_csv()
        
        Returns:
        --------
        SurveyHelper
            Initialized helper with loaded data
            
        Examples:
        ---------
        >>> helper = SurveyHelper.from_csv('survey.csv')
        >>> helper = SurveyHelper.from_csv('data.csv', encoding='latin-1', sep=';')
        """
        # Auto-generate name from filename if not provided
        if name is None:
            import os
            name = os.path.splitext(os.path.basename(csv_path))[0]
        
        # Load CSV with pandas
        print(f"Loading CSV: {csv_path}")
        df = pd.read_csv(csv_path, encoding=encoding, **kwargs)
        print(f"Loaded {len(df)} rows × {len(df.columns)} columns")
        
        # Create and return helper
        helper = cls(name=name)
        helper._setup_dataset(df, name)
        return helper
    
    @classmethod
    def from_quantipy(cls, path_meta: str, path_data: str, name: str | None = None) -> 'SurveyHelper':
        """
        Create a SurveyHelper by loading quantipy format files.
        
        Parameters:
        -----------
        path_meta : str
            Path to the quantipy metadata JSON file
        path_data : str
            Path to the quantipy data CSV/pickle file
        name : str, optional
            Dataset name (defaults to filename without extension)
            
        Returns:
        --------
        SurveyHelper
            Initialized helper with loaded quantipy data
            
        Examples:
        ---------
        >>> helper = SurveyHelper.from_quantipy('survey_meta.json', 'survey_data.csv')
        """
        if name is None:
            import os
            name = os.path.splitext(os.path.basename(path_meta))[0]
        
        print(f"Loading quantipy files: {path_meta}, {path_data}")
        
        # Create helper with empty dataset
        helper = cls(name=name)
        
        # Use quantipy's native loading
        from quantipy.core.dataset import DataSet
        helper.ds = DataSet(name)
        helper.ds.read_quantipy(path_meta, path_data)
        helper.df = helper.ds._data.copy()
        
        # Extract any existing categorical labels
        helper._extract_all_labels()
        
        print(f"Loaded {len(helper.df)} rows × {len(helper.df.columns)} columns")
        return helper
    
    @classmethod 
    def from_spss(cls, path: str, name: str | None = None) -> 'SurveyHelper':
        """
        Create a SurveyHelper by loading an SPSS .sav file.
        
        Parameters:
        -----------
        path : str
            Path to the SPSS .sav file
        name : str, optional
            Dataset name (defaults to filename without extension)
            
        Returns:
        --------
        SurveyHelper
            Initialized helper with loaded SPSS data
            
        Examples:
        ---------
        >>> helper = SurveyHelper.from_spss('survey.sav')
        """
        if name is None:
            import os
            name = os.path.splitext(os.path.basename(path))[0]
        
        print(f"Loading SPSS file: {path}")
        
        # Create helper with empty dataset
        helper = cls(name=name)
        
        # Use quantipy's native SPSS loading
        from quantipy.core.dataset import DataSet
        helper.ds = DataSet(name)
        helper.ds.read_spss(path)
        helper.df = helper.ds._data.copy()
        
        # Extract categorical labels from SPSS metadata
        helper._extract_all_labels()
        
        print(f"Loaded {len(helper.df)} rows × {len(helper.df.columns)} columns")
        return helper
    
    @classmethod
    def from_dimensions(cls, path_meta: str, path_data: str, name: str | None = None) -> 'SurveyHelper':
        """
        Create a SurveyHelper by loading Dimensions MDD/DDF files.
        
        Parameters:
        -----------
        path_meta : str
            Path to the Dimensions .mdd metadata file
        path_data : str
            Path to the Dimensions .ddf data file  
        name : str, optional
            Dataset name (defaults to filename without extension)
            
        Returns:
        --------
        SurveyHelper
            Initialized helper with loaded Dimensions data
            
        Examples:
        ---------
        >>> helper = SurveyHelper.from_dimensions('survey.mdd', 'survey.ddf')
        """
        if name is None:
            import os
            name = os.path.splitext(os.path.basename(path_meta))[0]
        
        print(f"Loading Dimensions files: {path_meta}, {path_data}")
        
        # Create helper with empty dataset
        helper = cls(name=name)
        
        # Use quantipy's native Dimensions loading
        from quantipy.core.dataset import DataSet
        helper.ds = DataSet(name)
        helper.ds.read_dimensions(path_meta, path_data)
        helper.df = helper.ds._data.copy()
        
        # Extract categorical labels from Dimensions metadata
        helper._extract_all_labels()
        
        print(f"Loaded {len(helper.df)} rows × {len(helper.df.columns)} columns")
        return helper
    
    @classmethod
    def from_csv(cls, csv_path: str, name: str | None = None, encoding: str = 'utf-8', 
                 auto_categorize: bool = True, categorical_threshold: int = 20,
                 delimited_delimiter: str = ';', quantipy_native: bool = True,
                 **kwargs) -> 'SurveyHelper':
        """
        Create a SurveyHelper by loading a CSV file with intelligent quantipy-native type inference.
        
        This method loads a CSV file and automatically:
        - Uses the first row as variable names (column headers)
        - Infers quantipy variable types (single, delimited set, int, float, string, date)
        - Detects delimited sets (multiple choice) with preserved order of mention
        - Creates proper quantipy metadata with value labels
        - Generates a fully compatible quantipy DataSet
        
        Parameters:
        -----------
        csv_path : str
            Path to the CSV file
        name : str, optional
            Dataset name (defaults to filename without extension)
        encoding : str
            File encoding (default: 'utf-8')
        auto_categorize : bool
            Whether to automatically detect single choice variables (default: True)
        categorical_threshold : int
            Maximum unique values for single choice auto-detection (default: 20)
        delimited_delimiter : str
            Delimiter for multiple choice detection (default: ';' - semicolon)
        quantipy_native : bool
            Create quantipy metadata structure vs pandas categorical (default: True)
        **kwargs : dict
            Additional arguments passed to pd.read_csv()
            
        Returns:
        --------
        SurveyHelper
            Initialized helper with loaded and typed CSV data
            
        Examples:
        ---------
        >>> # Load CSV with full quantipy intelligence
        >>> helper = SurveyHelper.from_csv('survey.csv')
        
        >>> # Detect multiple choice with custom delimiter
        >>> helper = SurveyHelper.from_csv('data.csv', delimited_delimiter=',')
        
        >>> # Disable auto-categorization for pure data types
        >>> helper = SurveyHelper.from_csv('data.csv', auto_categorize=False)
        
        >>> # European CSV format with quantipy intelligence
        >>> helper = SurveyHelper.from_csv('data.csv', sep=';', decimal=',')
        
        >>> # Then use with full quantipy functionality
        >>> crosstab = helper.crosstab('q1', 'gender')  # Uses proper quantipy metadata
        """
        import os
        import pandas as pd
        
        if name is None:
            name = os.path.splitext(os.path.basename(csv_path))[0]
        
        print(f"Loading CSV file: {csv_path}")
        
        # Load CSV with first row as headers
        try:
            df = pd.read_csv(csv_path, encoding=encoding, **kwargs)
        except UnicodeDecodeError:
            print(f"Encoding error with {encoding}, trying 'latin1'...")
            df = pd.read_csv(csv_path, encoding='latin1', **kwargs)
        
        print(f"Loaded {len(df)} rows × {len(df.columns)} columns")
        
        # Enhanced quantipy-native type inference
        if quantipy_native:
            df, quantipy_meta = cls._infer_quantipy_types(
                df, auto_categorize, categorical_threshold, delimited_delimiter
            )
            # Create helper with quantipy DataSet integration
            helper = cls._create_with_quantipy_meta(df, name, quantipy_meta)
        else:
            # Legacy pandas-style processing 
            df = cls._infer_and_convert_types(df, auto_categorize, categorical_threshold)
            helper = cls(df=df, name=name)
            if auto_categorize:
                helper._infer_categorical_labels()
        
        print(f"Type inference complete - {helper._get_quantipy_type_summary()}")
        return helper
    
    @staticmethod
    def _infer_and_convert_types(df: pd.DataFrame, auto_categorize: bool = True, 
                                categorical_threshold: int = 20) -> pd.DataFrame:
        """
        Infer and convert data types for CSV data.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input DataFrame with raw CSV data
        auto_categorize : bool
            Whether to convert variables with few unique values to categorical
        categorical_threshold : int
            Maximum unique values for auto-categorization
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with inferred and converted types
        """
        import pandas as pd
        import numpy as np
        
        df_typed = df.copy()
        
        for col in df_typed.columns:
            series = df_typed[col]
            
            # Skip if column is entirely NaN
            if series.isna().all():
                continue
            
            # Try to convert to numeric first
            numeric_series = pd.to_numeric(series, errors='coerce')
            
            # If most values converted successfully, it's numeric
            if numeric_series.notna().sum() / len(series) > 0.8:  # 80% success rate
                df_typed[col] = numeric_series
                
                # Check if it should be integer (no decimal places)
                # Only check is_integer() for float values, not already int values
                non_null_values = numeric_series.dropna()
                if len(non_null_values) > 0:
                    # If all values are already integers or float values that are whole numbers
                    if (non_null_values.apply(lambda x: isinstance(x, (int, np.integer)) or 
                                              (isinstance(x, (float, np.floating)) and x.is_integer())).all()):
                        df_typed[col] = df_typed[col].astype('Int64')  # Nullable integer
                continue
            
            # Check for date/datetime patterns
            try:
                datetime_series = pd.to_datetime(series, errors='coerce')
                if datetime_series.notna().sum() / len(series) > 0.8:  # 80% success rate
                    df_typed[col] = datetime_series
                    continue
            except:
                pass
            
            # For string/object columns, check if should be categorical
            if auto_categorize:
                unique_values = series.dropna().nunique()
                total_values = len(series.dropna())
                
                # Convert to categorical if:
                # 1. Few unique values (below threshold)
                # 2. High repetition (unique values < 50% of total)
                if (unique_values <= categorical_threshold or 
                    (total_values > 0 and unique_values / total_values < 0.5)):
                    df_typed[col] = df_typed[col].astype('category')
                    continue
            
            # Keep as string/object for text data
            df_typed[col] = df_typed[col].astype('string')
        
        return df_typed
    
    def _infer_categorical_labels(self) -> None:
        """
        Infer and store categorical labels from categorical columns.
        Creates value labels dictionary for categorical variables.
        """
        import pandas as pd
        
        if self.df is None:
            return
        
        for col in self.df.columns:
            if pd.api.types.is_categorical_dtype(self.df[col]):
                # Get unique categories and create numeric mapping
                categories = self.df[col].cat.categories.tolist()
                
                # Create numeric codes (1-based to match survey conventions)
                value_labels = {i + 1: str(cat) for i, cat in enumerate(categories)}
                self.value_labels[col] = value_labels
                
                # Convert categorical to numeric codes + 1 (1-based indexing)
                self.df[col] = self.df[col].cat.codes + 1
                # Replace -1 (pandas missing category code) with NaN
                self.df[col] = self.df[col].replace(0, pd.NA)
    
    def _get_type_summary(self) -> str:
        """
        Get a summary of inferred data types.
        
        Returns:
        --------
        str
            Summary string of data types
        """
        if self.df is None:
            return "No data loaded"
        
        type_counts = {}
        for col in self.df.columns:
            dtype_str = str(self.df[col].dtype)
            if dtype_str.startswith('int'):
                type_key = 'integer'
            elif dtype_str.startswith('float'):
                type_key = 'numeric'
            elif dtype_str.startswith('datetime'):
                type_key = 'datetime'
            elif dtype_str == 'category':
                type_key = 'categorical'
            elif dtype_str == 'string':
                type_key = 'text'
            else:
                type_key = 'other'
            
            type_counts[type_key] = type_counts.get(type_key, 0) + 1
        
        # Add categorical from value_labels (for converted categoricals)
        if hasattr(self, 'value_labels') and self.value_labels:
            categorical_from_labels = len(self.value_labels)
            if categorical_from_labels > 0:
                type_counts['categorical'] = type_counts.get('categorical', 0) + categorical_from_labels
        
        summary_parts = []
        for type_name, count in type_counts.items():
            summary_parts.append(f"{count} {type_name}")
        
        return ", ".join(summary_parts)
    
    @staticmethod
    def _infer_quantipy_types(df: pd.DataFrame, auto_categorize: bool = True,
                             categorical_threshold: int = 20, 
                             delimited_delimiter: str = ';') -> tuple[pd.DataFrame, dict]:
        """
        Infer quantipy-native variable types and create proper metadata structure.
        
        Returns:
        --------
        tuple[pd.DataFrame, dict]
            Processed DataFrame and quantipy metadata dictionary
        """
        import pandas as pd
        import numpy as np
        from collections import OrderedDict
        
        df_processed = df.copy()
        quantipy_meta = {
            'columns': OrderedDict(),
            'info': {'dataset': {'name': 'CSV Import'}},
            'lib': {'default text': 'en-GB', 'values': {}},
            'sets': {},
            'type': 'pandas.DataFrame'
        }
        
        for col in df_processed.columns:
            series = df_processed[col]
            col_meta = {
                'name': col,
                'text': {'en-GB': col},  # Use column name as label
                'parent': {}
            }
            
            # Detect delimited sets (multiple choice) - highest priority
            if series.dtype == 'object' and delimited_delimiter:
                delimited_detected = SurveyHelper._detect_delimited_set(series, delimited_delimiter)
                if delimited_detected:
                    unique_values, value_labels = delimited_detected
                    col_meta['type'] = 'delimited set'
                    col_meta['values'] = [
                        {'text': {'en-GB': label}, 'value': value}
                        for value, label in value_labels.items()
                    ]
                    # Keep delimited data as string for quantipy
                    df_processed[col] = df_processed[col].astype('string')
                    quantipy_meta['columns'][col] = col_meta
                    continue
            
            # Try numeric conversion
            numeric_series = pd.to_numeric(series, errors='coerce')
            numeric_success_rate = numeric_series.notna().sum() / len(series) if len(series) > 0 else 0
            
            if numeric_success_rate > 0.8:  # 80% success threshold
                df_processed[col] = numeric_series
                
                # Check if should be integer
                non_null_values = numeric_series.dropna()
                if len(non_null_values) > 0:
                    is_integer = (non_null_values.apply(lambda x: isinstance(x, (int, np.integer)) or 
                                                       (isinstance(x, (float, np.floating)) and x.is_integer())).all())
                    if is_integer:
                        col_meta['type'] = 'int'
                        df_processed[col] = df_processed[col].astype('Int64')  # Nullable integer
                    else:
                        col_meta['type'] = 'float'
                else:
                    col_meta['type'] = 'int'  # Default for empty numeric
                quantipy_meta['columns'][col] = col_meta
                continue
            
            # Try datetime conversion
            try:
                datetime_series = pd.to_datetime(series, errors='coerce')
                datetime_success_rate = datetime_series.notna().sum() / len(series) if len(series) > 0 else 0
                if datetime_success_rate > 0.8:
                    df_processed[col] = datetime_series
                    col_meta['type'] = 'date'
                    quantipy_meta['columns'][col] = col_meta
                    continue
            except:
                pass
            
            # Check for single choice (categorical) if auto_categorize enabled
            if auto_categorize:
                unique_values = series.dropna().nunique()
                total_values = len(series.dropna())
                
                if (unique_values <= categorical_threshold or 
                    (total_values > 0 and unique_values / total_values < 0.5)):
                    
                    # Create single choice quantipy metadata
                    col_meta['type'] = 'single'
                    unique_vals = series.dropna().unique()
                    
                    # Create value labels (1-based indexing)
                    value_labels = []
                    for i, val in enumerate(sorted(unique_vals), 1):
                        value_labels.append({
                            'text': {'en-GB': str(val)},
                            'value': i
                        })
                    
                    col_meta['values'] = value_labels
                    
                    # Convert data to numeric codes (1-based)
                    value_map = {val: i for i, val in enumerate(sorted(unique_vals), 1)}
                    df_processed[col] = df_processed[col].map(value_map).astype('Int64')
                    
                    quantipy_meta['columns'][col] = col_meta
                    continue
            
            # Default to string type
            col_meta['type'] = 'string'
            df_processed[col] = df_processed[col].astype('string')
            quantipy_meta['columns'][col] = col_meta
        
        return df_processed, quantipy_meta
    
    @staticmethod
    def _detect_delimited_set(series: pd.Series, delimiter: str) -> tuple[set, dict] | None:
        """
        Detect if a series contains delimited set data (multiple choice).
        
        Returns:
        --------
        tuple[set, dict] | None
            (unique_values_set, value_labels_dict) if delimited set detected, None otherwise
        """
        # Check for delimiter presence in non-null values
        non_null = series.dropna()
        if len(non_null) == 0:
            return None
        
        # Count how many values contain the delimiter
        delimiter_count = non_null.str.contains(delimiter, regex=False, na=False).sum()
        delimiter_ratio = delimiter_count / len(non_null)
        
        # If at least 20% of values contain delimiter, likely a delimited set
        if delimiter_ratio >= 0.2:
            all_values = set()
            
            # Extract all unique values from delimited strings
            for val in non_null:
                if pd.notna(val) and delimiter in str(val):
                    # Split and clean (remove empty strings and whitespace)
                    parts = [p.strip() for p in str(val).split(delimiter) if p.strip()]
                    for part in parts:
                        # Try to convert to int if possible, otherwise keep as string
                        try:
                            all_values.add(int(part))
                        except ValueError:
                            all_values.add(part)
            
            if all_values:
                # Create value labels - use the values themselves as labels if they're strings
                # or generic labels if they're numbers
                value_labels = {}
                for val in sorted(all_values):
                    if isinstance(val, (int, float)):
                        value_labels[val] = f"Option {val}"
                    else:
                        value_labels[val] = str(val)
                
                return all_values, value_labels
        
        return None
    
    @classmethod
    def _create_with_quantipy_meta(cls, df: pd.DataFrame, name: str, 
                                  quantipy_meta: dict) -> 'SurveyHelper':
        """
        Create SurveyHelper with quantipy DataSet integration.
        """
        helper = cls(name=name)
        
        # Create quantipy DataSet with proper metadata
        from quantipy.core.dataset import DataSet
        helper.ds = DataSet(name)
        helper.ds._data = df
        helper.ds._meta = quantipy_meta
        helper.df = df.copy()
        
        # Extract value labels for display purposes
        helper._extract_quantipy_labels()
        
        return helper
    
    def _extract_quantipy_labels(self) -> None:
        """Extract value labels from quantipy metadata structure."""
        if not hasattr(self, 'ds') or not self.ds or not hasattr(self.ds, '_meta'):
            return
        
        for col, col_meta in self.ds._meta.get('columns', {}).items():
            if col_meta.get('type') == 'single' and 'values' in col_meta:
                # Extract labels from quantipy values structure
                labels = {}
                for value_item in col_meta['values']:
                    value = value_item['value']
                    text = value_item['text'].get('en-GB', str(value))
                    labels[value] = text
                self.value_labels[col] = labels
            elif col_meta.get('type') == 'delimited set' and 'values' in col_meta:
                # Extract labels for delimited sets too
                labels = {}
                for value_item in col_meta['values']:
                    value = value_item['value']
                    text = value_item['text'].get('en-GB', str(value))
                    labels[value] = text
                self.value_labels[col] = labels
    
    def _get_quantipy_type_summary(self) -> str:
        """Get summary of quantipy variable types."""
        if not hasattr(self, 'ds') or not self.ds or not hasattr(self.ds, '_meta'):
            return self._get_type_summary()  # Fallback to pandas summary
        
        type_counts = {}
        for col_meta in self.ds._meta.get('columns', {}).values():
            qtype = col_meta.get('type', 'unknown')
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        summary_parts = []
        for type_name, count in sorted(type_counts.items()):
            summary_parts.append(f"{count} {type_name}")
        
        return ", ".join(summary_parts)
    
    def load_csv(self, csv_path: str, name: str | None = None, encoding: str = 'utf-8', **kwargs) -> 'SurveyHelper':
        """
        Load data from a CSV file into this helper instance.
        
        Parameters:
        -----------
        csv_path : str
            Path to the CSV file
        name : str, optional
            Dataset name (defaults to current name or filename)
        encoding : str
            File encoding (default: 'utf-8')
        **kwargs : dict
            Additional arguments passed to pd.read_csv()
        
        Returns:
        --------
        self
            Returns self for method chaining
            
        Examples:
        ---------
        >>> helper = SurveyHelper()
        >>> helper.load_csv('survey.csv').auto_categorize()
        """
        # Auto-generate name from filename if not provided
        if name is None:
            if self.name == "survey_data":
                import os
                name = os.path.splitext(os.path.basename(csv_path))[0]
            else:
                name = self.name
        
        # Load CSV with pandas
        print(f"Loading CSV: {csv_path}")
        self.df = pd.read_csv(csv_path, encoding=encoding, **kwargs)
        print(f"Loaded {len(self.df)} rows × {len(self.df.columns)} columns")
        
        # Setup dataset
        self._setup_dataset(self.df, name)
        self.name = name
        self.value_labels = {}  # Reset labels
        
        return self
    
    def info(self) -> None:
        """
        Display basic information about the dataset.
        
        Shows dataset shape, column names, data types, first few rows,
        and any categorical variables that have been converted.
        """
        if self.df is None:
            print("No data loaded. Use load_csv() or from_csv() first.")
            return
        
        print(f"Dataset: {self.name}")
        print(f"Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        print(f"Columns: {list(self.df.columns)}")
        print("\nData types:")
        print(self.df.dtypes)
        print("\nFirst 5 rows:")
        print(self.df.head())
        
        # Show categorical conversions if any
        if self.value_labels:
            print(f"\nCategorical variables: {list(self.value_labels.keys())}")
            for var, labels in self.value_labels.items():
                print(f"  {var}: {labels}")
    
    def categorize(self, columns: list[str]) -> 'SurveyHelper':
        """
        Convert specified columns to categoricals in Quantipy.
        
        This method converts text/string columns into coded categorical
        variables that quantipy can use for analysis, while storing the
        original text labels for display.
        
        Parameters:
        -----------
        columns : list[str]
            List of column names to convert to categorical
            
        Returns:
        --------
        self
            Returns self for method chaining
            
        Examples:
        ---------
        >>> helper.categorize(['gender', 'age_group', 'satisfaction'])
        """
        if self.ds is None:
            print("No data loaded. Use load_csv() first.")
            return self
            
        for col in columns:
            if col not in self.ds._data.columns:
                print(f"Warning: Column '{col}' not found in dataset")
                continue
                
            # Check if already categorical
            try:
                if self.ds._is_single(col):
                    # Already categorical, just get the labels
                    self._extract_labels(col)
                    continue
            except:
                pass
            
            # Convert to single (categorical) 
            try:
                self.ds.convert(col, 'single')
                # After conversion, extract the value labels
                self._extract_labels(col)
                    
            except Exception as e:
                print(f"Could not fully process {col}: {e}")
                # Even if conversion had issues, try to work with what we have
                self._extract_labels(col)
                
        return self
    
    def auto_categorize(self, max_unique: int = 10, exclude_numeric: bool = True) -> 'SurveyHelper':
        """
        Automatically detect and convert likely categorical columns.
        
        Uses heuristics to identify columns that should be treated as
        categorical variables (like gender, age groups, rating scales).
        
        Parameters:
        -----------
        max_unique : int
            Maximum number of unique values to consider as categorical (default: 10)
        exclude_numeric : bool
            If True, don't convert pure numeric columns unless they look like rating scales
            
        Returns:
        --------
        self
            Returns self for method chaining
            
        Examples:
        ---------
        >>> helper.auto_categorize()  # Use defaults
        >>> helper.auto_categorize(max_unique=15, exclude_numeric=False)
        """
        if self.df is None:
            print("No data loaded. Use load_csv() first.")
            return self
        
        categorical_candidates = []
        
        for col in self.df.columns:
            unique_count = self.df[col].nunique()
            
            # Skip if too many unique values
            if unique_count > max_unique:
                continue
                
            # Skip if purely numeric and exclude_numeric is True
            if exclude_numeric and pd.api.types.is_numeric_dtype(self.df[col]):
                # Check if it's a rating scale (small range of integers)
                if self.df[col].dtype in ['int64', 'float64']:
                    min_val, max_val = self.df[col].min(), self.df[col].max()
                    if (max_val - min_val) <= 10 and unique_count <= 7:
                        # Likely a rating scale, include it
                        categorical_candidates.append(col)
                continue
            
            categorical_candidates.append(col)
        
        if categorical_candidates:
            print(f"Auto-detected categorical columns: {categorical_candidates}")
            self.categorize(categorical_candidates)
        else:
            print("No categorical columns detected with current criteria.")
        
        return self
    
    def _extract_labels(self, col: str) -> None:
        """
        Extract value labels from the quantipy metadata.
        
        Internal method that reads the value mappings created by
        quantipy's conversion process and stores them for display.
        """
        try:
            # Get the values from metadata
            if col in self.ds._meta.get('columns', {}):
                col_meta = self.ds._meta['columns'][col]
                
                if 'values' in col_meta:
                    self.value_labels[col] = {}
                    values = col_meta['values']
                    
                    # Handle different value formats
                    if isinstance(values, list):
                        for i, val in enumerate(values):
                            if isinstance(val, dict):
                                code = val.get('value', val.get('code', i + 1))
                                label = val.get('text', str(code))
                                
                                # Extract text from language dict if needed
                                if isinstance(label, dict):
                                    # Get first available language or 'en-GB' if available
                                    label = label.get('en-GB', label.get('en', next(iter(label.values())) if label else str(code)))
                                           
                            else:
                                # Simple list of values
                                code = i + 1
                                label = str(val)
                            self.value_labels[col][code] = label
                    elif isinstance(values, dict):
                        # Direct code: label mapping
                        for code, label in values.items():
                            # Extract text from language dict if needed
                            if isinstance(label, dict):
                                label = label.get('en-GB', label.get('en', next(iter(label.values())) if label else str(code)))
                            self.value_labels[col][code] = str(label)
                        
        except Exception as e:
            print(f"Could not extract labels for {col}: {e}")
    
    def _extract_all_labels(self) -> None:
        """
        Extract value labels for all categorical columns from quantipy metadata.
        
        This method is called when loading data from quantipy native formats
        that already have metadata with categorical definitions.
        """
        if self.ds is None or self.ds._meta is None:
            return
            
        columns_meta = self.ds._meta.get('columns', {})
        for col_name, col_info in columns_meta.items():
            if col_info.get('type') == 'single' and 'values' in col_info:
                try:
                    self._extract_labels(col_name)
                except Exception as e:
                    print(f"Could not extract labels for {col_name}: {e}")
    
    def crosstab(self, x: str | list[str], y: str | list[str] = "@", pct: bool = False, pct_type: str = "total", 
                 margins: bool = False, show_base: bool = False, show_total: bool = True,
                 sort_rows: str = None, sort_columns: str = None) -> pd.DataFrame:
        """
        Create a crosstab using pandas after Quantipy conversion.
        
        This is the main analysis method for creating frequency tables
        and cross-tabulations with various percentage options.
        
        Parameters:
        -----------
        x : str or list[str]
            Column name(s) for rows (e.g., 'gender' or ['gender', 'age'])
        y : str or list[str]
            Column name(s) for columns, or "@" for simple frequency table
        pct : bool
            If True, show percentages instead of counts
        pct_type : str
            Type of percentage calculation:
            - "total": percentage of total sample (default)
            - "column" or "col": column percentages (each column sums to 100%)
            - "row": row percentages (each row sums to 100%)
        margins : bool
            If True, add row and column totals (pandas default margins)
        show_base : bool
            If True, add a "Base" row showing unweighted sample sizes (as first row)
        show_total : bool
            If True, add a "Total" column (default True for survey analysis, as first column)
        sort_rows : str
            Sort rows by values: 'ascending', 'descending', or None (default)
            Sorts based on Total column if present, otherwise first column
        sort_columns : str  
            Sort columns by values: 'ascending', 'descending', or None (default)
            Sorts based on Base row if present, otherwise first row
        
        Returns:
        --------
        pd.DataFrame
            Crosstab result with proper labels
            
        Examples:
        ---------
        >>> # Simple frequency table with Total column
        >>> helper.crosstab('gender', pct=True, show_total=True)
        
        >>> # Cross-tabulation with column percentages, Total column, and Base row
        >>> helper.crosstab('gender', 'age_group', pct=True, pct_type='column', 
        ...                 show_total=True, show_base=True)
        
        >>> # Nested variables with survey features
        >>> helper.crosstab(['gender', 'age_group'], 'satisfaction', pct=True,
        ...                 show_total=True, show_base=True)
        
        >>> # Full survey table with margins, Total, and Base
        >>> helper.crosstab('gender', 'age_group', pct=True, pct_type='column',
        ...                 margins=True, show_total=True, show_base=True)
        
        >>> # Nested columns: gender by age and satisfaction  
        >>> helper.crosstab('gender', ['age_group', 'satisfaction'])
        
        >>> # Both nested: gender+age by satisfaction+region
        >>> helper.crosstab(['gender', 'age'], ['satisfaction', 'region'])
        """
        if self.ds is None:
            print("No data loaded. Use load_csv() first.")
            return pd.DataFrame()
        
        # Convert to lists for consistent handling
        x_vars = [x] if isinstance(x, str) else x
        y_vars = [y] if isinstance(y, str) else y if y != "@" else ["@"]
        
        # Ensure all columns are categorical
        all_vars = x_vars + ([var for var in y_vars if var != "@"])
        for var in all_vars:
            if var not in self.value_labels:
                self.categorize([var])
        
        # Check all columns exist
        for var in all_vars:
            if var != "@" and var not in self.ds._data.columns:
                print(f"Error: Column '{var}' not found in data")
                return pd.DataFrame()
        
        # Handle single vs multiple variables
        if len(x_vars) == 1:
            x_data = self.ds._data[x_vars[0]]
        else:
            # Create multi-index for rows
            x_data = pd.MultiIndex.from_arrays(
                [self.ds._data[var] for var in x_vars], 
                names=x_vars
            )
        
        if y_vars == ["@"]:
            # Simple frequency table
            if len(x_vars) == 1:
                counts = x_data.value_counts().sort_index()
            else:
                # Multi-variable frequency - use Series with MultiIndex
                temp_df = pd.DataFrame(index=range(len(self.ds._data)))
                for i, var in enumerate(x_vars):
                    temp_df[var] = self.ds._data[var]
                counts = temp_df.groupby(x_vars).size().sort_index()
            
            if len(counts) == 0:
                print(f"WARNING: No data found for variables: {x_vars}")
                return pd.DataFrame()
            
            if pct:
                total = counts.sum()
                percentages = (counts / total * 100).round(1)
                result = percentages.to_frame(name='%')
            else:
                result = counts.to_frame(name='Count')
            
            # Apply labels for multi-index
            if len(x_vars) == 1 and x_vars[0] in self.value_labels:
                x_labels = self.value_labels[x_vars[0]]
                result.index = result.index.map(lambda i: x_labels.get(i, str(i)))
                result.index.name = x_vars[0]
            elif len(x_vars) > 1:
                # Apply labels to each level of multi-index
                new_index = result.index
                for level, var in enumerate(x_vars):
                    if var in self.value_labels:
                        labels = self.value_labels[var]
                        new_index = new_index.set_levels(
                            new_index.levels[level].map(lambda i: labels.get(i, str(i))), 
                            level=level
                        )
                result.index = new_index
                
        else:
            # Cross-tabulation with potentially multiple variables
            
            # Prepare row and column data for pd.crosstab
            # For single variables, pass the Series directly with None for names (pandas will use .name)
            # For multiple variables, pass as a list of Series with list of names
            if len(x_vars) == 1:
                row_data = self.ds._data[x_vars[0]]
                row_names = None  # Let pandas use the Series .name attribute
            else:
                row_data = [self.ds._data[var] for var in x_vars]
                row_names = x_vars
                
            if len(y_vars) == 1:
                col_data = self.ds._data[y_vars[0]]
                col_names = None  # Let pandas use the Series .name attribute
            else:
                col_data = [self.ds._data[var] for var in y_vars]
                col_names = y_vars
            
            if pct:
                # Determine normalization type
                if pct_type.lower() in ["column", "col"]:
                    normalize = "columns"
                elif pct_type.lower() == "row":
                    normalize = "index" 
                else:  # "total" or any other value
                    normalize = "all"
                
                result = pd.crosstab(
                    row_data, col_data, 
                    rownames=row_names, colnames=col_names,
                    normalize=normalize, margins=margins
                ) * 100
            else:
                result = pd.crosstab(
                    row_data, col_data,
                    rownames=row_names, colnames=col_names, 
                    margins=margins
                )
            
            # Apply labels to index (rows)
            if len(x_vars) == 1 and x_vars[0] in self.value_labels:
                x_labels = self.value_labels[x_vars[0]]
                result.index = result.index.map(lambda i: x_labels.get(i, str(i)))
            elif len(x_vars) > 1 and hasattr(result.index, 'levels'):
                # Multi-index rows
                new_index = result.index
                for level, var in enumerate(x_vars):
                    if var in self.value_labels:
                        labels = self.value_labels[var]
                        new_index = new_index.set_levels(
                            new_index.levels[level].map(lambda i: labels.get(i, str(i))), 
                            level=level
                        )
                result.index = new_index
                
            # Apply labels to columns
            if len(y_vars) == 1 and y_vars[0] in self.value_labels:
                y_labels = self.value_labels[y_vars[0]]
                result.columns = result.columns.map(lambda i: y_labels.get(i, str(i)))
            elif len(y_vars) > 1 and hasattr(result.columns, 'levels'):
                # Multi-index columns
                new_columns = result.columns
                for level, var in enumerate(y_vars):
                    if var in self.value_labels:
                        labels = self.value_labels[var]
                        new_columns = new_columns.set_levels(
                            new_columns.levels[level].map(lambda i: labels.get(i, str(i))), 
                            level=level
                        )
                result.columns = new_columns
        
        # Add Total column if requested
        if show_total and y_vars != ["@"]:
            if pct and pct_type.lower() in ["row"]:
                # For row percentages, Total column should be 100%
                result['Total'] = 100.0
            elif pct and pct_type.lower() in ["column", "col"]:
                # For column percentages, Total column should show row totals (counts)
                # Need to recalculate the original counts
                if len(x_vars) == 1 and len(y_vars) == 1:
                    # Simple case: recalculate row totals from original data
                    row_totals = self.ds._data.groupby(x_vars[0]).size()
                    if x_vars[0] in self.value_labels:
                        x_labels = self.value_labels[x_vars[0]]
                        row_totals.index = row_totals.index.map(lambda i: x_labels.get(i, str(i)))
                    result['Total'] = row_totals
                else:
                    # Complex case: sum the percentages (may not be perfect but reasonable)
                    result['Total'] = result.sum(axis=1)
            else:
                # For counts or total percentages, sum across columns
                result['Total'] = result.sum(axis=1)
        
        # Add Base row if requested  
        if show_base:
            # Calculate base counts for each column
            if y_vars == ["@"]:
                # For frequency tables, base is total count
                base_count = len(self.ds._data)
                base_row = pd.Series([base_count], index=['Base'], name='Base')
                result = pd.concat([result, base_row.to_frame().T])
            else:
                # For crosstabs, calculate base for each column
                if len(y_vars) == 1:
                    # Single column variable
                    base_counts = self.ds._data.groupby(y_vars[0]).size()
                    if y_vars[0] in self.value_labels:
                        y_labels = self.value_labels[y_vars[0]]
                        base_counts.index = base_counts.index.map(lambda i: y_labels.get(i, str(i)))
                    base_counts.name = 'Base'
                    
                    # Add Total column to base if show_total is True
                    if show_total:
                        base_counts['Total'] = base_counts.sum()
                        
                    result = pd.concat([result, base_counts.to_frame().T])
                else:
                    # Multiple column variables - create base for each combination
                    col_data = [self.ds._data[var] for var in y_vars]
                    if len(col_data) == 1:
                        base_counts = col_data[0].value_counts().sort_index()
                    else:
                        # Multi-index: count combinations
                        base_df = pd.DataFrame({var: self.ds._data[var] for var in y_vars})
                        base_counts = base_df.groupby(y_vars).size()
                    
                    base_counts.name = 'Base'
                    
                    # Add Total column to base if show_total is True
                    if show_total:
                        base_counts = pd.concat([base_counts, pd.Series([base_counts.sum()], index=['Total'])])
                        
                    result = pd.concat([result, base_counts.to_frame().T])
            
        # Reorder columns to put Total first if it exists
        if show_total and 'Total' in result.columns:
            cols = result.columns.tolist()
            cols.remove('Total')
            cols = ['Total'] + cols
            result = result[cols]
        
        # Reorder rows to put Base first if it exists
        if show_base and 'Base' in result.index:
            # Store the base row
            base_row = result.loc[['Base']]
            # Remove base from result
            result_without_base = result.drop('Base')
            # Concatenate with Base first
            result = pd.concat([base_row, result_without_base])
        
        # Apply sorting if requested
        if sort_rows:
            # Determine which column to sort by
            sort_col = 'Total' if 'Total' in result.columns else result.columns[0]
            
            # Exclude Base row from sorting if present
            if 'Base' in result.index:
                base_row = result.loc[['Base']]
                data_rows = result.drop('Base')
            else:
                base_row = None
                data_rows = result
            
            # Sort the data rows
            ascending = (sort_rows == 'ascending')
            data_rows = data_rows.sort_values(by=sort_col, ascending=ascending)
            
            # Recombine with Base row first if present
            if base_row is not None:
                result = pd.concat([base_row, data_rows])
            else:
                result = data_rows
        
        if sort_columns and y_vars != ["@"]:
            # Determine which row to sort by
            sort_row = 'Base' if 'Base' in result.index else result.index[0]
            
            # Get column values for sorting (excluding Total)
            if 'Total' in result.columns:
                total_col = result[['Total']]
                data_cols = result.drop('Total', axis=1)
            else:
                total_col = None
                data_cols = result
            
            # Sort the data columns
            ascending = (sort_columns == 'ascending')
            sort_values = data_cols.loc[sort_row]
            sorted_cols = sort_values.sort_values(ascending=ascending).index.tolist()
            data_cols = data_cols[sorted_cols]
            
            # Recombine with Total column first if present
            if total_col is not None:
                result = pd.concat([total_col, data_cols], axis=1)
            else:
                result = data_cols
        
        return result