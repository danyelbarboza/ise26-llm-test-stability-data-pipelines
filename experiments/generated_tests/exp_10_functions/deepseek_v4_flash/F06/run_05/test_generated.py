import pytest
import pandas as pd
import numpy as np
from ise26.targets import classify_payment_status


def test_classify_paid_on_time():
    """Valid payment paid on or before due date."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15", "2023-01-15"],
        "paid_date": ["2023-01-10", "2023-01-15"],
        "amount": [100.0, 200.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert list(result["payment_status"]) == ["paid_on_time", "paid_on_time"]


def test_classify_paid_late():
    """Valid payment paid after due date."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-20"],
        "amount": [150.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-25")
    assert result["payment_status"].iloc[0] == "paid_late"


def test_classify_overdue():
    """Unpaid payment past due date before reference date."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": [None],
        "amount": [300.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result["payment_status"].iloc[0] == "overdue"


def test_classify_pending():
    """Unpaid payment not yet due relative to reference date."""
    df = pd.DataFrame({
        "due_date": ["2023-01-25"],
        "paid_date": [None],
        "amount": [400.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result["payment_status"].iloc[0] == "pending"


def test_invalid_amount_missing():
    """Amount missing -> invalid."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": [None]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_amount_non_numeric():
    """Amount non‑numeric string -> invalid."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": ["abc"]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_amount_zero():
    """Amount equal to zero -> invalid."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": [0.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_amount_negative():
    """Amount negative -> invalid."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": [-50.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_invalid_due_date():
    """Invalid due date -> invalid regardless of other fields."""
    df = pd.DataFrame({
        "due_date": ["not_a_date", None],
        "paid_date": ["2023-01-10", "2023-01-10"],
        "amount": [100.0, 100.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert list(result["payment_status"]) == ["invalid", "invalid"]


def test_invalid_paid_date_provided():
    """Provided paid_date is invalid (malformed) -> invalid."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["invalid_date"],
        "amount": [100.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result["payment_status"].iloc[0] == "invalid"


def test_valid_paid_date_empty_string():
    """Empty string in paid_date treated as not provided (not invalid)."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": [""],
        "amount": [100.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-10")
    # Unpaid, due date after reference -> pending
    assert result["payment_status"].iloc[0] == "pending"


def test_valid_paid_date_na():
    """None/NaN in paid_date treated as unpaid."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15", "2023-01-25"],
        "paid_date": [None, np.nan],
        "amount": [100.0, 200.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert list(result["payment_status"]) == ["overdue", "pending"]


def test_reference_date_on_due_date():
    """Unpaid row with reference equal to due date -> pending (since not past due)."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": [None],
        "amount": [100.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-15")
    assert result["payment_status"].iloc[0] == "pending"


def test_mixed_classifications():
    """Multiple rows covering all statuses."""
    df = pd.DataFrame({
        "due_date": ["2023-01-10", "2023-01-15", "2023-01-20", "2023-01-25", "2023-01-30", "invalid"],
        "paid_date": ["2023-01-05", "2023-01-20", None, None, "bad_date", "2023-01-15"],
        "amount": [100.0, 200.0, 300.0, 400.0, 500.0, 600.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    expected = ["paid_on_time", "paid_late", "overdue", "pending", "invalid", "invalid"]
    assert list(result["payment_status"]) == expected


def test_empty_dataframe():
    """Empty DataFrame results in empty output column."""
    df = pd.DataFrame({"due_date": [], "paid_date": [], "amount": []})
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result.empty
    assert "payment_status" in result.columns


def test_duplicate_rows():
    """Duplicate rows should be classified independently."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15", "2023-01-15"],
        "paid_date": ["2023-01-10", None],
        "amount": [100.0, 100.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert list(result["payment_status"]) == ["paid_on_time", "overdue"]


def test_different_column_names():
    """Custom column names work correctly."""
    df = pd.DataFrame({
        "dd": ["2023-01-15", "2023-01-20"],
        "pd": ["2023-01-10", None],
        "amt": [150.0, 250.0]
    })
    result = classify_payment_status(
        df,
        reference_date="2023-01-25",
        due_date_col="dd",
        paid_date_col="pd",
        amount_col="amt",
        output_col="status"
    )
    assert list(result["status"]) == ["paid_on_time", "overdue"]


def test_invalid_reference_date_raises():
    """Invalid reference_date raises ValueError."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": [100.0]
    })
    with pytest.raises(ValueError, match="reference_date must be a valid date-like value"):
        classify_payment_status(df, reference_date="not_a_date")


def test_numeric_amount_as_string():
    """Numeric string in amount is accepted and parsed."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15"],
        "paid_date": ["2023-01-10"],
        "amount": ["200"]
    })
    result = classify_payment_status(df, reference_date="2023-01-20")
    assert result["payment_status"].iloc[0] == "paid_on_time"


def test_mixed_invalid_valid_paid_date():
    """Rows with valid paid dates are still valid even if other rows have invalid paid dates."""
    df = pd.DataFrame({
        "due_date": ["2023-01-15", "2023-01-20"],
        "paid_date": ["2023-01-10", "bad"],
        "amount": [100.0, 200.0]
    })
    result = classify_payment_status(df, reference_date="2023-01-25")
    assert list(result["payment_status"]) == ["paid_on_time", "invalid"]