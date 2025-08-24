#!/usr/bin/python
"""
Options module for quantipy configuration management.

This module provides global configuration options for quantipy behavior,
allowing users to customize processing, rule application, and performance
optimizations throughout the library.
"""

OPTIONS = {
    'new_rules': False,
    'new_chains': False,
    'short_item_texts': False,
    'convert_chains': False,
    'fast_stack_filters': False,
}


def set_option(option, val):
    """
    Set a quantipy configuration option.

    Parameters
    ----------
    option : str
        Name of the option to set. Must be a valid option key.
    val : bool
        Value to set for the option.

    Raises
    ------
    ValueError
        If option is not a valid configuration key.
    """
    if option not in OPTIONS:
        err = "'{}' is not a valid option!".format(option)
        raise ValueError(err)
    OPTIONS[option] = val
    return None
