import pandas as pd
import pytest
from ise26.targets import deduplicate_events


def test_keeps_rows_with_null_id():
    """Rows with null event_id are always kept unchanged."""
    df = pd.DataFrame({
        "event_id": [None, None, None],
        "updated_at": ["2022-01-01", "2022-01-02", "2022-01-03"],
        "value": [1, 2, 3],
    })
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)


def test_removes_duplicates_keeps_most_recent():
    """For same non-null event_id, only the row with the most recent timestamp remains."""
    df = pd.DataFrame({
        "event_id": ["A", "A", "A"],
        "updated_at": ["2022-01-01", "2022-01-03", "2022-01-02"],
        "value": [1, 3, 2],
    })
    result = deduplicate_events(df)
    assert len(result) == 1
    assert result.iloc[0]["event_id"] == "A"
    assert result.iloc[0]["updated_at"] == "2022-01-03"
    assert result.iloc[0]["value"] == 3


def test_invalid_timestamps_treated_as_old():
    """Invalid timestamps are considered older than any valid timestamp."""
    df = pd.DataFrame({
        "event_id": ["B", "B"],
        "updated_at": ["invalid", "2022-01-01"],
        "value": [1, 2],
    })
    result = deduplicate_events(df)
    assert len(result) == 1
    assert result.iloc[0]["value"] == 2


def test_timestamp_tie_keeps_last_row():
    """When timestamps are equal, the last row in original order is retained."""
    df = pd.DataFrame({
        "event_id": ["C", "C", "C"],
        "updated_at": ["2022-01-01", "2022-01-01", "2022-01-01"],
        "value": [1, 2, 3],
    })
    result = deduplicate_events(df)
    assert len(result) == 1
    assert result.iloc[0]["value"] == 3


def test_mixed_null_and_non_null_ids():
    """Null ids are preserved, non-null ids are deduplicated independently."""
    df = pd.DataFrame({
        "event_id": [None, "D", "D", None, "E"],
        "updated_at": ["2022-01-01", "2022-01-02", "2022-01-01", "2022-01-03", "2022-01-04"],
        "value": [1, 2, 3, 4, 5],
    })
    result = deduplicate_events(df)
    # Expect rows: null (val 1), "D" (val 2), null (val 4), "E" (val 5)
    expected_values = [1, 2, 4, 5]
    assert result["value"].tolist() == expected_values


def test_custom_column_names():
    """Function works with user‑supplied column names."""
    df = pd.DataFrame({
        "my_id": ["X", "X", "Y"],
        "my_ts": ["2022-01-03", "2022-01-01", "2022-01-02"],
    })
    result = deduplicate_events(df, id_col="my_id", timestamp_col="my_ts")
    # Only X (most recent) and Y kept
    assert len(result) == 2
    assert set(result["my_id"]) == {"X", "Y"}


def test_empty_dataframe():
    """Empty input returns empty output."""
    df = pd.DataFrame(columns=["event_id", "updated_at", "value"])
    result = deduplicate_events(df)
    assert len(result) == 0
    assert list(result.columns) == ["event_id", "updated_at", "value"]


def test_no_duplicates():
    """When all non-null ids are unique, every row is kept."""
    df = pd.DataFrame({
        "event_id": ["A", "B", "C"],
        "updated_at": ["2022-01-01", "2022-01-02", "2022-01-03"],
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)


def test_does_not_mutate_input():
    """The original DataFrame remains unchanged after the call."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["2022-01-01", "2022-01-02"],
        "value": [1, 2],
    })
    original = df.copy()
    deduplicate_events(df)
    pd.testing.assert_frame_equal(df, original)


def test_datetime_columns():
    """Timestamps as datetime objects work correctly."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": [pd.Timestamp("2022-01-02"), pd.Timestamp("2022-01-01")],
    })
    result = deduplicate_events(df)
    assert len(result) == 1
    assert result.iloc[0]["updated_at"] == pd.Timestamp("2022-01-02")


def test_mixed_timestamp_types():
    """Function can handle a mix of valid and invalid strings, NaT, etc."""
    df = pd.DataFrame({
        "event_id": ["A", "A", "A"],
        "updated_at": ["2022-01-01", None, "invalid_date"],
    })
    # Both invalid and NaT are treated as older, so the valid one should be kept
    result = deduplicate_events(df)
    assert len(result) == 1
    assert result.iloc[0]["updated_at"] == "2022-01-01"