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
    
    def crosstab(self, x: str, y: str = "@", pct: bool = False, pct_type: str = "total", margins: bool = False) -> pd.DataFrame:
        """
        Create a crosstab using pandas after Quantipy conversion.
        
        This is the main analysis method for creating frequency tables
        and cross-tabulations with various percentage options.
        
        Parameters:
        -----------
        x : str
            Column name for rows (e.g., 'gender')
        y : str  
            Column name for columns, or "@" for simple frequency table
        pct : bool
            If True, show percentages instead of counts
        pct_type : str
            Type of percentage calculation:
            - "total": percentage of total sample (default)
            - "column" or "col": column percentages (each column sums to 100%)
            - "row": row percentages (each row sums to 100%)
        margins : bool
            If True, add row and column totals
        
        Returns:
        --------
        pd.DataFrame
            Crosstab result with proper labels
            
        Examples:
        ---------
        >>> # Simple frequency table
        >>> helper.crosstab('gender', pct=True)
        
        >>> # Cross-tabulation with column percentages
        >>> helper.crosstab('gender', 'age_group', pct=True, pct_type='column')
        
        >>> # With row totals
        >>> helper.crosstab('gender', 'age_group', margins=True)
        """
        if self.ds is None:
            print("No data loaded. Use load_csv() first.")
            return pd.DataFrame()
            
        # Ensure columns are categorical
        if x not in self.value_labels:
            self.categorize([x])
        if y != "@" and y not in self.value_labels:
            self.categorize([y])
        
        # Get the data - ensure we're getting the actual column
        if x not in self.ds._data.columns:
            print(f"Error: Column '{x}' not found in data")
            return pd.DataFrame()
            
        x_data = self.ds._data[x]
        
        if y == "@":
            # Simple frequency table
            counts = x_data.value_counts().sort_index()
            
            if len(counts) == 0:
                print(f"WARNING: No data found for column '{x}'")
                return pd.DataFrame()
            
            if pct:
                total = counts.sum()
                percentages = (counts / total * 100).round(1)
                result = percentages.to_frame(name='%')
            else:
                result = counts.to_frame(name='Count')
            
            # Apply labels
            if x in self.value_labels and self.value_labels[x]:
                x_labels = self.value_labels[x]
                result.index = result.index.map(lambda i: x_labels.get(i, str(i)))
            result.index.name = x
                
        else:
            # Cross-tabulation
            if y not in self.ds._data.columns:
                print(f"Error: Column '{y}' not found in data")
                return pd.DataFrame()
                
            y_data = self.ds._data[y]
            
            if pct:
                # Determine normalization type
                if pct_type.lower() in ["column", "col"]:
                    normalize = "columns"
                elif pct_type.lower() == "row":
                    normalize = "index" 
                else:  # "total" or any other value
                    normalize = "all"
                
                result = pd.crosstab(x_data, y_data, normalize=normalize, margins=margins) * 100
            else:
                result = pd.crosstab(x_data, y_data, margins=margins)
            
            # Replace codes with labels
            if x in self.value_labels and self.value_labels[x]:
                x_labels = self.value_labels[x]
                result.index = result.index.map(lambda i: x_labels.get(i, str(i)))
                result.index.name = x
                
            if y in self.value_labels and self.value_labels[y]:
                y_labels = self.value_labels[y]
                result.columns = result.columns.map(lambda i: y_labels.get(i, str(i)))
                result.columns.name = y
            
        return result