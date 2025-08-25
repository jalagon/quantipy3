#!/usr/bin/python
"""
Options module for quantipy configuration management.

This module provides global configuration options for quantipy behavior,
allowing users to customize processing, rule application, and performance
optimizations throughout the library.

Following SOLID principles, this module handles:
- Global configuration management
- Option validation and setting
- Performance optimization flags
- Processing behavior customization
"""
from __future__ import annotations

OPTIONS: dict[str, bool] = {
    'new_rules': False,
    'new_chains': False,
    'short_item_texts': False,
    'convert_chains': False,
    'fast_stack_filters': False,
}


def set_option(option: str, val: bool) -> None:
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
        err = f"'{option}' is not a valid option!"
        raise ValueError(err)
    OPTIONS[option] = val


def get_option(option: str) -> bool:
    """
    Get a quantipy configuration option value.

    Parameters
    ----------
    option : str
        Name of the option to get. Must be a valid option key.

    Returns
    -------
    bool
        Current value of the option.

    Raises
    ------
    ValueError
        If option is not a valid configuration key.
    """
    if option not in OPTIONS:
        err = f"'{option}' is not a valid option!"
        raise ValueError(err)
    return OPTIONS[option]


def get_all_options() -> dict[str, bool]:
    """
    Get all quantipy configuration options.

    Returns
    -------
    dict[str, bool]
        Dictionary containing all configuration options and their values.
    """
    return OPTIONS.copy()


def reset_options() -> None:
    """
    Reset all quantipy configuration options to their default values.
    """
    OPTIONS.update({
        'new_rules': False,
        'new_chains': False,
        'short_item_texts': False,
        'convert_chains': False,
        'fast_stack_filters': False,
    })
