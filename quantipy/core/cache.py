"""
Cache module for quantipy data processing.

This module provides the Cache class for storing and managing Quantipy resources
such as matrices, weight vectors, and statistical quantities during analysis
workflows.

Following SOLID principles, this class handles:
- Resource caching and storage
- Statistical quantity management
- Memory optimization for analysis workflows
- Collection-based object organization
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


class Cache(defaultdict[str, dict[str, Any]]):
    def __init__(self) -> None:
        # The 'lock_cache' raises an exception in the
        super().__init__(Cache)

    def __reduce__(self) -> tuple[type, tuple[()], None, None, Any]:
        return self.__class__, (), None, None, iter(list(self.items()))

    def set_obj(self, collection: str, key: str, obj: Any) -> None:
        '''
        Save a Quantipy resource inside the cache.

        Parameters
        ----------
        collection : str
            The key of the collection the object should be placed in.
            Valid values: 'matrices', 'weight_vectors', 'quantities',
            'mean_view_names', 'count_view_names'
        key : str
            The reference key for the object.
        obj : Any
            The object to store inside the cache.

        Returns
        -------
        None
        '''
        self[collection][key] = obj

    def get_obj(self, collection: str, key: str) -> Any:
        '''
        Look up if an object exists in the cache and return it.

        Parameters
        ----------
        collection : str
            The key of the collection to look into.
            Valid values: 'matrices', 'weight_vectors', 'quantities',
            'mean_view_names', 'count_view_names'
        key : str
            The reference key for the object.

        Returns
        -------
        Union[Any, Tuple[Any, ...]]
            The cached object mapped to the passed key or default tuple.
        '''
        if collection == 'matrices':
            return self[collection].get(key, (None, None))
        if collection == 'squeezed':
            return self[collection].get(key, (None, None, None, None, None, None, None))
        return self[collection].get(key, None)

    def has_obj(self, collection: str, key: str) -> bool:
        """
        Check if an object exists in the cache.

        Parameters
        ----------
        collection : str
            The key of the collection to check.
        key : str
            The reference key for the object.

        Returns
        -------
        bool
            True if the object exists in the cache, False otherwise.
        """
        return key in self[collection]

    def clear_collection(self, collection: str) -> None:
        """
        Clear all objects from a specific collection.

        Parameters
        ----------
        collection : str
            The key of the collection to clear.
        """
        if collection in self:
            self[collection].clear()

    def get_collections(self) -> list[str]:
        """
        Get list of all collection names in the cache.

        Returns
        -------
        list[str]
            List of collection names.
        """
        return list(self.keys())
