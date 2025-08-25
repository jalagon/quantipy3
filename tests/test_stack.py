"""
Test module for Stack class using pytest framework.

This module provides comprehensive testing for the Stack class,
following modern pytest patterns and best practices.
"""
import pytest
import os
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from collections import defaultdict, OrderedDict
from typing import Any

from quantipy.core.stack import Stack
from quantipy.core.chain import Chain
from quantipy.core.link import Link
from quantipy.core.view_generators.view_mapper import ViewMapper
from quantipy.core.view_generators.view_maps import QuantipyViews
from quantipy.core.view_generators.view_specs import net, calc
from quantipy.core.view import View
from quantipy.core.helpers import functions
from quantipy.core.helpers.functions import load_json
from quantipy.core.cache import Cache

# Constants
CBASE = "x|f|x:|||cbase"
COUNTS = "x|f|:|||counts"
DEFAULT = "x|default|:|||default"

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


@pytest.fixture(scope='module')
def variable_types():
    """Define variables by type for Example Data A."""
    return {
        'int': ['record_number', 'unique_id', 'age', 'birth_day', 'birth_month'],
        'float': ['weight', 'weight_a', 'weight_b'],
        'single': ['gender', 'locality', 'ethnicity', 'religion', 'q1'],
        'delimited_set': ['q2', 'q3', 'q8', 'q9'],
        'string': ['q8a', 'q9a'],
        'date': ['start_time', 'end_time'],
        'time': ['duration'],
        'array': ['q5', 'q6', 'q7'],
        'minimum': ['q2b', 'Wave', 'q2', 'q3', 'q5_1']
    }


@pytest.fixture
def stack_setup(example_data):
    """Set up example stack for testing."""
    data, meta = example_data
    
    # Create stack
    stack = Stack(name="Example Data (A)")
    stack.add_data(
        data_key=stack.name,
        meta=meta,
        data=data
    )
    
    # Add basic aggregations
    stack.add_link(
        data_keys=stack.name,
        filters='no_filter',
        x=['q2b', 'Wave'],
        y=['@', 'gender'],
        views=QuantipyViews(['default', 'cbase', 'counts']),
        weights=[None, 'weight_a']
    )
    
    return stack


class TestStackCore:
    """Test core Stack functionality."""
    
    def test_stack_is_subclassed_dict(self, stack_setup):
        """Test that Stack is a subclassed dict."""
        assert isinstance(stack_setup, dict)
        assert isinstance(stack_setup, Stack)
    
    def test_stack_behaves_like_dict(self, stack_setup):
        """Test that Stack behaves like a dictionary."""
        key = "some_key_name"
        value = "some_value"
        stack_setup[key] = value
        
        assert key in stack_setup.keys()
        assert stack_setup[key] == value
    
    def test_stack_has_required_attributes(self, stack_setup):
        """Test that Stack has all required attributes."""
        assert hasattr(stack_setup, 'name')
        assert hasattr(stack_setup, 'key')
        assert hasattr(stack_setup, 'meta')
        assert hasattr(stack_setup, 'data')
    
    def test_stack_name_property(self, stack_setup):
        """Test Stack name property."""
        assert stack_setup.name == "Example Data (A)"
        assert isinstance(stack_setup.name, str)


class TestStackCache:
    """Test Stack cache functionality."""
    
    def test_cache_is_created(self, example_data):
        """Test that cache is created when stack is initialized."""
        data, meta = example_data
        name = 'cache_test'
        
        # Init a stack
        stack = Stack(name=name)
        stack.add_data(
            data_key=stack.name,
            meta=meta,
            data=data
        )
        
        # Assert that it has a Cache that is empty
        assert 'cache' in stack[name].__dict__.keys()
        assert isinstance(stack[name].cache, Cache)
        assert stack[name].cache == Cache()
    
    def test_cache_population(self, example_data, variable_types):
        """Test cache population after aggregations."""
        data, meta = example_data
        name = 'cache_test'
        fk = ['no_filter']
        xk = variable_types['minimum']
        yk = ['@'] + variable_types['minimum']
        views = ['default']
        
        # Init stack and run aggregations
        stack = Stack(name=name)
        stack.add_data(
            data_key=stack.name,
            meta=meta,
            data=data
        )
        
        stack.add_link(
            data_keys=name,
            filters=fk,
            x=xk,
            y=yk,
            views=views,
            weights=None
        )
        
        # Check cache is populated
        assert len(stack[name].cache) > 0


class TestStackDataManagement:
    """Test Stack data management functionality."""
    
    def test_add_data(self, example_data):
        """Test adding data to stack."""
        data, meta = example_data
        stack = Stack(name="test_stack")
        
        stack.add_data(
            data_key="test_data",
            meta=meta,
            data=data
        )
        
        assert "test_data" in stack.keys()
        assert stack["test_data"].meta == meta
        assert_frame_equal(stack["test_data"].data, data)
    
    def test_multiple_data_keys(self, example_data):
        """Test adding multiple data keys to stack."""
        data, meta = example_data
        stack = Stack(name="multi_stack")
        
        # Add first dataset
        stack.add_data(
            data_key="data1",
            meta=meta,
            data=data.head(100)
        )
        
        # Add second dataset
        stack.add_data(
            data_key="data2",
            meta=meta,
            data=data.tail(100)
        )
        
        assert "data1" in stack.keys()
        assert "data2" in stack.keys()
        assert len(stack["data1"].data) == 100
        assert len(stack["data2"].data) == 100


class TestStackAggregation:
    """Test Stack aggregation functionality."""
    
    def test_add_link_basic(self, stack_setup):
        """Test basic link addition."""
        data_key = stack_setup.name
        
        # Check links exist
        assert data_key in stack_setup
        assert 'no_filter' in stack_setup[data_key]
        assert 'q2b' in stack_setup[data_key]['no_filter']
    
    def test_add_link_with_views(self, example_data):
        """Test adding links with multiple views."""
        data, meta = example_data
        stack = Stack(name="view_test")
        stack.add_data(
            data_key=stack.name,
            meta=meta,
            data=data
        )
        
        views = QuantipyViews(['default', 'cbase', 'counts'])
        stack.add_link(
            data_keys=stack.name,
            filters='no_filter',
            x=['gender'],
            y=['@'],
            views=views
        )
        
        link = stack[stack.name]['no_filter']['gender']['@']
        assert 'default' in link
        assert 'cbase' in link
        assert 'counts' in link
    
    def test_add_link_with_weights(self, example_data):
        """Test adding links with weights."""
        data, meta = example_data
        stack = Stack(name="weight_test")
        stack.add_data(
            data_key=stack.name,
            meta=meta,
            data=data
        )
        
        stack.add_link(
            data_keys=stack.name,
            filters='no_filter',
            x=['gender'],
            y=['@'],
            views=['cbase'],
            weights=['weight_a']
        )
        
        # Check weighted view exists
        link = stack[stack.name]['no_filter']['gender']['@']
        weighted_key = 'x|f|x:||weight_a|cbase'
        assert weighted_key in link


class TestStackChainIntegration:
    """Test Stack and Chain integration."""
    
    def test_chain_creation(self, stack_setup):
        """Test creating chains from stack."""
        chain = stack_setup.get_chain(
            data_keys=stack_setup.name,
            filters=['no_filter'],
            x=['q2b'],
            y=['@'],
            views=['default']
        )
        
        assert isinstance(chain, Chain)
        assert chain.name is not None
        assert len(chain) > 0
    
    def test_chain_concat(self, stack_setup):
        """Test chain concatenation."""
        chain = stack_setup.get_chain(
            data_keys=stack_setup.name,
            filters=['no_filter'],
            x=['q2b', 'Wave'],
            y=['@'],
            views=['default']
        )
        
        df = chain.concat()
        assert isinstance(df, pd.DataFrame)
        assert not df.empty


class TestStackSaveLoad:
    """Test Stack save and load functionality."""
    
    @pytest.fixture
    def temp_path(self, tmp_path):
        """Create temporary directory for save/load tests."""
        return str(tmp_path / "test_stack.stack")
    
    def test_save_stack(self, stack_setup, temp_path):
        """Test saving stack to file."""
        stack_setup.save(temp_path)
        assert os.path.exists(temp_path)
    
    def test_load_stack(self, stack_setup, temp_path):
        """Test loading stack from file."""
        # Save original
        stack_setup.save(temp_path)
        
        # Load and compare
        loaded_stack = Stack.load(temp_path)
        assert isinstance(loaded_stack, Stack)
        assert loaded_stack.name == stack_setup.name
        assert list(loaded_stack.keys()) == list(stack_setup.keys())


class TestStackEdgeCases:
    """Test Stack edge cases and error handling."""
    
    def test_empty_stack(self):
        """Test empty stack creation."""
        stack = Stack(name="empty")
        assert isinstance(stack, Stack)
        assert stack.name == "empty"
        assert len(stack) == 0
    
    def test_invalid_data_key(self, stack_setup):
        """Test accessing invalid data key."""
        with pytest.raises(KeyError):
            _ = stack_setup['nonexistent_key']['no_filter']
    
    def test_duplicate_data_key(self, example_data):
        """Test adding duplicate data key."""
        data, meta = example_data
        stack = Stack(name="duplicate_test")
        
        # Add data first time
        stack.add_data(
            data_key="test",
            meta=meta,
            data=data
        )
        
        # Adding again should overwrite
        stack.add_data(
            data_key="test",
            meta=meta,
            data=data.head(50)
        )
        
        assert len(stack["test"].data) == 50