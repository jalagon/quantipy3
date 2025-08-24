"""
CacheManager - Handles all caching and performance optimization for DataSet

This module provides a focused, SOLID-compliant implementation of caching
and performance optimization functionality extracted from the monolithic DataSet class.

Following Single Responsibility Principle, this module handles:
- Session state caching and management
- Resource caching (matrices, weights, quantities)
- Memory management and optimization
- Performance monitoring and profiling
- Cache invalidation and cleanup strategies
"""

import gc
import sys
import time
import warnings
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from quantipy.core.dataset import DataSet

# Import the existing Cache class
from quantipy.core.cache import Cache


class CacheStrategy(ABC):
    """Abstract base class for cache operations following Strategy pattern."""

    @abstractmethod
    def execute(
        self,
        dataset: "DataSet",
        *args,
        **kwargs
    ) -> Any:
        """
        Execute cache operation on dataset.

        Args:
            dataset: DataSet instance to operate on
            *args: Strategy-specific positional arguments
            **kwargs: Strategy-specific keyword arguments

        Returns:
            Strategy-dependent return value
        """

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the name of this cache strategy."""


class SessionCacheStrategy(CacheStrategy):
    """Strategy for session state caching and management."""

    def execute(
        self,
        dataset: "DataSet",
        operation: str,
        **kwargs
    ) -> Any:
        """Execute session cache operations."""
        if operation == "save_session":
            return self._save_session(dataset, **kwargs)
        if operation == "revert_session":
            return self._revert_session(dataset)
        if operation == "clear_session":
            return self._clear_session(dataset)
        if operation == "get_savepoints":
            return self._get_savepoints(dataset)
        if operation == "create_savepoint":
            return self._create_savepoint(dataset, **kwargs)
        raise ValueError(f"Unknown session cache operation: {operation}")

    def _save_session(
        self,
        dataset: "DataSet",
        savepoint_name: str = 'savepoint'
    ) -> None:
        """Save current dataset state to cache."""
        if dataset._data is None and dataset._meta is None:
            warnings.warn("No data/meta components found in the DataSet.")
            return

        # Create a deep copy to avoid reference issues
        ds_clone = dataset.clone()
        dataset._cache[savepoint_name] = ds_clone.split()
        return

    def _revert_session(self, dataset: "DataSet") -> None:
        """Revert to previously saved session state."""
        if 'savepoint' not in dataset._cache:
            warnings.warn("No saved session DataSet file found!")
            return

        dataset._meta, dataset._data = dataset._cache['savepoint']
        print(f'Reverted to last savepoint of {dataset.name}')
        return

    def _clear_session(self, dataset: "DataSet") -> None:
        """Clear all session savepoints."""
        savepoints_to_remove = [
            key for key in dataset._cache.keys()
            if key in ['savepoint'] or key.startswith('savepoint_')
        ]

        for savepoint in savepoints_to_remove:
            del dataset._cache[savepoint]

        return

    def _get_savepoints(self, dataset: "DataSet") -> list[str]:
        """Get list of available savepoints."""
        return [
            key for key in dataset._cache.keys()
            if key == 'savepoint' or key.startswith('savepoint_')
        ]

    def _create_savepoint(
        self,
        dataset: "DataSet",
        name: str,
        description: str = ""
    ) -> None:
        """Create named savepoint."""
        if dataset._data is None and dataset._meta is None:
            warnings.warn("No data/meta components found in the DataSet.")
            return

        ds_clone = dataset.clone()
        savepoint_key = f'savepoint_{name}'
        dataset._cache[savepoint_key] = {
            'data': ds_clone.split(),
            'description': description,
            'timestamp': pd.Timestamp.now(),
        }
        return

    def get_strategy_name(self) -> str:
        return "session_cache"


class ResourceCacheStrategy(CacheStrategy):
    """Strategy for resource caching (matrices, weights, quantities)."""

    def execute(
        self,
        dataset: "DataSet",
        operation: str,
        **kwargs
    ) -> Any:
        """Execute resource cache operations."""
        if operation == "set_resource":
            return self._set_resource(dataset, **kwargs)
        if operation == "get_resource":
            return self._get_resource(dataset, **kwargs)
        if operation == "clear_resources":
            return self._clear_resources(dataset, **kwargs)
        if operation == "list_resources":
            return self._list_resources(dataset, **kwargs)
        if operation == "cache_matrix":
            return self._cache_matrix(dataset, **kwargs)
        if operation == "cache_weights":
            return self._cache_weights(dataset, **kwargs)
        raise ValueError(f"Unknown resource cache operation: {operation}")

    def _set_resource(
        self,
        dataset: "DataSet",
        collection: str,
        key: str,
        obj: Any
    ) -> None:
        """Cache a resource object."""
        valid_collections = ['matrices', 'weight_vectors', 'quantities', 'mean_view_names', 'count_view_names']
        if collection not in valid_collections:
            raise ValueError(f"Invalid collection. Must be one of: {valid_collections}")

        dataset._cache.set_obj(collection, key, obj)
        return

    def _get_resource(
        self,
        dataset: "DataSet",
        collection: str,
        key: str
    ) -> Any:
        """Retrieve cached resource object."""
        return dataset._cache.get_obj(collection, key)

    def _clear_resources(
        self,
        dataset: "DataSet",
        collection: str | None = None
    ) -> None:
        """Clear cached resources."""
        if collection:
            if collection in dataset._cache:
                dataset._cache[collection].clear()
        else:
            # Clear all resource collections
            resource_collections = ['matrices', 'weight_vectors', 'quantities', 'mean_view_names', 'count_view_names']
            for coll in resource_collections:
                if coll in dataset._cache:
                    dataset._cache[coll].clear()
        return

    def _list_resources(
        self,
        dataset: "DataSet",
        collection: str | None = None
    ) -> dict[str, list[str]]:
        """List cached resources."""
        if collection:
            return {collection: list(dataset._cache.get(collection, {}).keys())}
        resource_collections = ['matrices', 'weight_vectors', 'quantities', 'mean_view_names', 'count_view_names']
        result = {}
        for coll in resource_collections:
            if coll in dataset._cache:
                result[coll] = list(dataset._cache[coll].keys())
        return result

    def _cache_matrix(
        self,
        dataset: "DataSet",
        key: str,
        matrix: Any,
        metadata: dict[str, Any | None] = None
    ) -> None:
        """Cache a matrix with optional metadata."""
        if metadata:
            cached_obj = (matrix, metadata)
        else:
            cached_obj = (matrix, None)

        dataset._cache.set_obj('matrices', key, cached_obj)
        return

    def _cache_weights(
        self,
        dataset: "DataSet",
        key: str,
        weights: Any,
        weight_info: dict[str, Any | None] = None
    ) -> None:
        """Cache weight vectors with optional info."""
        if weight_info:
            cached_obj = (weights, weight_info)
        else:
            cached_obj = weights

        dataset._cache.set_obj('weight_vectors', key, cached_obj)
        return

    def get_strategy_name(self) -> str:
        return "resource_cache"


class MemoryManagementStrategy(CacheStrategy):
    """Strategy for memory management and optimization."""

    def execute(
        self,
        dataset: "DataSet",
        operation: str,
        **kwargs
    ) -> Any:
        """Execute memory management operations."""
        if operation == "optimize_memory":
            return self._optimize_memory(dataset, **kwargs)
        if operation == "get_memory_usage":
            return self._get_memory_usage(dataset)
        if operation == "cleanup_unused":
            return self._cleanup_unused(dataset)
        if operation == "compress_data":
            return self._compress_data(dataset, **kwargs)
        if operation == "memory_report":
            return self._memory_report(dataset)
        raise ValueError(f"Unknown memory management operation: {operation}")

    def _optimize_memory(
        self,
        dataset: "DataSet",
        aggressive: bool = False
    ) -> dict[str, Any]:
        """Optimize dataset memory usage."""
        initial_memory = self._get_memory_usage(dataset)

        optimizations = {}

        # Optimize data types in DataFrame
        if dataset._data is not None:
            df_memory_before = dataset._data.memory_usage(deep=True).sum()

            # Convert object dtypes to category where appropriate
            for col in dataset._data.columns:
                if dataset._data[col].dtype == 'object':
                    nunique = dataset._data[col].nunique()
                    total_count = len(dataset._data[col])

                    # Convert to category if less than 50% unique values
                    if nunique / total_count < 0.5:
                        dataset._data[col] = dataset._data[col].astype('category')
                        optimizations[f'{col}_to_category'] = True

            # Downcast numeric types if safe
            numeric_cols = dataset._data.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                original_dtype = dataset._data[col].dtype

                if original_dtype == 'int64':
                    dataset._data[col] = pd.to_numeric(dataset._data[col], downcast='integer')
                elif original_dtype == 'float64':
                    dataset._data[col] = pd.to_numeric(dataset._data[col], downcast='float')

                new_dtype = dataset._data[col].dtype
                if new_dtype != original_dtype:
                    optimizations[f'{col}_downcast'] = f'{original_dtype} -> {new_dtype}'

            df_memory_after = dataset._data.memory_usage(deep=True).sum()
            optimizations['dataframe_memory_saved'] = df_memory_before - df_memory_after

        # Clean up cache if aggressive
        if aggressive:
            self._cleanup_unused(dataset)
            optimizations['cache_cleaned'] = True

        # Force garbage collection
        collected = gc.collect()
        optimizations['gc_objects_collected'] = collected

        final_memory = self._get_memory_usage(dataset)
        optimizations['total_memory_saved'] = initial_memory['total_mb'] - final_memory['total_mb']

        return optimizations

    def _get_memory_usage(self, dataset: "DataSet") -> dict[str, Any]:
        """Get detailed memory usage information."""
        memory_info = {}

        # DataSet object memory
        memory_info['dataset_object_mb'] = sys.getsizeof(dataset) / (1024 * 1024)

        # DataFrame memory
        if dataset._data is not None:
            memory_info['dataframe_mb'] = dataset._data.memory_usage(deep=True).sum() / (1024 * 1024)
            memory_info['dataframe_shape'] = dataset._data.shape
        else:
            memory_info['dataframe_mb'] = 0
            memory_info['dataframe_shape'] = (0, 0)

        # Metadata memory
        if dataset._meta is not None:
            memory_info['metadata_mb'] = sys.getsizeof(str(dataset._meta)) / (1024 * 1024)
        else:
            memory_info['metadata_mb'] = 0

        # Cache memory
        memory_info['cache_mb'] = sys.getsizeof(dataset._cache) / (1024 * 1024)

        # Total memory
        memory_info['total_mb'] = (
            memory_info['dataset_object_mb'] +
            memory_info['dataframe_mb'] +
            memory_info['metadata_mb'] +
            memory_info['cache_mb']
        )

        return memory_info

    def _cleanup_unused(self, dataset: "DataSet") -> dict[str, int]:
        """Clean up unused cached objects."""
        cleanup_stats = {}

        # Remove empty cache collections
        empty_collections = []
        for key, value in dataset._cache.items():
            if isinstance(value, (dict, list)) and len(value) == 0:
                empty_collections.append(key)

        for collection in empty_collections:
            del dataset._cache[collection]

        cleanup_stats['empty_collections_removed'] = len(empty_collections)

        # Force garbage collection
        collected = gc.collect()
        cleanup_stats['gc_objects_collected'] = collected

        return cleanup_stats

    def _compress_data(
        self,
        dataset: "DataSet",
        columns: list[str | None] = None
    ) -> dict[str, Any]:
        """Compress data columns to save memory."""
        if dataset._data is None:
            return {'error': 'No data to compress'}

        compression_results = {}
        columns_to_compress = columns or dataset._data.columns

        for col in columns_to_compress:
            if col not in dataset._data.columns:
                continue

            original_memory = dataset._data[col].memory_usage(deep=True)

            # Try to compress strings/objects
            if dataset._data[col].dtype == 'object':
                # Convert to category if beneficial
                unique_ratio = dataset._data[col].nunique() / len(dataset._data[col])
                if unique_ratio < 0.5:
                    dataset._data[col] = dataset._data[col].astype('category')
                    new_memory = dataset._data[col].memory_usage(deep=True)
                    compression_results[col] = {
                        'method': 'category',
                        'memory_saved_bytes': original_memory - new_memory,
                        'compression_ratio': new_memory / original_memory
                    }

        return compression_results

    def _memory_report(self, dataset: "DataSet") -> dict[str, Any]:
        """Generate comprehensive memory usage report."""
        report = {
            'timestamp': pd.Timestamp.now(),
            'dataset_name': dataset.name,
            'memory_usage': self._get_memory_usage(dataset),
        }

        # Add data type breakdown
        if dataset._data is not None:
            dtype_info = {}
            for dtype in dataset._data.dtypes.unique():
                cols_with_dtype = dataset._data.select_dtypes(include=[dtype]).columns
                dtype_info[str(dtype)] = {
                    'column_count': len(cols_with_dtype),
                    'memory_mb': dataset._data[cols_with_dtype].memory_usage(deep=True).sum() / (1024 * 1024)
                }
            report['data_types'] = dtype_info

        # Add cache breakdown
        cache_info = {}
        for collection in ['matrices', 'weight_vectors', 'quantities', 'savepoint']:
            if collection in dataset._cache:
                cache_info[collection] = {
                    'item_count': len(dataset._cache[collection]) if isinstance(dataset._cache[collection], dict) else 1,
                    'memory_mb': sys.getsizeof(dataset._cache[collection]) / (1024 * 1024)
                }
        report['cache_breakdown'] = cache_info

        return report

    def get_strategy_name(self) -> str:
        return "memory_management"


class PerformanceMonitoringStrategy(CacheStrategy):
    """Strategy for performance monitoring and profiling."""

    def execute(
        self,
        dataset: "DataSet",
        operation: str,
        **kwargs
    ) -> Any:
        """Execute performance monitoring operations."""
        if operation == "start_profiling":
            return self._start_profiling(dataset, **kwargs)
        if operation == "stop_profiling":
            return self._stop_profiling(dataset, **kwargs)
        if operation == "get_performance_stats":
            return self._get_performance_stats(dataset)
        if operation == "benchmark_operation":
            return self._benchmark_operation(dataset, **kwargs)
        raise ValueError(f"Unknown performance monitoring operation: {operation}")

    def _start_profiling(
        self,
        dataset: "DataSet",
        profile_name: str = 'default'
    ) -> None:
        """Start performance profiling."""
        if 'performance_profiles' not in dataset._cache:
            dataset._cache['performance_profiles'] = {}

        dataset._cache['performance_profiles'][profile_name] = {
            'start_time': time.time(),
            'operations': [],
            'memory_start': sys.getsizeof(dataset)
        }
        return

    def _stop_profiling(
        self,
        dataset: "DataSet",
        profile_name: str = 'default'
    ) -> dict[str, Any]:
        """Stop performance profiling and return results."""
        if 'performance_profiles' not in dataset._cache:
            return {'error': 'No active profiling sessions'}

        if profile_name not in dataset._cache['performance_profiles']:
            return {'error': f'Profile {profile_name} not found'}

        profile = dataset._cache['performance_profiles'][profile_name]
        end_time = time.time()

        results = {
            'profile_name': profile_name,
            'total_time_seconds': end_time - profile['start_time'],
            'operations_count': len(profile['operations']),
            'memory_delta_bytes': sys.getsizeof(dataset) - profile['memory_start'],
            'operations': profile['operations']
        }

        # Clean up profile
        del dataset._cache['performance_profiles'][profile_name]

        return results

    def _get_performance_stats(self, dataset: "DataSet") -> dict[str, Any]:
        """Get current performance statistics."""
        stats = {
            'dataset_size': {
                'rows': len(dataset._data) if dataset._data is not None else 0,
                'columns': len(dataset._data.columns) if dataset._data is not None else 0,
                'variables': len(dataset._meta.get('columns', {})) if dataset._meta else 0,
                'arrays': len(dataset._meta.get('masks', {})) if dataset._meta else 0
            },
            'memory_usage': sys.getsizeof(dataset),
            'cache_size': len(dataset._cache),
            'active_profiles': list(dataset._cache.get('performance_profiles', {}).keys())
        }

        return stats

    def _benchmark_operation(
        self,
        dataset: "DataSet",
        operation_func: callable,
        operation_name: str = 'benchmark',
        iterations: int = 1
    ) -> dict[str, Any]:
        """Benchmark a specific operation."""
        times = []
        memory_before = sys.getsizeof(dataset)

        for i in range(iterations):
            start_time = time.time()
            try:
                result = operation_func()
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
            end_time = time.time()

            times.append(end_time - start_time)

            if not success:
                break

        memory_after = sys.getsizeof(dataset)

        benchmark_results = {
            'operation_name': operation_name,
            'iterations': len(times),
            'success': success,
            'error': error,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'avg_time': sum(times) / len(times) if times else 0,
            'total_time': sum(times),
            'memory_delta_bytes': memory_after - memory_before,
            'times': times
        }

        return benchmark_results

    def get_strategy_name(self) -> str:
        return "performance_monitoring"


class CacheInvalidationStrategy(CacheStrategy):
    """Strategy for cache invalidation and cleanup."""

    def execute(
        self,
        dataset: "DataSet",
        operation: str,
        **kwargs
    ) -> Any:
        """Execute cache invalidation operations."""
        if operation == "invalidate_all":
            return self._invalidate_all(dataset)
        if operation == "invalidate_pattern":
            return self._invalidate_pattern(dataset, **kwargs)
        if operation == "clear_old_entries":
            return self._clear_old_entries(dataset, **kwargs)
        if operation == "validate_cache":
            return self._validate_cache(dataset)
        raise ValueError(f"Unknown cache invalidation operation: {operation}")

    def _invalidate_all(self, dataset: "DataSet") -> None:
        """Clear entire cache."""
        dataset._cache.clear()
        dataset._cache = Cache()  # Reinitialize with proper structure
        return

    def _invalidate_pattern(
        self,
        dataset: "DataSet",
        pattern: str,
        collection: str | None = None
    ) -> int:
        """Invalidate cache entries matching a pattern."""
        invalidated_count = 0

        if collection:
            collections_to_check = [collection]
        else:
            collections_to_check = list(dataset._cache.keys())

        for coll in collections_to_check:
            if coll not in dataset._cache:
                continue

            if isinstance(dataset._cache[coll], dict):
                keys_to_remove = [
                    key for key in dataset._cache[coll].keys()
                    if pattern in str(key)
                ]

                for key in keys_to_remove:
                    del dataset._cache[coll][key]
                    invalidated_count += 1

        return invalidated_count

    def _clear_old_entries(
        self,
        dataset: "DataSet",
        max_age_hours: float = 24.0
    ) -> int:
        """Clear cache entries older than specified age."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        removed_count = 0

        # Check for timestamped entries
        for collection_name, collection in dataset._cache.items():
            if isinstance(collection, dict):
                keys_to_remove = []
                for key, value in collection.items():
                    # Check if value has timestamp
                    if isinstance(value, dict) and 'timestamp' in value:
                        timestamp = value['timestamp']
                        if hasattr(timestamp, 'timestamp'):
                            entry_time = timestamp.timestamp()
                        else:
                            entry_time = timestamp

                        if current_time - entry_time > max_age_seconds:
                            keys_to_remove.append(key)

                for key in keys_to_remove:
                    del collection[key]
                    removed_count += 1

        return removed_count

    def _validate_cache(self, dataset: "DataSet") -> dict[str, Any]:
        """Validate cache integrity and consistency."""
        validation_results = {
            'valid': True,
            'issues': [],
            'collections': {},
            'total_size_mb': 0
        }

        try:
            total_size = 0
            for collection_name, collection in dataset._cache.items():
                collection_info = {
                    'type': type(collection).__name__,
                    'size_mb': sys.getsizeof(collection) / (1024 * 1024),
                    'item_count': len(collection) if hasattr(collection, '__len__') else 1
                }

                total_size += collection_info['size_mb']
                validation_results['collections'][collection_name] = collection_info

                # Check for common issues
                if isinstance(collection, dict):
                    for key, value in collection.items():
                        if value is None:
                            validation_results['issues'].append(f'Null value in {collection_name}[{key}]')
                        elif isinstance(value, (pd.DataFrame, pd.Series)) and value.empty:
                            validation_results['issues'].append(f'Empty DataFrame/Series in {collection_name}[{key}]')

            validation_results['total_size_mb'] = total_size

        except Exception as e:
            validation_results['valid'] = False
            validation_results['issues'].append(f'Cache validation error: {str(e)}')

        return validation_results

    def get_strategy_name(self) -> str:
        return "cache_invalidation"


class CacheManager:
    """
    Handles all caching and performance optimization following Single Responsibility Principle.

    This class manages:
    - Session state caching and management
    - Resource caching (matrices, weights, quantities)
    - Memory management and optimization
    - Performance monitoring and profiling
    - Cache invalidation and cleanup strategies

    Uses Strategy pattern for extensible cache operation support.
    """

    def __init__(self, dataset: "DataSet") -> None:
        """Initialize CacheManager with reference to parent DataSet."""
        self._dataset = dataset
        self._strategies: dict[str, CacheStrategy] = {}
        self._initialize_strategies()

    def _initialize_strategies(self) -> None:
        """Initialize all available cache strategies."""
        self._strategies = {
            "session_cache": SessionCacheStrategy(),
            "resource_cache": ResourceCacheStrategy(),
            "memory_management": MemoryManagementStrategy(),
            "performance_monitoring": PerformanceMonitoringStrategy(),
            "cache_invalidation": CacheInvalidationStrategy(),
        }

    def get_supported_operations(self) -> list[str]:
        """Get list of supported cache operation types."""
        return list(self._strategies.keys())

    # Session Cache Operations
    def save_session(self, savepoint_name: str = 'savepoint') -> None:
        """
        Save current dataset state to cache.

        Args:
            savepoint_name: Name for this savepoint

        Returns:
            None - State is saved to cache
        """
        strategy = self._strategies["session_cache"]
        return strategy.execute(
            self._dataset, "save_session", savepoint_name=savepoint_name
        )

    def revert_session(self) -> None:
        """
        Revert to previously saved session state.

        Returns:
            None - Dataset is modified inplace
        """
        strategy = self._strategies["session_cache"]
        return strategy.execute(self._dataset, "revert_session")

    def clear_session(self) -> None:
        """
        Clear all session savepoints.

        Returns:
            None - Cache is modified inplace
        """
        strategy = self._strategies["session_cache"]
        return strategy.execute(self._dataset, "clear_session")

    def get_savepoints(self) -> list[str]:
        """
        Get list of available savepoints.

        Returns:
            List of savepoint names
        """
        strategy = self._strategies["session_cache"]
        return strategy.execute(self._dataset, "get_savepoints")

    def create_savepoint(self, name: str, description: str = "") -> None:
        """
        Create named savepoint.

        Args:
            name: Savepoint name
            description: Optional description

        Returns:
            None - Savepoint is saved to cache
        """
        strategy = self._strategies["session_cache"]
        return strategy.execute(
            self._dataset, "create_savepoint", name=name, description=description
        )

    # Resource Cache Operations
    def set_resource(self, collection: str, key: str, obj: Any) -> None:
        """
        Cache a resource object.

        Args:
            collection: Resource collection name
            key: Resource key
            obj: Object to cache

        Returns:
            None - Object is cached
        """
        strategy = self._strategies["resource_cache"]
        return strategy.execute(
            self._dataset, "set_resource", collection=collection, key=key, obj=obj
        )

    def get_resource(self, collection: str, key: str) -> Any:
        """
        Retrieve cached resource object.

        Args:
            collection: Resource collection name
            key: Resource key

        Returns:
            Cached object or default value
        """
        strategy = self._strategies["resource_cache"]
        return strategy.execute(
            self._dataset, "get_resource", collection=collection, key=key
        )

    def clear_resources(self, collection: str | None = None) -> None:
        """
        Clear cached resources.

        Args:
            collection: Specific collection to clear (all if None)

        Returns:
            None - Resources are cleared
        """
        strategy = self._strategies["resource_cache"]
        return strategy.execute(
            self._dataset, "clear_resources", collection=collection
        )

    def list_resources(self, collection: str | None = None) -> dict[str, list[str]]:
        """
        List cached resources.

        Args:
            collection: Specific collection to list (all if None)

        Returns:
            Dictionary mapping collections to resource keys
        """
        strategy = self._strategies["resource_cache"]
        return strategy.execute(
            self._dataset, "list_resources", collection=collection
        )

    def cache_matrix(
        self,
        key: str,
        matrix: Any,
        metadata: dict[str, Any | None] = None
    ) -> None:
        """
        Cache a matrix with optional metadata.

        Args:
            key: Matrix key
            matrix: Matrix object
            metadata: Optional metadata

        Returns:
            None - Matrix is cached
        """
        strategy = self._strategies["resource_cache"]
        return strategy.execute(
            self._dataset, "cache_matrix", key=key, matrix=matrix, metadata=metadata
        )

    def cache_weights(
        self,
        key: str,
        weights: Any,
        weight_info: dict[str, Any | None] = None
    ) -> None:
        """
        Cache weight vectors with optional info.

        Args:
            key: Weights key
            weights: Weight vector
            weight_info: Optional weight information

        Returns:
            None - Weights are cached
        """
        strategy = self._strategies["resource_cache"]
        return strategy.execute(
            self._dataset, "cache_weights", key=key, weights=weights, weight_info=weight_info
        )

    # Memory Management Operations
    def optimize_memory(self, aggressive: bool = False) -> dict[str, Any]:
        """
        Optimize dataset memory usage.

        Args:
            aggressive: Use aggressive optimization

        Returns:
            Dictionary of optimization results
        """
        strategy = self._strategies["memory_management"]
        return strategy.execute(
            self._dataset, "optimize_memory", aggressive=aggressive
        )

    def get_memory_usage(self) -> dict[str, Any]:
        """
        Get detailed memory usage information.

        Returns:
            Dictionary of memory usage statistics
        """
        strategy = self._strategies["memory_management"]
        return strategy.execute(self._dataset, "get_memory_usage")

    def cleanup_unused(self) -> dict[str, int]:
        """
        Clean up unused cached objects.

        Returns:
            Dictionary of cleanup statistics
        """
        strategy = self._strategies["memory_management"]
        return strategy.execute(self._dataset, "cleanup_unused")

    def compress_data(self, columns: list[str | None] = None) -> dict[str, Any]:
        """
        Compress data columns to save memory.

        Args:
            columns: Specific columns to compress (all if None)

        Returns:
            Dictionary of compression results
        """
        strategy = self._strategies["memory_management"]
        return strategy.execute(
            self._dataset, "compress_data", columns=columns
        )

    def memory_report(self) -> dict[str, Any]:
        """
        Generate comprehensive memory usage report.

        Returns:
            Dictionary containing detailed memory report
        """
        strategy = self._strategies["memory_management"]
        return strategy.execute(self._dataset, "memory_report")

    # Performance Monitoring Operations
    def start_profiling(self, profile_name: str = 'default') -> None:
        """
        Start performance profiling.

        Args:
            profile_name: Name for this profiling session

        Returns:
            None - Profiling session is started
        """
        strategy = self._strategies["performance_monitoring"]
        return strategy.execute(
            self._dataset, "start_profiling", profile_name=profile_name
        )

    def stop_profiling(self, profile_name: str = 'default') -> dict[str, Any]:
        """
        Stop performance profiling and return results.

        Args:
            profile_name: Name of profiling session

        Returns:
            Dictionary of profiling results
        """
        strategy = self._strategies["performance_monitoring"]
        return strategy.execute(
            self._dataset, "stop_profiling", profile_name=profile_name
        )

    def get_performance_stats(self) -> dict[str, Any]:
        """
        Get current performance statistics.

        Returns:
            Dictionary of performance statistics
        """
        strategy = self._strategies["performance_monitoring"]
        return strategy.execute(self._dataset, "get_performance_stats")

    def benchmark_operation(
        self,
        operation_func: callable,
        operation_name: str = 'benchmark',
        iterations: int = 1
    ) -> dict[str, Any]:
        """
        Benchmark a specific operation.

        Args:
            operation_func: Function to benchmark
            operation_name: Name for this benchmark
            iterations: Number of iterations to run

        Returns:
            Dictionary of benchmark results
        """
        strategy = self._strategies["performance_monitoring"]
        return strategy.execute(
            self._dataset, "benchmark_operation",
            operation_func=operation_func, operation_name=operation_name,
            iterations=iterations
        )

    # Cache Invalidation Operations
    def invalidate_all(self) -> None:
        """
        Clear entire cache.

        Returns:
            None - Cache is cleared
        """
        strategy = self._strategies["cache_invalidation"]
        return strategy.execute(self._dataset, "invalidate_all")

    def invalidate_pattern(
        self,
        pattern: str,
        collection: str | None = None
    ) -> int:
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: Pattern to match
            collection: Specific collection (all if None)

        Returns:
            Number of entries invalidated
        """
        strategy = self._strategies["cache_invalidation"]
        return strategy.execute(
            self._dataset, "invalidate_pattern", pattern=pattern, collection=collection
        )

    def clear_old_entries(self, max_age_hours: float = 24.0) -> int:
        """
        Clear cache entries older than specified age.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of entries removed
        """
        strategy = self._strategies["cache_invalidation"]
        return strategy.execute(
            self._dataset, "clear_old_entries", max_age_hours=max_age_hours
        )

    def validate_cache(self) -> dict[str, Any]:
        """
        Validate cache integrity and consistency.

        Returns:
            Dictionary of validation results
        """
        strategy = self._strategies["cache_invalidation"]
        return strategy.execute(self._dataset, "validate_cache")

    # Legacy compatibility methods
    def get_cache(self) -> Cache:
        """Get the underlying cache object (legacy compatibility)."""
        return self._dataset._cache

    def clear_cache(self) -> None:
        """Clear cache (legacy compatibility)."""
        self.invalidate_all()

    def get_cache_info(self) -> dict[str, Any]:
        """Get information about cache capabilities."""
        return {
            "supported_strategies": self.get_supported_operations(),
            "dataset_name": self._dataset.name,
            "cache_collections": list(self._dataset._cache.keys()),
            "memory_usage_mb": self.get_memory_usage()["total_mb"],
            "strategy_count": len(self._strategies)
        }
