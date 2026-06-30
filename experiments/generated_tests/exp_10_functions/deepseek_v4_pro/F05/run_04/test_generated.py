import pytest
import pandas as pd
import numpy as np
from ise26.targets import validate_schema

def test_empty_schema_accepts_any_df():
    df = pd.DataFrame({'a': [1], 'b': [2.0]})
    result = validate_schema(df, {})
    assert result['valid'] == True
    assert result['missing_columns'] == []
    assert result['type_errors'] == []

def test_all_columns_correct():
    df = pd.DataFrame({
        'id': pd.Series([1, 2], dtype='int64'),
        'name': ['Alice', 'Bob'],
        'score': pd.Series([98.5, 88.0], dtype='float64'),
        'active': pd.Series([True, False], dtype='bool'),