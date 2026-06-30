import pandas as pd
import pytest
from ise26.targets import classify_payment_status


def test_basic_classification():
    df = pd.DataFrame({
        "due_date": ["2023-01-15", "2023-02-20"],
        "paid_date": ["2023-01-10", "2023-02-25"],
        "amount": [100.0, 200.0]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    expected = ["paid_on_time", "paid_late"]
    assert result["payment_status"].tolist() == expected


def test_invalid_amount_missing():
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": [None]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_amount_non_numeric():
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": ["abc"]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_amount_zero():
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": [0]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_amount_negative():
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": [-5.0]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_due_date():
    df = pd.DataFrame({
        "due_date": ["not_a_date"],
        "paid_date": ["2023-01-10"],
        "amount": [100.0]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_paid_date_provided():
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["invalid_date"],
        "amount": [100.0]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_paid_date_empty_string():
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": [""],
        "amount": [100.0]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    # Empty string is considered provided but invalid (pd.to_datetime("") -> NaT)
    assert result["payment_status"].iloc[0] == "invalid"


def test_missing_paid_date_pending():
    df = pd.DataFrame({
        "due_date": ["2023-04-01"],
        "paid_date": [None],
        "amount": [150.0]
    })
    result = classify_payment_status(df, reference_date="2023-03-15")
    assert result["payment_status"].iloc[0] == "pending"


def test_missing_paid_date_overdue():
    df = pd.DataFrame({
        "due_date": ["2023-03-01"],
        "paid_date": [None],
        "amount": [150.0]
    })
    result = classify_payment_status(df, reference_date="2023-03-15")
    assert result["payment_status"].iloc[0] == "overdue"


def test_paid_on_time_equal_dates():
    df = pd.DataFrame({
        "due_date": ["2023-05-10"],
        "paid_date": ["2023-05-10"],
        "amount": [80.0]
    })
    result = classify_payment_status(df, reference_date="2023-06-01")
    assert result["payment_status"].iloc[0] == "paid_on_time"


def test_duplicate_rows():
    df = pd.DataFrame({
        "due_date": ["2023-01-15", "2023-01-15"],
        "paid_date": ["2023-01-10", None],
        "amount": [100.0, 100.0]
    })
    result = classify_payment_status(df, reference_date="2023-02-01")
    expected = ["paid_on_time", "overdue"]
    assert result["payment_status"].tolist() == expected


def test_reference_date_invalid():
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": [None],
        "amount": [100.0]
    })
    with pytest.raises(ValueError, match="reference_date must be a valid date-like value"):
        classify_payment_status(df, reference_date="bad_date")


def test_custom_column_names():
    df = pd.DataFrame({
        "dd": ["2023-01-15"],
        "pd": ["2023-01-10"],
        "amt": [200.0]
    })
    result = classify_payment_status(
        df,
        reference_date="2023-02-01",
        due_date_col="dd",
        paid_date_col="pd",
        amount_col="amt",
        output_col="status"
    )
    assert result["status"].iloc[0] == "paid_on_time"


def test_mixed_valid_and_invalid():
    df = pd.DataFrame({
        "due_date": ["2023-01-15", "2023-02-20", None],
        "paid_date": ["2023-01-10", None, "2023-03-01"],
        "amount": [100.0, 200.0, 300.0]
    })
    result = classify_payment_status(df, reference_date="2023-03-01")
    expected = ["paid_on_time", "overdue", "invalid"]
    assert result["payment_status"].tolist() == expected