import pandas as pd
import pytest
from ise26.targets import deduplicate_events


def test_deduplicate_events_no_duplicates():
    """No duplicate event IDs, all rows should remain unchanged."""
    df = pd.DataFrame({
        "event_id": [1, 2, 3],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
        "value": ["a", "b", "c"]
    })
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_events_simple_duplicate():
    """Two rows with same event_id, keep the most recent timestamp."""
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02"]),
        "value": ["old", "new"]
    })
    result = deduplicate_events(df)
    expected = df.iloc[[1]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_events_keep_last_on_tie():
    """Same event_id and same timestamp, keep the last row in original order."""
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-01"]),
        "value": ["first", "second"]
    })
    result = deduplicate_events(df)
    expected = df.iloc[[1]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_events_preserve_null_ids():
    """Rows with null event_id should be kept even if they have same timestamp."""
    df = pd.DataFrame({
        "event_id": [None, None],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-01"]),
        "value": ["a", "b"]
    })
    result = deduplicate_events(df)
    expected = df.reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_events_mixed_null_and_duplicates():
    """Null IDs preserved, non-null duplicates deduplicated."""
    df = pd.DataFrame({
        "event_id": [1, 1, None, None, 2],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-03", "2023-01-02", "2023-01-02", "2023-01-04"]),
        "value": ["old", "new", "null1", "null2", "single"]
    })
    result = deduplicate_events(df)
    # Expected: keep row index1 (id=1 with newest timestamp), rows 2,3 (null ids), row4 (id=2 single)
    expected = pd.DataFrame({
        "event_id": [1, None, None, 2],
        "updated_at": pd.to_datetime(["2023-01-03", "2023-01-02", "2023-01-02", "2023-01-04"]),
        "value": ["new", "null1", "null2", "single"]
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


def test_deduplicate_events_invalid_timestamp_older_than_valid():
    """Invalid timestamps treated as older than valid ones."""
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": ["not_a_date", "2023-01-01"],
        "value": ["invalid", "valid"]
    })
    result = deduplicate_events(df)
    # The valid timestamp row should be kept because invalid is older.
    # Our sorting: [id=1, _parsed_timestamp=NaT (old), _original_order=0] then [id=1, 2023-01-01, 1] -> keep last per id (index1)
    expected = df.iloc[[1]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_events_both_invalid_timestamps():
    """Both timestamps invalid, keep last row per event_id."""
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": ["bad", "bad"],
        "value": ["first", "second"]
    })
    result = deduplicate_events(df)
    expected = df.iloc[[1]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_events_imutability():
    """Input DataFrame should not be modified."""
    df = pd.DataFrame({
        "event_id": [1, 2],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02"]),
        "value": ["a", "b"]
    })
    df_original = df.copy()
    _ = deduplicate_events(df)
    pd.testing.assert_frame_equal(df, df_original)


def test_deduplicate_events_custom_column_names():
    """Use custom id and timestamp column names."""
    df = pd.DataFrame({
        "my_id": [10, 10, 20],
        "my_ts": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01"]),
        "data": ["x", "y", "z"]
    })
    result = deduplicate_events(df, id_col="my_id", timestamp_col="my_ts")
    expected = pd.DataFrame({
        "my_id": [10, 20],
        "my_ts": pd.to_datetime(["2023-01-02", "2023-01-01"]),
        "data": ["y", "z"]
    })
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


def test_deduplicate_events_many_duplicates():
    """Multiple duplicates for same id, only the most recent (last on tie) kept."""
    df = pd.DataFrame({
        "event_id": [1, 1, 1, 1],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-03", "2023-01-02", "2023-01-03"]),
        "value": ["a", "b", "c", "d"]   # indices 1 and 3 both have 2023-01-03, keep last (3)
    })
    result = deduplicate_events(df)
    expected = df.iloc[[3]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_events_empty_dataframe():
    """Empty DataFrame should return empty DataFrame."""
    df = pd.DataFrame(columns=["event_id", "updated_at", "value"])
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_events_single_row():
    """Single row should be returned unchanged."""
    df = pd.DataFrame({
        "event_id": [1],
        "updated_at": pd.to_datetime(["2023-01-01"]),
        "value": ["a"]
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)


def test_deduplicate_events_timestamp_nat():
    """NaT timestamps treated as invalid (old)."""
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": [pd.NaT, pd.to_datetime("2023-01-01")],
        "value": ["nat", "valid"]
    })
    result = deduplicate_events(df)
    expected = df.iloc[[1]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)