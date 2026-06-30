import pandas as pd
import numpy as np
from ise26.targets import classify_payment_status


class TestClassifyPaymentStatus:
    """Test suite for classify_payment_status function."""

    # ------------------------------------------------------------------
    # Helper to create common test DataFrame
    # ------------------------------------------------------------------
    @staticmethod
    def _make_basic_df():
        """Return a simple DataFrame with typical columns."""
        return pd.DataFrame({
            'due_date':   ['2023-01-15', '2023-01-15', '2023-02-01', '2023-02-01', pd.NaT],
            'paid_date':  ['2023-01-10', '2023-01-20', None,          None,         '2023-01-15'],
            'amount':     [100.0,         100.0,        50.0,          50.0,         30.0]
        })

    # ------------------------------------------------------------------
    # Basic classification scenarios
    # ------------------------------------------------------------------
    def test_paid_on_time(self):
        """Row with paid_date <= due_date should be 'paid_on_time'."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'paid_on_time'

    def test_paid_late(self):
        """Row with paid_date > due_date should be 'paid_late'."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-20'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-25')
        assert result['payment_status'].iloc[0] == 'paid_late'

    def test_overdue(self):
        """Unpaid row with reference_date > due_date -> 'overdue'."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': [None],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'overdue'

    def test_pending(self):
        """Unpaid row with reference_date <= due_date -> 'pending'."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': [None],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-15')
        assert result['payment_status'].iloc[0] == 'pending'

    # ------------------------------------------------------------------
    # Invalid rows
    # ------------------------------------------------------------------
    def test_invalid_missing_amount(self):
        """Missing amount (NaN) -> invalid."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [np.nan]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_non_numeric_amount(self):
        """Non‑numeric amount -> invalid."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': ['abc']
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_zero_amount(self):
        """Amount equal to 0 -> invalid."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [0.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_negative_amount(self):
        """Amount < 0 -> invalid."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [-10.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_due_date(self):
        """Invalid due_date (unparseable) -> invalid."""
        df = pd.DataFrame({
            'due_date': ['not_a_date'],
            'paid_date': ['2023-01-10'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_paid_date_provided_but_invalid(self):
        """Provided paid_date that cannot be parsed -> invalid."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['bad_date'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_empty_string_paid_date_treated_as_missing(self):
        """Empty string paid_date is not considered provided -> unpaid."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': [''],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        # Since paid_date is effectively missing, should be overdue (ref > due)
        assert result['payment_status'].iloc[0] == 'overdue'

    def test_invalid_paid_date_nat(self):
        """Explicit NaT in paid_date is missing, not invalid (since not provided)."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': [pd.NaT],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'overdue'

    # ------------------------------------------------------------------
    # Validation of reference_date
    # ------------------------------------------------------------------
    def test_invalid_reference_date_raises_valueerror(self):
        """If reference_date cannot be parsed, raise ValueError."""
        df = self._make_basic_df()
        with pytest.raises(ValueError, match="reference_date must be a valid date-like value"):
            classify_payment_status(df, reference_date='invalid_date')

    def test_valid_reference_date_as_datetime(self):
        """reference_date can be a datetime object."""
        import datetime
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': [None],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date=datetime.date(2023, 1, 20))
        assert result['payment_status'].iloc[0] == 'overdue'

    # ------------------------------------------------------------------
    # Original DataFrame is not modified
    # ------------------------------------------------------------------
    def test_original_dataframe_not_modified(self):
        """The function returns a new DataFrame, the original remains unchanged."""
        original = self._make_basic_df().copy()
        original_copy = original.copy()
        classify_payment_status(original, reference_date='2023-02-01')
        pd.testing.assert_frame_equal(original, original_copy)

    # ------------------------------------------------------------------
    # Custom column names
    # ------------------------------------------------------------------
    def test_custom_column_names(self):
        """Use non‑default column names and ensure correct mapping."""
        df = pd.DataFrame({
            'd': ['2023-01-15'],
            'p': ['2023-01-10'],
            'a': [100.0]
        })
        result = classify_payment_status(
            df,
            reference_date='2023-01-20',
            due_date_col='d',
            paid_date_col='p',
            amount_col='a',
            output_col='status'
        )
        assert 'status' in result.columns
        assert result['status'].iloc[0] == 'paid_on_time'
        # Original column names still present
        assert 'd' in result.columns

    # ------------------------------------------------------------------
    # Mixed scenario
    # ------------------------------------------------------------------
    def test_mixed_statuses(self):
        """Test a DataFrame with all six statuses in one go."""
        df = pd.DataFrame({
            'due_date': ['2023-01-01', '2023-01-01', '2023-01-01', '2023-01-01',
                         '2023-01-01', '2023-01-01'],
            'paid_date': ['2022-12-31', '2023-01-05', None,           None,
                          None,          '2023-01-05'],
            'amount':    [100.0,         100.0,        100.0,         0.0,
                          100.0,         'bad']
        })
        # expected: paid_on_time, paid_late, pending (ref_date=2023-01-01 <= due),
        # invalid (zero), overdue (ref=2023-01-02 > due), invalid (bad amount)
        result = classify_payment_status(df, reference_date='2023-01-02')
        expected = ['paid_on_time', 'paid_late', 'pending',
                    'invalid', 'overdue', 'invalid']
        assert result['payment_status'].tolist() == expected

    # ------------------------------------------------------------------
    # Empty DataFrame
    # ------------------------------------------------------------------
    def test_empty_dataframe(self):
        """Empty DataFrame returns empty output column."""
        df = pd.DataFrame(columns=['due_date', 'paid_date', 'amount'])
        result = classify_payment_status(df, reference_date='2023-01-01')
        assert result.shape[0] == 0
        assert 'payment_status' in result.columns

    # ------------------------------------------------------------------
    # All invalid rows
    # ------------------------------------------------------------------
    def test_all_invalid(self):
        """Every row invalid because of bad amount or date."""
        df = pd.DataFrame({
            'due_date': ['2023-01-01', pd.NaT],
            'paid_date': [None, 'bad'],
            'amount': [0, 100]
        })
        result = classify_payment_status(df, reference_date='2023-01-01')
        assert (result['payment_status'] == 'invalid').all()

    # ------------------------------------------------------------------
    # Duplicate rows (no special handling expected, just ensure they work)
    # ------------------------------------------------------------------
    def test_duplicate_rows(self):
        """Rows with identical data are classified independently."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15', '2023-01-15'],
            'paid_date': ['2023-01-10', '2023-01-10'],
            'amount': [100.0, 100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert (result['payment_status'] == 'paid_on_time').all()

    # ------------------------------------------------------------------
    # Null in due_date (NaT) -> invalid
    # ------------------------------------------------------------------
    def test_null_due_date(self):
        """NaT in due_date -> invalid."""
        df = pd.DataFrame({
            'due_date': [pd.NaT],
            'paid_date': ['2023-01-10'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    # ------------------------------------------------------------------
    # Amount as string that can be parsed (e.g., '100.5') -> valid
    # ------------------------------------------------------------------
    def test_amount_string_parseable(self):
        """String amount that converts to numeric is valid."""
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': ['100.5']
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'paid_on_time'