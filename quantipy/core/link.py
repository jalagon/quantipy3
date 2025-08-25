"""
Link module for quantipy data processing.

This module provides the Link class for managing relationships between variables
in survey data analysis workflows, generating views and statistical computations.

Following SOLID principles, this class handles:
- Variable relationship management
- View generation and storage
- Data access and filtering
- Statistical computation coordination
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from .view_generators.view_maps import QuantipyViews as View

if TYPE_CHECKING:
    from pandas import DataFrame

    from quantipy.core.stack import Stack


class Link(dict[str, Any]):
    """
    The Link object is a subclassed dictionary that generates an instance of
    Pandas.DataFrame for every view method applied.

    Manages relationships between variables in survey data analysis workflows,
    providing access to filtered data and metadata while generating statistical views.
    """

    def __init__(
        self,
        the_filter: str | dict[str, Any],
        y: str,
        x: str,
        data_key: str,
        stack: Stack,
        views: str | list[str] | View | None = None,
        store_view: bool = False,
        create_views: bool = True,
    ) -> None:

        self.filter: str | dict[str, Any] = the_filter
        self.y: str = y
        self.x: str = x
        self.data_key: str = data_key
        self.stack: Stack = stack

        # If this variable is set to true, then the view will be transposed.
        self.transpose: bool = False

        if isinstance(views, str):
            views = View(views)
        elif isinstance(views, list):
            views = View(*views)
        elif views is None:
            views = View()

        if store_view:
            self.view: View = views

        data = stack[data_key].data
        if create_views:
            if '@1' not in list(data.keys()):
                data['@1'] = np.ones(len(data.index))
            views._apply_to(self)

    def get_meta(self) -> dict[str, Any]:
        """Get metadata for the linked dataset.

        Returns:
            Dataset metadata dictionary
        """
        stack = self.stack
        data_key = self.data_key
        return stack[data_key].meta

    def get_data(self) -> DataFrame:
        """Get filtered data for the link.

        Returns:
            Pandas DataFrame with filtered data
        """
        stack = self.stack
        data_key = self.data_key
        filter_def = self.filter
        return stack[data_key][filter_def].data

    def get_cache(self) -> dict[str, Any]:
        """Get cache for the linked dataset.

        Returns:
            Dataset cache dictionary
        """
        return self.stack[self.data_key].cache

    def merge(
        self,
        link: Link,
        views: list[str] | None = None,
        overwrite: bool = False
    ) -> None:
        """
        Merge the views from another link into this link.

        Args:
            link: Source Link to merge views from
            views: Specific view keys to merge, or None for all
            overwrite: Whether to overwrite existing views
        """

        if views is None:
            views = list(link.keys())

        for vk in views:
            if overwrite or vk not in self:
                self[vk] = link.pop(vk)

    def __getitem__(self, key: str) -> Any:
        """Get item with optional transposition.

        If the 'transpose' variable is set to True, this method tries
        to transpose the result using the .T attribute.

        Args:
            key: Dictionary key to retrieve

        Returns:
            Value from dictionary, optionally transposed

        Note:
            Only objects with a .T attribute can be transposed.
        """
        val = dict.__getitem__(self, key)

        if self.transpose:
            if "T" in dir(val):
                return val.T
            return val
        return val
