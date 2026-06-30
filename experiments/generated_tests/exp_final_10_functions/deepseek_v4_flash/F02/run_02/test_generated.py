import pandas as pd
import pytest
from ise26.targets import deduplicate_events


def test_deduplicate_basic_keeps_most_recent():
    """Basic dedup: same id, different timestamps, keep most recent."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["2023-01-01", "2023-01-02"],
        "value": [1, 2],
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": ["2023-01-02"],
        "value": [2],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_deduplicate_tie_keeps_last():
    """Same id, same timestamp, keep last row in original order."""
    df = pd.DataFrame({
        "event_id": ["B", "B", "B"],
        "updated_at": ["2023-01-01", "2023-01-01", "2023-01-01"],
        "value": [10, 20, 30],
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["B"],
        "updated_at": ["2023-01-01"],
        "value": [30],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_preserves_null_ids():
    """Rows with null event_id are kept unchanged."""
    df = pd.DataFrame({
        "event_id": [None, "X", None],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "value": [1, 2, 3],
    })
    result = deduplicate_events(df)
    # null rows untouched, "X" deduped (only one)
    expected = pd.DataFrame({
        "event_id": [None, "X", None],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "value": [1, 2, 3],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_multiple_null_ids_kept_all():
    """Multiple null ids are all preserved, even if timestamps identical."""
    df = pd.DataFrame({
        "event_id": [None, None],
        "updated_at": ["2023-01-01", "2023-01-01"],
        "value": [100, 200],
    })
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_timestamps_treated_as_old():
    """Invalid timestamp (NaT) considered older than valid one."""
    df = pd.DataFrame({
        "event_id": ["Z", "Z"],
        "updated_at": ["invalid", "2023-01-02"],
        "value": [1, 2],
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["Z"],
        "updated_at": ["2023-01-02"],
        "value": [2],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_timestamp_tie_with_valid():
    """If invalid is older, valid timestamp rows retained."""
    df = pd.DataFrame({
        "event_id": ["Y", "Y"],
        "updated_at": ["2023-01-01", "garbage"],
        "value": [10, 20],
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["Y"],
        "updated_at": ["2023-01-01"],
        "value": [10],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_invalid_and_nat():
    """Multiple rows with invalid parse and same id: keep last by original order."""
    df = pd.DataFrame({
        "event_id": ["M", "M", "M"],
        "updated_at": ["bad", "worse", "awful"],
        "value": [1, 2, 3],
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["M"],
        "updated_at": ["awful"],
        "value": [3],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_custom_id_and_timestamp_columns():
    """Use non-default column names."""
    df = pd.DataFrame({
        "my_id": ["A", "A"],
        "my_ts": ["2023-01-01", "2023-01-02"],
        "info": ["first", "second"],
    })
    result = deduplicate_events(df, id_col="my_id", timestamp_col="my_ts")
    expected = pd.DataFrame({
        "my_id": ["A"],
        "my_ts": ["2023-01-02"],
        "info": ["second"],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_no_mutation_of_input():
    """Input DataFrame should not be modified."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["2023-01-01", "2023-01-02"],
        "value": [1, 2],
    })
    df_copy = df.copy()
    _ = deduplicate_events(df)
    pd.testing.assert_frame_equal(df, df_copy)


def test_returns_new_object():
    """Result is a different DataFrame object."""
    df = pd.DataFrame({"event_id": ["A"], "updated_at": ["2023-01-01"]})
    result = deduplicate_events(df)
    assert result is not df


def test_empty_dataframe():
    """Empty input returns empty output."""
    df = pd.DataFrame({"event_id": pd.Series(dtype="object"), "updated_at": pd.Series(dtype="object")})
    result = deduplicate_events(df)
    assert len(result) == 0
    assert list(result.columns) == ["event_id", "updated_at"]


def test_all_identical_ids_same_timestamp():
    """All rows identical in id and timestamp, keep last only."""
    df = pd.DataFrame({
        "event_id": ["X", "X", "X"],
        "updated_at": ["2023-01-01", "2023-01-01", "2023-01-01"],
        "val": [1, 2, 3],
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["X"],
        "updated_at": ["2023-01-01"],
        "val": [3],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_null_and_nonnull_with_duplicates():
    """Null rows preserved, non-null deduped, original order maintained."""
    df = pd.DataFrame({
        "event_id": ["A", None, "A", "B", None],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-01", "2023-01-04"],
        "value": [1, 2, 3, 4, 5],
    })
    result = deduplicate_events(df)
    # Expect: keep last A (row 2), keep B (row 3), keep both null rows (rows 1,4), order by original index
    expected = pd.DataFrame({
        "event_id": ["A", None, "B", None],
        "updated_at": ["2023-01-03", "2023-01-02", "2023-01-01", "2023-01-04"],
        "value": [3, 2, 4, 5],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_timestamps_various_types():
    """Timestamp column can contain datetime objects or strings."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": [pd.Timestamp("2023-01-01"), "2023-01-02"],
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": ["2023-01-02"],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_preserves_dtypes():
    """Result columns maintain original dtypes where possible."""
    df = pd.DataFrame({
        "event_id": pd.Series(["A", "A"], dtype="string"),
        "updated_at": pd.Series(["2023-01-01", "2023-01-02"], dtype="string"),
        "value": pd.Series([1, 2], dtype="int64"),
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": pd.Series(["A"], dtype="string"),
        "updated_at": pd.Series(["2023-01-02"], dtype="string"),
        "value": pd.Series([2], dtype="int64"),
    })
    pd.testing.assert_frame_equal(result, expected, check_dtype=True)