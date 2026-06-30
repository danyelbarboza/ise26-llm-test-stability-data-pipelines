import pytest
import pandas as pd
import numpy as np
from ise26.targets import classify_payment_status

class TestClassifyPaymentStatus:
    def test_paid_on_time(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'paid_on_time'

    def test_paid_late(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-20'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-25')
        assert result['payment_status'].iloc[0] == 'paid_late'

    def test_overdue(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': [None],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'overdue'

    def test_pending(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-20'],
            'paid_date': [None],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'pending'

    def test_pending_reference_before_due(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-20'],
            'paid_date': [None],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-15')
        assert result['payment_status'].iloc[0] == 'pending'

    def test_invalid_amount_missing(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [None]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_amount_non_numeric(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': ['abc']
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_amount_zero(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_amount_negative(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [-1]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_due_date(self):
        df = pd.DataFrame({
            'due_date': ['not-a-date'],
            'paid_date': ['2023-01-10'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_invalid_paid_date_provided(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['invalid-date'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'invalid'

    def test_empty_string_paid_date_treated_as_missing(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': [''],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-10')
        # vazia => não fornecida, reference_date <= due_date => pending
        assert result['payment_status'].iloc[0] == 'pending'

    def test_whitespace_paid_date_treated_as_missing(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['   '],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].iloc[0] == 'overdue'

    def test_custom_column_names(self):
        df = pd.DataFrame({
            'my_due': ['2023-01-15'],
            'my_paid': ['2023-01-10'],
            'my_amt': [100.0]
        })
        result = classify_payment_status(
            df, reference_date='2023-01-20',
            due_date_col='my_due',
            paid_date_col='my_paid',
            amount_col='my_amt',
            output_col='custom_status'
        )
        assert 'custom_status' in result.columns
        assert result['custom_status'].iloc[0] == 'paid_on_time'

    def test_output_is_new_dataframe(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [100.0]
        })
        original_columns = df.columns.tolist()
        result = classify_payment_status(df, reference_date='2023-01-20')
        # original não deve ter a coluna de status
        assert df.columns.tolist() == original_columns
        # resultado deve ter a coluna adicional
        assert 'payment_status' in result.columns
        assert result is not df

    def test_multiple_rows_all_statuses(self):
        df = pd.DataFrame({
            'due_date': [
                '2023-01-15',  # paid_on_time
                '2023-01-15',  # paid_late
                '2023-01-15',  # overdue
                '2023-01-20',  # pending
                '2023-01-15',  # invalid_amount
                '2023-01-15',  # invalid_due
                '2023-01-15'   # invalid_paid_date provided
            ],
            'paid_date': [
                '2023-01-10',
                '2023-01-20',
                None,
                None,
                '2023-01-10',
                '2023-01-10',
                'bad-date'
            ],
            'amount': [
                100.0,
                100.0,
                100.0,
                100.0,
                None,
                100.0,
                100.0
            ]
        })
        # Trocando uma due_date para inválida
        df.loc[5, 'due_date'] = 'not-valid'
        result = classify_payment_status(df, reference_date='2023-01-18')
        expected = ['paid_on_time', 'paid_late', 'overdue', 'pending', 'invalid', 'invalid', 'invalid']
        assert result['payment_status'].tolist() == expected

    def test_duplicates(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15', '2023-01-15'],
            'paid_date': ['2023-01-10', None],
            'amount': [100.0, 100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].tolist() == ['paid_on_time', 'overdue']

    def test_reference_date_invalid_raises(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [100.0]
        })
        with pytest.raises(ValueError, match="reference_date must be a valid date-like value"):
            classify_payment_status(df, reference_date='not-a-date')

    def test_timestamp_reference_date(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15'],
            'paid_date': ['2023-01-10'],
            'amount': [100.0]
        })
        result = classify_payment_status(df, reference_date=pd.Timestamp('2023-01-20'))
        assert result['payment_status'].iloc[0] == 'paid_on_time'

    def test_numeric_amount_with_zeros_and_positives(self):
        df = pd.DataFrame({
            'due_date': ['2023-01-15', '2023-01-15'],
            'paid_date': ['2023-01-10', '2023-01-10'],
            'amount': [0.0, 100.0]
        })
        result = classify_payment_status(df, reference_date='2023-01-20')
        assert result['payment_status'].tolist() == ['invalid', 'paid_on_time']