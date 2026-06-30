import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal
from ise26.targets import deduplicate_events


def test_basic_deduplication_keep_most_recent():
    """Should keep the row with the most recent timestamp for a given id."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["2023-01-01", "2023-01-02"],
        "data": ["old", "new"]
    })
    result = deduplicate_events(df, id_col="event_id", timestamp_col="updated_at")
    expected = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": ["2023-01-02"],
        "data": ["new"]
    })
    assert_frame_equal(result, expected)


def test_timestamp_tie_keep_last_row():
    """When timestamps tie, keep the last row in original order."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["2023-01-01", "2023-01-01"],
        "data": ["first", "last"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": ["2023-01-01"],
        "data": ["last"]
    })
    assert_frame_equal(result, expected)


def test_null_identifiers_preserved():
    """Rows with null event_id should all be kept."""
    df = pd.DataFrame({
        "event_id": [np.nan, np.nan],
        "updated_at": ["2023-01-01", "2023-01-02"],
        "data": ["x", "y"]
    })
    result = deduplicate_events(df)
    expected = df.copy()  # all rows kept, same order
    assert_frame_equal(result, expected)


def test_mixed_null_and_nonnull():
    """Null ids preserved, duplicates among non-null ids removed."""
    df = pd.DataFrame({
        "event_id": ["A", np.nan, "A", np.nan],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
        "data": ["old", "n1", "new", "n2"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A", np.nan, np.nan],
        "updated_at": ["2023-01-03", "2023-01-02", "2023-01-04"],
        "data": ["new", "n1", "n2"]
    })
    assert_frame_equal(result, expected)


def test_invalid_timestamp_treated_as_older():
    """NaT generated from invalid timestamp should be considered older than valid."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["not-a-date", "2023-01-01"],
        "data": ["invalid", "valid"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": ["2023-01-01"],
        "data": ["valid"]
    })
    assert_frame_equal(result, expected)


def test_multiple_duplicates_same_id():
    """Multiple rows with same id, keep the most recent."""
    df = pd.DataFrame({
        "event_id": ["X", "X", "X"],
        "updated_at": ["2023-01-01", "2023-01-03", "2023-01-02"],
        "data": ["a", "c", "b"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["X"],
        "updated_at": ["2023-01-03"],
        "data": ["c"]
    })
    assert_frame_equal(result, expected)


def test_no_duplicates():
    """All event_ids unique, rows should remain unchanged."""
    df = pd.DataFrame({
        "event_id": ["A", "B", "C"],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "data": [1, 2, 3]
    })
    result = deduplicate_events(df)
    expected = df.copy()
    assert_frame_equal(result, expected)


def test_empty_dataframe():
    """Empty input should return empty dataframe."""
    df = pd.DataFrame(columns=["event_id", "updated_at", "data"])
    result = deduplicate_events(df)
    assert result.empty
    assert list(result.columns) == ["event_id", "updated_at", "data"]


def test_custom_column_names():
    """Custom id and timestamp columns should work."""
    df = pd.DataFrame({
        "my_id": ["A", "A"],
        "my_ts": ["2023-01-01", "2023-01-02"],
        "value": [10, 20]
    })
    result = deduplicate_events(df, id_col="my_id", timestamp_col="my_ts")
    expected = pd.DataFrame({
        "my_id": ["A"],
        "my_ts": ["2023-01-02"],
        "value": [20]
    })
    assert_frame_equal(result, expected)


def test_input_not_mutated():
    """Original dataframe should not be modified."""
    original = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["2023-01-01", "2023-01-02"],
        "data": ["old", "new"]
    })
    df_copy = original.copy()
    deduplicate_events(original)
    assert_frame_equal(original, df_copy)