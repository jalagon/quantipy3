"""
Test module for View class using pytest framework.

This module provides comprehensive testing for the View class,
following modern pytest patterns and best practices.
"""
import pytest
import os
import json
import pandas as pd
import numpy as np
from copy import deepcopy
from typing import Any

from quantipy.core.stack import Stack
from quantipy.core.view import View
from quantipy.core.link import Link
from quantipy.core.helpers.functions import load_json
from quantipy.core.view_generators.view_maps import QuantipyViews

# Test data paths
PATH_DATA = './tests/'
PROJECT_NAME = 'Example Data (A)'
NAME_DATA = f'{PROJECT_NAME}.csv'
NAME_META = f'{PROJECT_NAME}.json'
PATH_CSV = os.path.join(PATH_DATA, NAME_DATA)
PATH_JSON = os.path.join(PATH_DATA, NAME_META)


@pytest.fixture(scope='module')
def example_data():
    """Load Example Data (A) data and meta."""
    data = pd.read_csv(PATH_CSV)
    meta = load_json(PATH_JSON)
    return data, meta


@pytest.fixture
def stack_with_data(example_data):
    """Create a stack with data for testing."""
    data, meta = example_data
    stack = Stack(name="test_views")
    stack.add_data(
        data_key=stack.name,
        meta=meta,
        data=data
    )
    return stack


@pytest.fixture
def basic_link(stack_with_data):
    """Create a basic link for view testing."""
    stack = stack_with_data
    stack.add_link(
        data_keys=stack.name,
        filters='no_filter',
        x=['gender'],
        y=['@'],
        views=['cbase', 'counts']
    )
    return stack[stack.name]['no_filter']['gender']['@']


@pytest.fixture
def basic_view():
    """Create a basic View instance for testing."""
    return View()


class TestViewCore:
    """Test core View functionality."""
    
    def test_view_instantiation(self):
        """Test that View can be instantiated."""
        view = View()
        assert view is not None
        assert isinstance(view, View)
    
    def test_view_with_link(self, basic_link):
        """Test View instantiation with a Link."""
        view = View(link=basic_link, name='test_view')
        assert view.name == 'test_view'
        assert hasattr(view, '_x')
        assert hasattr(view, '_y')
    
    def test_view_attributes(self, basic_view):
        """Test View has expected attributes."""
        assert hasattr(basic_view, 'dataframe')
        assert hasattr(basic_view, 'name')
        assert hasattr(basic_view, 'rbases')
        assert hasattr(basic_view, 'cbases')
        assert hasattr(basic_view, 'grp_text_map')
        assert hasattr(basic_view, 'add_base_text')
        
        # Check initial values
        assert isinstance(basic_view.dataframe, pd.DataFrame)
        assert basic_view.dataframe.empty
        assert basic_view.rbases is None
        assert basic_view.cbases is None
        assert basic_view.add_base_text is True


class TestViewMeta:
    """Test View metadata functionality."""
    
    def test_view_meta_structure(self, basic_view):
        """Test View.meta() returns correct structure."""
        meta = basic_view.meta()
        
        assert isinstance(meta, dict)
        assert 'agg' in meta
        assert 'x' in meta
        assert 'y' in meta
        assert 'shape' in meta
        
        # Check aggregation metadata
        agg = meta['agg']
        assert 'is_weighted' in agg
        assert 'weights' in agg
        assert 'method' in agg
        assert 'name' in agg
        assert 'fullname' in agg
        assert 'text' in agg
        assert 'grp_text_map' in agg
        assert 'is_block' in agg
    
    def test_view_meta_with_link(self, basic_link):
        """Test View.meta() with Link data."""
        view = View(link=basic_link, name='test_view')
        meta = view.meta()
        
        assert meta['x']['name'] == 'gender'
        assert meta['y']['name'] == '@'
        assert isinstance(meta['shape'], tuple)


class TestViewAnalysisMethods:
    """Test View analysis methods."""
    
    def test_is_weighted(self, basic_view):
        """Test is_weighted method."""
        assert basic_view.is_weighted() is False
    
    def test_is_pct(self, basic_view):
        """Test is_pct method."""
        result = basic_view.is_pct()
        assert isinstance(result, bool)
    
    def test_is_base(self, basic_view):
        """Test is_base method."""
        result = basic_view.is_base()
        assert isinstance(result, bool)
    
    def test_is_sum(self, basic_view):
        """Test is_sum method."""
        result = basic_view.is_sum()
        assert isinstance(result, bool)
    
    def test_is_net(self, basic_view):
        """Test is_net method."""
        result = basic_view.is_net()
        assert isinstance(result, bool)
    
    def test_is_counts(self, basic_view):
        """Test is_counts method."""
        result = basic_view.is_counts()
        assert isinstance(result, bool)
    
    def test_is_stat(self, basic_view):
        """Test is_stat method."""
        result = basic_view.is_stat()
        assert isinstance(result, bool)
    
    def test_is_meanstest(self, basic_view):
        """Test is_meanstest method."""
        result = basic_view.is_meanstest()
        assert isinstance(result, bool)
    
    def test_is_propstest(self, basic_view):
        """Test is_propstest method."""
        result = basic_view.is_propstest()
        assert isinstance(result, bool)
    
    def test_has_other_source(self, basic_view):
        """Test has_other_source method."""
        result = basic_view.has_other_source()
        assert isinstance(result, bool)
    
    def test_has_calc(self, basic_view):
        """Test has_calc method."""
        result = basic_view.has_calc()
        assert isinstance(result, bool)
    
    def test_is_cumulative(self, basic_view):
        """Test is_cumulative method."""
        result = basic_view.is_cumulative()
        assert isinstance(result, bool)


class TestViewProperties:
    """Test View property methods."""
    
    def test_missing(self, basic_view):
        """Test missing method."""
        result = basic_view.missing()
        assert result is None or isinstance(result, list)
    
    def test_rescaling(self, basic_view):
        """Test rescaling method."""
        result = basic_view.rescaling()
        assert result is None or isinstance(result, dict)
    
    def test_weights(self, basic_view):
        """Test weights method."""
        result = basic_view.weights()
        assert result is None or isinstance(result, str)


class TestViewNotation:
    """Test View notation functionality."""
    
    def test_notation_creation(self, basic_view):
        """Test notation method."""
        notation = basic_view.notation('frequency', 'default')
        assert isinstance(notation, str)
        assert '|' in notation
    
    def test_shortname(self):
        """Test _shortname extraction."""
        view = View()
        view.name = 'x|f|:|test|counts'
        assert view._shortname() == 'counts'
    
    def test_method_extraction(self):
        """Test _method extraction."""
        view = View()
        view._notation = 'x|f|:|test|counts'
        method = view._method()
        assert isinstance(method, str)


class TestViewDataFrameOperations:
    """Test View DataFrame operations."""
    
    def test_dataframe_initialization(self, basic_view):
        """Test DataFrame is properly initialized."""
        assert isinstance(basic_view.dataframe, pd.DataFrame)
        assert basic_view.dataframe.empty
    
    def test_dataframe_assignment(self):
        """Test DataFrame can be assigned."""
        view = View()
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        view.dataframe = df
        
        assert not view.dataframe.empty
        assert view.dataframe.shape == (3, 2)
        assert list(view.dataframe.columns) == ['A', 'B']


class TestViewTextManagement:
    """Test View text and label management."""
    
    def test_custom_text(self, basic_view):
        """Test custom text attribute."""
        assert basic_view._custom_txt == ''
        basic_view._custom_txt = 'Custom Label'
        assert basic_view._custom_txt == 'Custom Label'
    
    def test_add_base_text_flag(self, basic_view):
        """Test add_base_text flag."""
        assert basic_view.add_base_text is True
        basic_view.add_base_text = False
        assert basic_view.add_base_text is False
    
    def test_translate_metric(self, basic_view):
        """Test translate_metric method."""
        result = basic_view.translate_metric()
        assert result is None or isinstance(result, str)
    
    def test_metric_name_map(self):
        """Test _metric_name_map static method."""
        name_map = View._metric_name_map()
        assert isinstance(name_map, dict)
        assert len(name_map) > 0


class TestViewParameters:
    """Test View parameter methods."""
    
    def test_get_std_params(self, basic_view):
        """Test get_std_params method."""
        params = basic_view.get_std_params()
        assert isinstance(params, tuple)
        assert len(params) > 0
    
    def test_get_edit_params(self, basic_view):
        """Test get_edit_params method."""
        params = basic_view.get_edit_params()
        assert isinstance(params, tuple)


class TestViewNesting:
    """Test View nesting functionality."""
    
    def test_nests_without_nesting(self, basic_view):
        """Test nests method raises error without nested columns."""
        with pytest.raises(ValueError, match="Columns are not nested"):
            basic_view.nests()


class TestViewStringRepresentation:
    """Test View string representation."""
    
    def test_repr(self, basic_view):
        """Test __repr__ method."""
        repr_str = repr(basic_view)
        assert isinstance(repr_str, str)
    
    def test_str(self, basic_view):
        """Test string representation doesn't crash."""
        str_repr = str(basic_view)
        assert isinstance(str_repr, str)


class TestViewEdgeCases:
    """Test View edge cases and error handling."""
    
    def test_empty_kwargs(self):
        """Test View with empty kwargs."""
        view = View(kwargs={})
        assert view._kwargs == {}
    
    def test_none_kwargs(self):
        """Test View with None kwargs."""
        view = View(kwargs=None)
        assert view._kwargs is None
    
    def test_kwargs_copy(self):
        """Test that kwargs are copied."""
        original_kwargs = {'key': 'value'}
        view = View(kwargs=original_kwargs)
        view._kwargs['key'] = 'modified'
        assert original_kwargs['key'] == 'value'


class TestViewIntegration:
    """Test View integration with Stack and Link."""
    
    def test_view_from_stack_link(self, stack_with_data):
        """Test creating Views from Stack Links."""
        stack = stack_with_data
        
        # Add aggregations
        stack.add_link(
            data_keys=stack.name,
            filters='no_filter',
            x=['gender'],
            y=['locality'],
            views=['cbase', 'counts']
        )
        
        # Get link and views
        link = stack[stack.name]['no_filter']['gender']['locality']
        
        # Check views exist
        assert 'cbase' in link
        assert 'counts' in link
        
        # Check view properties
        for view_key in ['cbase', 'counts']:
            if view_key in link:
                view = link[view_key]
                assert isinstance(view, View)
                assert hasattr(view, 'dataframe')
                assert hasattr(view, 'meta')