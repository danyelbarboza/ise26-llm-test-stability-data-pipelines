import pandas as pd
import numpy as np
import pytest
from ise26.targets import standardize_currency_values


def test_basic_brazilian_format():
    df = pd.DataFrame({"amount_raw": ["1.234,56"]})
    result = standardize_currency_values(df)
    assert result.loc[0, "amount"] == 1234.56
    assert "amount_raw" in result.columns
    assert "amount" in result.columns
    assert result["amount"].dtype == pd.Float64Dtype()


def test_basic_english_format():
    df = pd.DataFrame({"amount_raw": ["1,234.56"]})
    result = standardize_currency_values(df)
    assert result.loc[0, "amount"] == 1234.56


def test_with_currency_symbol():
    df = pd.DataFrame({"amount_raw": ["R$ 1.234,56"]})
    result = standardize_currency_values(df)
    assert result.loc[0, "amount"] == 1234.56


def test_with_whitespace():
    df = pd.DataFrame({"amount_raw": ["   R$  1,234.56   "]})
    result = standardize_currency_values(df)
    assert result.loc[0, "amount"] == 1234.56


def test_simple_number_no_separators():
    df = pd.DataFrame({"amount_raw": ["1234.56"]})
    result = standardize_currency_values(df)
    assert result.loc[0, "amount"] == 1234.56


def test_simple_number_comma_decimal():
    df = pd.DataFrame({"amount_raw": ["1234,56"]})
    result = standardize_currency_values(df)
    assert result.loc[0, "amount"] == 1234.56


def test_negative_values():
    df = pd.DataFrame({"amount_raw": [" -R$ 1.234,56", "-1,234.56"]})
    result = standardize_currency_values(df)
    assert result.loc[0, "amount"] == -1234.56
    assert result.loc[1, "amount"] == -1234.56


def test_invalid_values_become_pdna():
    df = pd.DataFrame({"amount_raw": ["abc", "R$", "12.3.4", "12,3,4"]})
    result = standardize_currency_values(df)
    assert pd.isna(result.loc[0, "amount"])
    assert pd.isna(result.loc[1, "amount"])
    assert pd.isna(result.loc[2, "amount"])
    assert pd.isna(result.loc[3, "amount"])


def test_empty_string_is_na():
    df = pd.DataFrame({"amount_raw": [""]})
    result = standardize_currency_values(df)
    assert pd.isna(result.loc[0, "amount"])


def test_none_value_is_na():
    df = pd.DataFrame({"amount_raw": [None]})
    result = standardize_currency_values(df)
    assert pd.isna(result.loc[0, "amount"])


def test_mixture_of_valid_and_invalid():