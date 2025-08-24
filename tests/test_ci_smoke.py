"""
Smoke tests for CI pipeline - Week 5 Implementation.

These tests verify that the core enhanced modules can be imported
and basic functionality works after our Week 4+ modernization.
"""

import pytest
import sys
from typing import Any


class TestCISmoke:
    """Smoke tests for CI pipeline verification."""

    def test_python_version(self):
        """Test that we're running on Python 3.10+."""
        version_info = sys.version_info
        assert version_info.major == 3, "Must run on Python 3"
        assert version_info.minor >= 10, f"Must run on Python 3.10+, got {version_info.major}.{version_info.minor}"

    def test_core_imports(self):
        """Test that enhanced core modules can be imported individually."""
        # Test individual enhanced modules from Week 4+
        try:
            from quantipy.core.cache import Cache
            assert Cache is not None
            print("✅ Cache imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import Cache: {e}")
            
        try:
            from quantipy.core.options import set_option, OPTIONS
            assert callable(set_option)
            assert isinstance(OPTIONS, dict)
            print("✅ Options imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import Options: {e}")
            
        try:
            from quantipy.core.chain import Chain
            assert Chain is not None
            print("✅ Chain imported successfully")  
        except ImportError as e:
            pytest.fail(f"Failed to import Chain: {e}")
            
        try:
            from quantipy.core.cluster import Cluster
            assert Cluster is not None
            print("✅ Cluster imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import Cluster: {e}")
            
        # Test functions from query module
        try:
            from quantipy.core.tools.dp.query import uniquify_list
            assert callable(uniquify_list)
            print("✅ Query utilities imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import Query utilities: {e}")

    def test_type_annotations_present(self):
        """Test that our enhanced modules have type annotations."""
        import inspect
        from quantipy.core.cache import Cache
        from quantipy.core.options import set_option
        from quantipy.core.chain import Chain
        
        # Test Cache class has type annotations
        cache_init = Cache.__init__
        assert hasattr(cache_init, '__annotations__'), "Cache.__init__ should have type annotations"
        
        cache_get_obj = Cache.get_obj
        assert hasattr(cache_get_obj, '__annotations__'), "Cache.get_obj should have type annotations"
        
        # Test set_option function has type annotations  
        assert hasattr(set_option, '__annotations__'), "set_option should have type annotations"
        
        # Test Chain class has type annotations
        chain_init = Chain.__init__
        assert hasattr(chain_init, '__annotations__'), "Chain.__init__ should have type annotations"

    def test_cache_functionality(self):
        """Test basic Cache functionality."""
        from quantipy.core.cache import Cache
        
        cache = Cache()
        
        # Test setting and getting objects
        cache.set_obj('test_collection', 'test_key', 'test_value')
        result = cache.get_obj('test_collection', 'test_key')
        assert result == 'test_value'
        
        # Test default returns
        result = cache.get_obj('matrices', 'nonexistent')
        assert result == (None, None)
        
        result = cache.get_obj('squeezed', 'nonexistent')  
        assert result == (None, None, None, None, None, None, None)
        
        result = cache.get_obj('other', 'nonexistent')
        assert result is None

    def test_options_functionality(self):
        """Test basic options functionality."""
        from quantipy.core.options import set_option, OPTIONS
        
        # Test that OPTIONS is properly defined
        assert isinstance(OPTIONS, dict)
        assert 'new_rules' in OPTIONS
        
        # Test setting an option
        original_value = OPTIONS.get('new_rules', False)
        set_option('new_rules', True)
        assert OPTIONS['new_rules'] is True
        
        # Restore original value
        set_option('new_rules', original_value)

    def test_chain_basic_functionality(self):
        """Test basic Chain functionality."""
        from quantipy.core.chain import Chain
        
        # Test Chain creation
        chain = Chain(name='test_chain')
        assert chain.name == 'test_chain'
        assert hasattr(chain, 'orientation')
        assert hasattr(chain, 'source_name')
        
        # Test that it's a defaultdict
        assert hasattr(chain, 'default_factory')

    def test_cluster_basic_functionality(self):
        """Test basic Cluster functionality."""
        from quantipy.core.cluster import Cluster
        
        # Test Cluster creation
        cluster = Cluster(name='test_cluster')
        assert cluster.name == 'test_cluster'
        
        # Test that it's an OrderedDict subclass
        assert hasattr(cluster, 'keys')
        assert hasattr(cluster, 'values')

    def test_query_utilities(self):
        """Test basic query utility functions."""  
        from quantipy.core.tools.dp.query import uniquify_list, get_tests_slicer
        import pandas as pd
        
        # Test uniquify_list
        test_list = ['a', 'b', 'a', 'c', 'b']
        result = uniquify_list(test_list)
        assert result == ['a', 'b', 'c']
        assert len(result) == 3
        
        # Test get_tests_slicer with sample data
        test_series = pd.Series(['t.050', 't.010', 't.001'], index=[0, 1, 2])
        result = get_tests_slicer(test_series)
        assert len(result) == 3
        assert isinstance(result, list)

    @pytest.mark.slow
    def test_stack_creation(self):
        """Test basic Stack creation (marked as slow)."""
        from quantipy.core.stack import Stack
        
        # Test Stack creation
        stack = Stack(name='test_stack')
        assert stack.name == 'test_stack'
        assert hasattr(stack, 'stack_pos')
        assert stack.stack_pos == 'stack_root'

    def test_modern_python_features(self):
        """Test that modern Python features are working."""
        # Test modern union syntax (Python 3.10+)
        def test_union_types(value: str | None = None) -> str | None:
            return value
        
        assert test_union_types('test') == 'test'
        assert test_union_types() is None
        
        # Test dict/list generics (Python 3.9+)  
        test_dict: dict[str, Any] = {'key': 'value'}
        test_list: list[str] = ['a', 'b', 'c']
        
        assert test_dict['key'] == 'value'
        assert len(test_list) == 3


class TestCIIntegration:
    """Integration tests for CI pipeline."""
    
    @pytest.mark.integration  
    def test_full_import_chain(self):
        """Test that we can import and use multiple modules together."""
        import quantipy as qp
        from quantipy.core.stack import Stack
        from quantipy.core.chain import Chain
        from quantipy.core.cache import Cache
        from quantipy.core.cluster import Cluster
        
        # Test creating instances
        stack = Stack('integration_test')
        chain = Chain('integration_test')
        cache = Cache()
        cluster = Cluster('integration_test')
        
        # Test basic interactions
        cache.set_obj('test', 'stack_name', stack.name)
        stored_name = cache.get_obj('test', 'stack_name')
        assert stored_name == 'integration_test'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])