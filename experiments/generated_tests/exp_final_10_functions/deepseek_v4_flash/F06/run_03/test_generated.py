import pandas as pd
import pytest
from pandas import NaT, Timestamp

from ise26.targets import classify_payment_status


def test_invalid_amount_missing():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": [None],
        "amount": [None]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "invalid"
    assert result["amount"].isna().iloc[0]


def test_invalid_amount_zero():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": [None],
        "amount": [0.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_amount_negative():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": [None],
        "amount": [-100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_amount_non_numeric():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": [None],
        "amount": ["abc"]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_due_date():
    df = pd.DataFrame({
        "due_date": ["not-a-date"],
        "paid_date": [None],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_due_date_missing():
    df = pd.DataFrame({
        "due_date": [None],
        "paid_date": [None],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_paid_date_provided_invalid():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": ["bad-date"],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_paid_on_time():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": ["2024-01-14"],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "paid_on_time"


def test_paid_on_time_same_date():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": ["2024-01-15"],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "paid_on_time"


def test_paid_late():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": ["2024-01-16"],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "paid_late"


def test_overdue():
    df = pd.DataFrame({
        "due_date": ["2024-01-10"],
        "paid_date": [None],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "overdue"


def test_pending():
    df = pd.DataFrame({
        "due_date": ["2024-02-01"],
        "paid_date": [None],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "pending"


def test_pending_reference_equal_to_due():
    df = pd.DataFrame({
        "due_date": ["2024-01-20"],
        "paid_date": [None],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "pending"


def test_mixed_statuses():
    df = pd.DataFrame({
        "due_date": ["2024-01-10", "2024-01-15", "2024-01-20", "2024-01-05", "2024-02-01"],
        "paid_date": ["2024-01-09", None, "2024-01-22", None, None],
        "amount": [100.0, 200.0, 300.0, 400.0, 500.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    expected = ["paid_on_time", "overdue", "paid_late", "overdue", "pending"]
    assert result["payment_status"].tolist() == expected


def test_preserves_row_order():
    df = pd.DataFrame({
        "due_date": ["2024-02-01", "2024-01-15", "2024-01-10"],
        "paid_date": [None, None, "2024-01-09"],
        "amount": [100.0, 200.0, 300.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result.index.tolist() == [0, 1, 2]
    assert result["payment_status"].tolist() == ["pending", "overdue", "paid_on_time"]


def test_new_column_added_no_side_effect_original():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": [None],
        "amount": [100.0]
    })
    original_columns = list(df.columns)
    result = classify_payment_status(df, "2024-01-20")
    assert "payment_status" not in df.columns
    assert "payment_status" in result.columns
    assert list(result.columns) == original_columns + ["payment_status"]


def test_original_dataframe_not_mutated():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": [None],
        "amount": [100.0]
    })
    original = df.copy()
    _ = classify_payment_status(df, "2024-01-20")
    pd.testing.assert_frame_equal(df, original)


def test_provided_paid_date_invalid_ignores_amount_validity():
    # Even if amount is valid, invalid paid date makes it invalid
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": ["invalid"],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_missing_paid_date_treated_as_unpaid():
    df = pd.DataFrame({
        "due_date": ["2024-01-10"],
        "paid_date": [None],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    assert result["payment_status"].iloc[0] == "overdue"


def test_empty_string_paid_date_treated_as_unpaid():
    df = pd.DataFrame({
        "due_date": ["2024-01-10"],
        "paid_date": [""],
        "amount": [100.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    # Empty string is not provided (stripped becomes empty), so unpaid
    assert result["payment_status"].iloc[0] == "overdue"


def test_invalid_reference_date_raises_valueerror():
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": [None],
        "amount": [100.0]
    })
    with pytest.raises(ValueError, match="reference_date must be a valid date-like value"):
        classify_payment_status(df, "bad-date")


def test_custom_column_names():
    df = pd.DataFrame({
        "my_due": ["2024-01-10"],
        "my_paid": [None],
        "my_amount": [100.0]
    })
    result = classify_payment_status(
        df,
        "2024-01-20",
        due_date_col="my_due",
        paid_date_col="my_paid",
        amount_col="my_amount",
        output_col="status"
    )
    assert result["status"].iloc[0] == "overdue"


def test_all_invalid_due_dates():
    df = pd.DataFrame({
        "due_date": [None, "abc", "", "2024-01-01"],
        "paid_date": [None, None, None, "bad"],
        "amount": [100.0, 200.0, 300.0, 400.0]
    })
    result = classify_payment_status(df, "2024-01-20")
    expected = ["invalid", "invalid", "invalid", "invalid"]
    assert result["payment_status"].tolist() == expected


def test_all_paid_on_time():
    df = pd.DataFrame({
        "due_date": ["2024-01-01", "2024-01-15", "2024-02-01"],
        "paid_date": ["2024-01-01", "2024-01-10", "2024-01-25"],
        "amount": [10, 20, 30]
    })
    result = classify_payment_status(df, "2024-02-01")
    assert all(s == "paid_on_time" for s in result["payment_status"])