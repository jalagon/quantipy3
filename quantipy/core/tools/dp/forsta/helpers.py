from __future__ import annotations


def int_or_float(variable):
    numeric_scale = variable.get('scale')
    if numeric_scale and numeric_scale != 0:
        return 'float'
    return 'int'
