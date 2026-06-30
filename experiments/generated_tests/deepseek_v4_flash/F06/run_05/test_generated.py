import pandas as pd
import pytest
from ise26.targets import classify_payment_status


def test_invalid_reference_date_raises_error():
    """A invalid reference_date must raise ValueError."""
    df = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": ["2024-01-10"],
        "amount": [100.0]
    })
    with pytest.raises(ValueError, match="reference_date must be a valid date-like value"):
        classify_payment_status(df, reference_date="not_a_date")


def test_returns_new_dataframe():
    """Function must return a new DataFrame, not modify the original."""
    original = pd.DataFrame({
        "due_date": ["2024-01-15"],
        "paid_date": ["2024-01-10"],
        "amount": [100.0]
    })
    result = classify_payment_status(original, reference_date="2024-01-20")
    assert result is not original
    assert "payment_status" in result.columns
    assert "payment_status" not in original.columns


class TestInvalidAmount:
    @pytest.mark.parametrize("amount", [None, "abc", "1,2", pd.NA, 0, -1, -0.01])
    def test_invalid_amount_classified_invalid(self, amount):
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": ["2024-01-10"],
            "amount": [amount]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].iloc[0] == "invalid"

    def test_missing_amount(self):
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": ["2024-01-10"],
            "amount": [float("nan")]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].iloc[0] == "invalid"


class TestInvalidDueDate:
    @pytest.mark.parametrize("due_date", [None, "abc", "", pd.NA])
    def test_invalid_due_date_classified_invalid(self, due_date):
        df = pd.DataFrame({
            "due_date": [due_date],
            "paid_date": [None],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].iloc[0] == "invalid"


class TestInvalidPaidDate:
    @pytest.mark.parametrize("paid_date", [None, "", pd.NA])
    def test_missing_paid_date_does_not_cause_invalid(self, paid_date):
        """Missing paid_date is allowed; row will be classified as pending/overdue."""
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": [paid_date],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        # due_date is valid, amount valid -> either pending or overdue
        assert result["payment_status"].iloc[0] in ("pending", "overdue")

    @pytest.mark.parametrize("paid_date", ["not_a_date", "2024-13-01", "abc123"])
    def test_invalid_provided_paid_date_classified_invalid(self, paid_date):
        """A provided but invalid paid date must be treated as invalid."""
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": [paid_date],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].iloc[0] == "invalid"


class TestPaymentStatus:
    def test_paid_on_time_when_paid_before_due(self):
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": ["2024-01-10"],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].iloc[0] == "paid_on_time"

    def test_paid_on_time_when_paid_on_due(self):
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": ["2024-01-15"],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].iloc[0] == "paid_on_time"

    def test_paid_late_when_paid_after_due(self):
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": ["2024-01-20"],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-25")
        assert result["payment_status"].iloc[0] == "paid_late"

    def test_pending_when_unpaid_and_reference_before_or_on_due(self):
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": [None],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-15")
        assert result["payment_status"].iloc[0] == "pending"

    def test_overdue_when_unpaid_and_reference_after_due(self):
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": [None],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].iloc[0] == "overdue"

    def test_reference_date_as_datetime(self):
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": [None],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date=pd.Timestamp("2024-01-20"))
        assert result["payment_status"].iloc[0] == "overdue"


class TestSpecialCases:
    def test_duplicate_rows_all_independently_classified(self):
        """Duplicates in input must be processed independently."""
        df = pd.DataFrame({
            "due_date": ["2024-01-15", "2024-01-15"],
            "paid_date": [None, "2024-01-10"],
            "amount": [100.0, 100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].tolist() == ["overdue", "paid_on_time"]

    def test_mixed_types_in_dates(self):
        """Both date columns can contain strings or datetime objects."""
        df = pd.DataFrame({
            "due_date": [pd.Timestamp("2024-01-15")],
            "paid_date": ["2024-01-10"],
            "amount": [100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-20")
        assert result["payment_status"].iloc[0] == "paid_on_time"

    def test_reference_date_string_various_formats(self):
        """Different date string formats should be accepted."""
        df = pd.DataFrame({
            "due_date": ["2024-01-15"],
            "paid_date": [None],
            "amount": [100.0]
        })
        for ref in ["2024-01-20", "20/01/2024", "2024-01-20 12:00"]:
            result = classify_payment_status(df, reference_date=ref)
            assert result["payment_status"].iloc[0] == "overdue"

    def test_multiple_rows_various_statuses(self):
        """Test a batch of rows with different characteristics."""
        df = pd.DataFrame({
            "due_date": [
                "2024-01-15",  # paid on time
                "2024-01-15",  # invalid amount (zero)
                "2024-01-15",  # paid late
                "2024-01-20",  # pending
                "2024-01-10",  # overdue
                None,          # invalid due date
                "2024-01-15",  # invalid paid date provided
            ],
            "paid_date": [
                "2024-01-10",
                "2024-01-10",
                "2024-01-20",
                None,
                None,
                "2024-01-10",
                "invalid",
            ],
            "amount": [100.0, 0.0, 100.0, 100.0, 100.0, 100.0, 100.0]
        })
        result = classify_payment_status(df, reference_date="2024-01-15")
        expected = [
            "paid_on_time",
            "invalid",
            "paid_late",
            "pending",
            "overdue",
            "invalid",
            "invalid",
        ]
        assert result["payment_status"].tolist() == expected