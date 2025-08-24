"""
ExportManager - Handles all export and output operations for DataSet

This module provides a focused, SOLID-compliant implementation of export
and output functionality extracted from the monolithic DataSet class.

Following Single Responsibility Principle, this module handles:
- Native Quantipy format exports (.csv/.json)
- External format exports (SPSS, Dimensions, Forsta)
- Metadata exports and serialization
- Session management and snapshots
- Data splitting and component extraction
"""

import os
import json
import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Tuple
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

if TYPE_CHECKING:
    from quantipy.core.dataset import DataSet

# Import export utility functions
from quantipy.core.tools.dp.io import write_quantipy as w_quantipy
from quantipy.core.tools.dp.io import write_spss as w_spss
from quantipy.core.tools.dp.io import write_dimensions as w_dimensions
from quantipy.core.tools.dp.io import write_forsta_api as w_forsta_api


class ExportStrategy(ABC):
    """Abstract base class for export operations following Strategy pattern."""

    @abstractmethod
    def export(
        self, 
        dataset: "DataSet", 
        *args, 
        **kwargs
    ) -> Any:
        """
        Execute export operation on dataset.

        Args:
            dataset: DataSet instance to export
            *args: Strategy-specific positional arguments
            **kwargs: Strategy-specific keyword arguments

        Returns:
            Strategy-dependent return value
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this export strategy."""
        pass


class NativeExportStrategy(ExportStrategy):
    """Strategy for native Quantipy format exports."""

    def export(
        self, 
        dataset: "DataSet", 
        operation: str,
        **kwargs
    ) -> Any:
        """Execute native export operations."""
        if operation == "write_quantipy":
            return self._write_quantipy(dataset, **kwargs)
        elif operation == "split":
            return self._split(dataset, **kwargs)
        elif operation == "save":
            return self._save(dataset)
        else:
            raise ValueError(f"Unknown native export operation: {operation}")

    def _write_quantipy(
        self, 
        dataset: "DataSet",
        path_meta: Optional[str] = None,
        path_data: Optional[str] = None
    ) -> None:
        """Write data and meta components to .csv/.json files."""
        meta, data = dataset._meta, dataset._data
        
        if path_data is None and path_meta is None:
            # Use dataset's default path and name
            path = dataset.path or ''
            name = dataset.name
            path_meta = os.path.join(path, f'{name}.json')
            path_data = os.path.join(path, f'{name}.csv')
        elif path_data is not None and path_meta is not None:
            # Ensure proper extensions
            if not path_meta.endswith('.json'):
                path_meta = f'{path_meta}.json'
            if not path_data.endswith('.csv'):
                path_data = f'{path_data}.csv'
        else:
            raise ValueError("Must either specify or omit both 'path_meta' and 'path_data'!")

        w_quantipy(meta, data, path_meta, path_data)
        return None

    def _split(
        self, 
        dataset: "DataSet",
        save: bool = False
    ) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """Return meta and data components, optionally saving them."""
        meta, data = dataset._meta, dataset._data
        
        if save:
            path = dataset.path or ''
            name = dataset.name
            w_quantipy(meta, data, f'{path}{name}.json', f'{path}{name}.csv')
        
        return meta, data

    def _save(self, dataset: "DataSet") -> None:
        """Save current state for later recovery."""
        if dataset._data is None and dataset._meta is None:
            warnings.warn("No data/meta components found in the DataSet.")
            return None

        # Create a clone and store in cache
        ds_clone = dataset.clone()
        dataset._cache['savepoint'] = ds_clone.split()
        return None

    def get_strategy_name(self) -> str:
        return "native_export"


class ExternalFormatStrategy(ExportStrategy):
    """Strategy for external format exports (SPSS, Dimensions, Forsta)."""

    def export(
        self, 
        dataset: "DataSet", 
        operation: str,
        **kwargs
    ) -> Any:
        """Execute external format export operations."""
        if operation == "write_spss":
            return self._write_spss(dataset, **kwargs)
        elif operation == "write_dimensions":
            return self._write_dimensions(dataset, **kwargs)
        elif operation == "write_forsta":
            return self._write_forsta(dataset, **kwargs)
        elif operation == "write_forsta_api":
            return self._write_forsta_api(dataset, **kwargs)
        else:
            raise ValueError(f"Unknown external format operation: {operation}")

    def _write_spss(
        self,
        dataset: "DataSet",
        path_sav: Optional[str] = None,
        index: bool = True,
        text_key: Optional[str] = None,
        mrset_tag_style: str = '__',
        drop_delimited: bool = True,
        from_set: Optional[str] = None,
        verbose: bool = True
    ) -> None:
        """Export to SPSS .sav format."""
        dataset.set_encoding('cp1252')
        meta, data = dataset._meta, dataset._data
        
        if not text_key:
            text_key = dataset.text_key
        
        if not path_sav:
            path_sav = os.path.join(dataset.path or '', f'{dataset.name}.sav')
        else:
            if not path_sav.endswith('.sav'):
                path_sav = f'{path_sav}.sav'

        w_spss(
            meta, data, path_sav, index, text_key, 
            mrset_tag_style, drop_delimited, from_set, verbose
        )
        return None

    def _write_dimensions(
        self,
        dataset: "DataSet",
        path_mdd: Optional[str] = None,
        path_ddf: Optional[str] = None,
        text_key: Optional[str] = None,
        run: bool = True,
        clean_up: bool = True
    ) -> None:
        """Export to Dimensions .mdd/.ddf format."""
        ds_clone = dataset.clone()
        
        if not text_key:
            text_key = ds_clone.text_key
            
        if ds_clone._dimensions_comp:
            ds_clone.undimensionize()
            
        # Check against weak dupes and rename automatically
        ds_clone._rename_weak_dupes()
        
        # Apply Dimensions naming rules
        ds_clone.dimensionize()
        
        w_dimensions(ds_clone, path_mdd, path_ddf, text_key, run, clean_up)
        return None

    def _write_forsta(
        self,
        dataset: "DataSet",
        path_meta: str,
        path_data: str,
        schema_vars: Optional[List[str]] = None,
        verbose: bool = False
    ) -> None:
        """Export to Forsta format."""
        if not hasattr(dataset, 'write_allowed') or not dataset.write_allowed:
            raise PermissionError("Write operations not allowed for this dataset")

        # Export metadata as JSON
        meta_json = json.dumps(dataset._meta)
        with open(path_meta, 'w') as f:
            f.write(meta_json)
        
        # Export data as CSV
        dataset._data.to_csv(path_data)
        return None

    def _write_forsta_api(
        self,
        dataset: "DataSet",
        projectid: str,
        public_url: str,
        idp_url: str,
        client_id: str,
        client_secret: str,
        schema_vars: Optional[List[str]] = None
    ) -> Any:
        """Export to Forsta API."""
        return w_forsta_api(
            dataset, projectid, public_url, idp_url, 
            client_id, client_secret, schema_vars
        )

    def get_strategy_name(self) -> str:
        return "external_format"


class MetadataExportStrategy(ExportStrategy):
    """Strategy for metadata export and serialization operations."""

    def export(
        self, 
        dataset: "DataSet", 
        operation: str,
        **kwargs
    ) -> Any:
        """Execute metadata export operations."""
        if operation == "meta_to_json":
            return self._meta_to_json(dataset, **kwargs)
        elif operation == "export_meta_subset":
            return self._export_meta_subset(dataset, **kwargs)
        elif operation == "serialize_metadata":
            return self._serialize_metadata(dataset, **kwargs)
        else:
            raise ValueError(f"Unknown metadata export operation: {operation}")

    def _meta_to_json(
        self,
        dataset: "DataSet",
        key: Optional[str] = None,
        collection: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Union[str, None]:
        """Save metadata object as JSON."""
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                else:
                    return super(NumpyEncoder, self).default(obj)

        meta = dataset._meta
        
        # Determine what to export
        if key:
            k_suffix = f'@{key}'
        else:
            k_suffix = ''

        collection_map = {
            'columns': f'columns{k_suffix}',
            'masks': f'masks{k_suffix}',
            'sets': f'sets{k_suffix}',
            'lib': f'lib@values{k_suffix}',
        }

        if collection and collection not in collection_map:
            raise ValueError(f'collection must be one of {list(collection_map.keys())}')

        if key and not collection:
            raise ValueError("Must specify collection when providing key")

        # Extract the specified metadata
        if collection and key:
            export_data = meta[collection].get(key, {})
        elif collection:
            export_data = meta.get(collection, {})
        else:
            export_data = meta

        # Serialize to JSON
        json_output = json.dumps(export_data, cls=NumpyEncoder, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_output)
            return None
        else:
            return json_output

    def _export_meta_subset(
        self,
        dataset: "DataSet",
        variables: List[str],
        output_path: Optional[str] = None
    ) -> Union[Dict[str, Any], None]:
        """Export metadata for specific variables."""
        subset_meta = {
            'info': dataset._meta.get('info', {}),
            'lib': dataset._meta.get('lib', {}),
            'columns': {},
            'masks': {},
            'sets': {}
        }

        # Add variable-specific metadata
        for var in variables:
            if var in dataset._meta.get('columns', {}):
                subset_meta['columns'][var] = dataset._meta['columns'][var]
            if var in dataset._meta.get('masks', {}):
                subset_meta['masks'][var] = dataset._meta['masks'][var]

        # Add relevant sets
        for set_name, set_def in dataset._meta.get('sets', {}).items():
            items = set_def.get('items', [])
            relevant_items = [
                item for item in items 
                if any(var in item for var in variables)
            ]
            if relevant_items:
                subset_meta['sets'][set_name] = {**set_def, 'items': relevant_items}

        if output_path:
            with open(output_path, 'w') as f:
                json.dump(subset_meta, f, indent=2)
            return None
        else:
            return subset_meta

    def _serialize_metadata(
        self,
        dataset: "DataSet",
        format_type: str = 'json',
        compact: bool = False
    ) -> str:
        """Serialize complete metadata in various formats."""
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                else:
                    return super(NumpyEncoder, self).default(obj)

        if format_type.lower() == 'json':
            if compact:
                return json.dumps(dataset._meta, cls=NumpyEncoder, separators=(',', ':'))
            else:
                return json.dumps(dataset._meta, cls=NumpyEncoder, indent=2)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def get_strategy_name(self) -> str:
        return "metadata_export"


class SessionManagementStrategy(ExportStrategy):
    """Strategy for session management and recovery operations."""

    def export(
        self, 
        dataset: "DataSet", 
        operation: str,
        **kwargs
    ) -> Any:
        """Execute session management operations."""
        if operation == "save_session":
            return self._save_session(dataset, **kwargs)
        elif operation == "revert_session":
            return self._revert_session(dataset)
        elif operation == "backup_dataset":
            return self._backup_dataset(dataset, **kwargs)
        elif operation == "create_checkpoint":
            return self._create_checkpoint(dataset, **kwargs)
        else:
            raise ValueError(f"Unknown session management operation: {operation}")

    def _save_session(
        self,
        dataset: "DataSet",
        checkpoint_name: str = 'default'
    ) -> None:
        """Save current session state."""
        if dataset._data is None and dataset._meta is None:
            warnings.warn("No data/meta components found in the DataSet.")
            return None

        ds_clone = dataset.clone()
        if 'checkpoints' not in dataset._cache:
            dataset._cache['checkpoints'] = {}
        dataset._cache['checkpoints'][checkpoint_name] = ds_clone.split()
        return None

    def _revert_session(self, dataset: "DataSet") -> None:
        """Revert to previously saved session state."""
        if 'savepoint' not in dataset._cache:
            warnings.warn("No saved session DataSet file found!")
            return None
        
        dataset._meta, dataset._data = dataset._cache['savepoint']
        print(f'Reverted to last savepoint of {dataset.name}')
        return None

    def _backup_dataset(
        self,
        dataset: "DataSet",
        backup_path: str,
        include_cache: bool = False
    ) -> None:
        """Create complete dataset backup."""
        backup_data = {
            'name': dataset.name,
            'path': dataset.path,
            'filtered': dataset.filtered,
            'text_key': dataset.text_key,
            'meta': dataset._meta,
            'data': dataset._data.to_dict('records') if dataset._data is not None else None
        }
        
        if include_cache:
            backup_data['cache'] = dict(dataset._cache)

        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        return None

    def _create_checkpoint(
        self,
        dataset: "DataSet",
        checkpoint_name: str,
        description: str = ""
    ) -> None:
        """Create named checkpoint for recovery."""
        if 'checkpoints' not in dataset._cache:
            dataset._cache['checkpoints'] = {}
        
        checkpoint_data = {
            'meta': dataset._meta,
            'data': dataset._data,
            'timestamp': pd.Timestamp.now(),
            'description': description
        }
        
        dataset._cache['checkpoints'][checkpoint_name] = checkpoint_data
        return None

    def get_strategy_name(self) -> str:
        return "session_management"


class ReportGenerationStrategy(ExportStrategy):
    """Strategy for report generation and summary exports."""

    def export(
        self, 
        dataset: "DataSet", 
        operation: str,
        **kwargs
    ) -> Any:
        """Execute report generation operations."""
        if operation == "dataset_summary":
            return self._dataset_summary(dataset, **kwargs)
        elif operation == "variable_report":
            return self._variable_report(dataset, **kwargs)
        elif operation == "export_codebook":
            return self._export_codebook(dataset, **kwargs)
        else:
            raise ValueError(f"Unknown report generation operation: {operation}")

    def _dataset_summary(
        self,
        dataset: "DataSet",
        output_path: Optional[str] = None
    ) -> Union[Dict[str, Any], None]:
        """Generate comprehensive dataset summary report."""
        summary = {
            'dataset_info': {
                'name': dataset.name,
                'path': dataset.path,
                'text_key': dataset.text_key,
                'filtered': dataset.filtered
            },
            'data_info': {
                'shape': dataset._data.shape if dataset._data is not None else (0, 0),
                'memory_usage': dataset._data.memory_usage(deep=True).sum() if dataset._data is not None else 0
            },
            'variable_counts': {
                'total_variables': len(dataset.columns()) if hasattr(dataset, 'columns') else 0,
                'arrays': len(dataset.masks()) if hasattr(dataset, 'masks') else 0,
                'singles': len(dataset.singles()) if hasattr(dataset, 'singles') else 0,
                'delimited_sets': len(dataset.delimited_sets()) if hasattr(dataset, 'delimited_sets') else 0,
                'ints': len(dataset.ints()) if hasattr(dataset, 'ints') else 0,
                'floats': len(dataset.floats()) if hasattr(dataset, 'floats') else 0
            },
            'metadata_info': {
                'text_keys': list(dataset.valid_tks) if hasattr(dataset, 'valid_tks') else [],
                'lib_values': len(dataset._meta.get('lib', {}).get('values', {})) if dataset._meta else 0,
                'sets_count': len(dataset._meta.get('sets', {})) if dataset._meta else 0
            }
        }

        if output_path:
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            return None
        else:
            return summary

    def _variable_report(
        self,
        dataset: "DataSet",
        variables: Optional[List[str]] = None,
        output_path: Optional[str] = None
    ) -> Union[Dict[str, Any], None]:
        """Generate detailed variable report."""
        if variables is None:
            variables = dataset.columns() if hasattr(dataset, 'columns') else []

        report = {}
        for var in variables:
            var_info = {
                'type': dataset._get_type(var) if hasattr(dataset, '_get_type') else 'unknown',
                'label': dataset.text(var) if hasattr(dataset, 'text') else 'N/A',
            }
            
            if dataset._data is not None and var in dataset._data.columns:
                var_info.update({
                    'dtype': str(dataset._data[var].dtype),
                    'null_count': int(dataset._data[var].isnull().sum()),
                    'unique_count': int(dataset._data[var].nunique())
                })
                
                if dataset._data[var].dtype in ['int64', 'float64']:
                    var_info.update({
                        'min': float(dataset._data[var].min()),
                        'max': float(dataset._data[var].max()),
                        'mean': float(dataset._data[var].mean())
                    })

            report[var] = var_info

        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            return None
        else:
            return report

    def _export_codebook(
        self,
        dataset: "DataSet",
        output_path: str,
        format_type: str = 'html'
    ) -> None:
        """Export dataset codebook in various formats."""
        if format_type.lower() == 'html':
            self._export_html_codebook(dataset, output_path)
        elif format_type.lower() == 'csv':
            self._export_csv_codebook(dataset, output_path)
        else:
            raise ValueError(f"Unsupported codebook format: {format_type}")

    def _export_html_codebook(
        self,
        dataset: "DataSet",
        output_path: str
    ) -> None:
        """Export codebook as HTML."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Codebook - {dataset.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .variable {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; }}
                .var-name {{ font-weight: bold; color: #333; }}
                .var-label {{ color: #666; font-style: italic; }}
                .var-type {{ color: #009; }}
            </style>
        </head>
        <body>
            <h1>Dataset Codebook: {dataset.name}</h1>
            <p>Generated on: {pd.Timestamp.now()}</p>
        """

        variables = dataset.columns() if hasattr(dataset, 'columns') else []
        for var in variables:
            var_type = dataset._get_type(var) if hasattr(dataset, '_get_type') else 'unknown'
            var_label = dataset.text(var) if hasattr(dataset, 'text') else 'N/A'
            
            html_content += f"""
            <div class="variable">
                <div class="var-name">{var}</div>
                <div class="var-type">Type: {var_type}</div>
                <div class="var-label">Label: {var_label}</div>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        with open(output_path, 'w') as f:
            f.write(html_content)

    def _export_csv_codebook(
        self,
        dataset: "DataSet",
        output_path: str
    ) -> None:
        """Export codebook as CSV."""
        codebook_data = []
        variables = dataset.columns() if hasattr(dataset, 'columns') else []
        
        for var in variables:
            codebook_data.append({
                'Variable': var,
                'Type': dataset._get_type(var) if hasattr(dataset, '_get_type') else 'unknown',
                'Label': dataset.text(var) if hasattr(dataset, 'text') else 'N/A'
            })

        df = pd.DataFrame(codebook_data)
        df.to_csv(output_path, index=False)

    def get_strategy_name(self) -> str:
        return "report_generation"


class ExportManager:
    """
    Handles all export and output operations following Single Responsibility Principle.

    This class manages:
    - Native Quantipy format exports (.csv/.json)
    - External format exports (SPSS, Dimensions, Forsta)
    - Metadata exports and serialization
    - Session management and snapshots
    - Report generation and summaries

    Uses Strategy pattern for extensible export support.
    """

    def __init__(self, dataset: "DataSet") -> None:
        """Initialize ExportManager with reference to parent DataSet."""
        self._dataset = dataset
        self._strategies: Dict[str, ExportStrategy] = {}
        self._initialize_strategies()

    def _initialize_strategies(self) -> None:
        """Initialize all available export strategies."""
        self._strategies = {
            "native_export": NativeExportStrategy(),
            "external_format": ExternalFormatStrategy(),
            "metadata_export": MetadataExportStrategy(),
            "session_management": SessionManagementStrategy(),
            "report_generation": ReportGenerationStrategy(),
        }

    def get_supported_exports(self) -> List[str]:
        """Get list of supported export types."""
        return list(self._strategies.keys())

    # Native Export Operations
    def write_quantipy(
        self,
        path_meta: Optional[str] = None,
        path_data: Optional[str] = None
    ) -> None:
        """
        Write data and meta components to .csv/.json files.

        Args:
            path_meta: Path for metadata JSON file
            path_data: Path for data CSV file

        Returns:
            None - Files are written to disk
        """
        strategy = self._strategies["native_export"]
        return strategy.export(
            self._dataset, "write_quantipy",
            path_meta=path_meta, path_data=path_data
        )

    def split(self, save: bool = False) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """
        Return meta and data components, optionally saving them.

        Args:
            save: Whether to save components to disk

        Returns:
            Tuple of (meta, data) components
        """
        strategy = self._strategies["native_export"]
        return strategy.export(self._dataset, "split", save=save)

    def save(self) -> None:
        """
        Save current state for later recovery.

        Returns:
            None - State is saved to cache
        """
        strategy = self._strategies["native_export"]
        return strategy.export(self._dataset, "save")

    # External Format Operations
    def write_spss(
        self,
        path_sav: Optional[str] = None,
        index: bool = True,
        text_key: Optional[str] = None,
        mrset_tag_style: str = '__',
        drop_delimited: bool = True,
        from_set: Optional[str] = None,
        verbose: bool = True
    ) -> None:
        """
        Export to SPSS .sav format.

        Args:
            path_sav: Output path for .sav file
            index: Include DataFrame index
            text_key: Text key for labels
            mrset_tag_style: Multiple response set tag style
            drop_delimited: Drop delimited set variables
            from_set: Export specific variable set
            verbose: Verbose output

        Returns:
            None - File is written to disk
        """
        strategy = self._strategies["external_format"]
        return strategy.export(
            self._dataset, "write_spss",
            path_sav=path_sav, index=index, text_key=text_key,
            mrset_tag_style=mrset_tag_style, drop_delimited=drop_delimited,
            from_set=from_set, verbose=verbose
        )

    def write_dimensions(
        self,
        path_mdd: Optional[str] = None,
        path_ddf: Optional[str] = None,
        text_key: Optional[str] = None,
        run: bool = True,
        clean_up: bool = True
    ) -> None:
        """
        Export to Dimensions .mdd/.ddf format.

        Args:
            path_mdd: Path for metadata .mdd file
            path_ddf: Path for data .ddf file
            text_key: Text key for labels
            run: Run the export process
            clean_up: Clean up temporary files

        Returns:
            None - Files are written to disk
        """
        strategy = self._strategies["external_format"]
        return strategy.export(
            self._dataset, "write_dimensions",
            path_mdd=path_mdd, path_ddf=path_ddf, text_key=text_key,
            run=run, clean_up=clean_up
        )

    def write_forsta(
        self,
        path_meta: str,
        path_data: str,
        schema_vars: Optional[List[str]] = None,
        verbose: bool = False
    ) -> None:
        """
        Export to Forsta format.

        Args:
            path_meta: Path for metadata file
            path_data: Path for data file
            schema_vars: Variables to include in schema
            verbose: Verbose output

        Returns:
            None - Files are written to disk
        """
        strategy = self._strategies["external_format"]
        return strategy.export(
            self._dataset, "write_forsta",
            path_meta=path_meta, path_data=path_data,
            schema_vars=schema_vars, verbose=verbose
        )

    def write_forsta_api(
        self,
        projectid: str,
        public_url: str,
        idp_url: str,
        client_id: str,
        client_secret: str,
        schema_vars: Optional[List[str]] = None
    ) -> Any:
        """
        Export to Forsta API.

        Args:
            projectid: Forsta project ID
            public_url: Public API URL
            idp_url: Identity provider URL
            client_id: API client ID
            client_secret: API client secret
            schema_vars: Variables to include

        Returns:
            API response
        """
        strategy = self._strategies["external_format"]
        return strategy.export(
            self._dataset, "write_forsta_api",
            projectid=projectid, public_url=public_url, idp_url=idp_url,
            client_id=client_id, client_secret=client_secret,
            schema_vars=schema_vars
        )

    # Metadata Export Operations
    def meta_to_json(
        self,
        key: Optional[str] = None,
        collection: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Union[str, None]:
        """
        Save metadata object as JSON.

        Args:
            key: Specific variable key
            collection: Metadata collection
            output_path: Output file path

        Returns:
            JSON string if no output_path, None if saved to file
        """
        strategy = self._strategies["metadata_export"]
        return strategy.export(
            self._dataset, "meta_to_json",
            key=key, collection=collection, output_path=output_path
        )

    def export_meta_subset(
        self,
        variables: List[str],
        output_path: Optional[str] = None
    ) -> Union[Dict[str, Any], None]:
        """
        Export metadata for specific variables.

        Args:
            variables: List of variables to include
            output_path: Optional output file path

        Returns:
            Metadata dict if no output_path, None if saved to file
        """
        strategy = self._strategies["metadata_export"]
        return strategy.export(
            self._dataset, "export_meta_subset",
            variables=variables, output_path=output_path
        )

    def serialize_metadata(
        self,
        format_type: str = 'json',
        compact: bool = False
    ) -> str:
        """
        Serialize complete metadata in various formats.

        Args:
            format_type: Output format (json, etc.)
            compact: Use compact formatting

        Returns:
            Serialized metadata string
        """
        strategy = self._strategies["metadata_export"]
        return strategy.export(
            self._dataset, "serialize_metadata",
            format_type=format_type, compact=compact
        )

    # Session Management Operations
    def save_session(self, checkpoint_name: str = 'default') -> None:
        """
        Save current session state.

        Args:
            checkpoint_name: Name for this checkpoint

        Returns:
            None - State is saved to cache
        """
        strategy = self._strategies["session_management"]
        return strategy.export(
            self._dataset, "save_session",
            checkpoint_name=checkpoint_name
        )

    def revert_session(self) -> None:
        """
        Revert to previously saved session state.

        Returns:
            None - Dataset is modified inplace
        """
        strategy = self._strategies["session_management"]
        return strategy.export(self._dataset, "revert_session")

    def backup_dataset(
        self,
        backup_path: str,
        include_cache: bool = False
    ) -> None:
        """
        Create complete dataset backup.

        Args:
            backup_path: Path for backup file
            include_cache: Include cache in backup

        Returns:
            None - Backup is written to disk
        """
        strategy = self._strategies["session_management"]
        return strategy.export(
            self._dataset, "backup_dataset",
            backup_path=backup_path, include_cache=include_cache
        )

    def create_checkpoint(
        self,
        checkpoint_name: str,
        description: str = ""
    ) -> None:
        """
        Create named checkpoint for recovery.

        Args:
            checkpoint_name: Name for this checkpoint
            description: Optional description

        Returns:
            None - Checkpoint is saved to cache
        """
        strategy = self._strategies["session_management"]
        return strategy.export(
            self._dataset, "create_checkpoint",
            checkpoint_name=checkpoint_name, description=description
        )

    # Report Generation Operations
    def dataset_summary(
        self,
        output_path: Optional[str] = None
    ) -> Union[Dict[str, Any], None]:
        """
        Generate comprehensive dataset summary report.

        Args:
            output_path: Optional output file path

        Returns:
            Summary dict if no output_path, None if saved to file
        """
        strategy = self._strategies["report_generation"]
        return strategy.export(
            self._dataset, "dataset_summary",
            output_path=output_path
        )

    def variable_report(
        self,
        variables: Optional[List[str]] = None,
        output_path: Optional[str] = None
    ) -> Union[Dict[str, Any], None]:
        """
        Generate detailed variable report.

        Args:
            variables: Variables to include (all if None)
            output_path: Optional output file path

        Returns:
            Report dict if no output_path, None if saved to file
        """
        strategy = self._strategies["report_generation"]
        return strategy.export(
            self._dataset, "variable_report",
            variables=variables, output_path=output_path
        )

    def export_codebook(
        self,
        output_path: str,
        format_type: str = 'html'
    ) -> None:
        """
        Export dataset codebook in various formats.

        Args:
            output_path: Output file path
            format_type: Format type (html, csv)

        Returns:
            None - Codebook is written to disk
        """
        strategy = self._strategies["report_generation"]
        return strategy.export(
            self._dataset, "export_codebook",
            output_path=output_path, format_type=format_type
        )

    def get_export_info(self) -> Dict[str, Any]:
        """Get information about export capabilities."""
        return {
            "supported_strategies": self.get_supported_exports(),
            "dataset_name": self._dataset.name,
            "native_formats": ["quantipy", "json", "csv"],
            "external_formats": ["spss", "dimensions", "forsta"],
            "report_formats": ["html", "csv", "json"],
            "strategy_count": len(self._strategies)
        }