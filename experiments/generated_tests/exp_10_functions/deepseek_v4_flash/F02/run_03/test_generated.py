import pandas as pd
import pytest
from ise26.targets import deduplicate_events


def test_basic_deduplication_keeps_most_recent():
    df = pd.DataFrame({
        "event_id": [1, 1, 2, 2, 3],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-03", "2023-01-01"]),
        "value": ["a", "b", "c", "d", "e"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1, 2, 3],
        "updated_at": pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-01"]),
        "value": ["b", "d", "e"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_ties_in_timestamps_keep_last_row():
    df = pd.DataFrame({
        "event_id": [1, 1, 1],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-01", "2023-01-01"]),
        "value": ["a", "b", "c"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1],
        "updated_at": pd.to_datetime(["2023-01-01"]),
        "value": ["c"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_timestamps_treated_as_older():
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": ["invalid", "2023-01-01"],
        "value": ["a", "b"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1],
        "updated_at": ["2023-01-01"],
        "value": ["b"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_null_identifiers_preserved():
    df = pd.DataFrame({
        "event_id": [None, None, 1, 1],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-02"]),
        "value": ["a", "b", "c", "d"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [None, None, 1],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-02"]),
        "value": ["a", "b", "d"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_no_duplicates():
    df = pd.DataFrame({
        "event_id": [1, 2, 3],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
        "value": ["a", "b", "c"]
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)


def test_empty_dataframe():
    df = pd.DataFrame({"event_id": [], "updated_at": [], "value": []})
    result = deduplicate_events(df)
    assert len(result) == 0
    assert list(result.columns) == ["event_id", "updated_at", "value"]


def test_all_null_identifiers():
    df = pd.DataFrame({
        "event_id": [None, None, None],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
        "value": ["a", "b", "c"]
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)


def test_single_row():
    df = pd.DataFrame({
        "event_id": [1],
        "updated_at": pd.to_datetime(["2023-01-01"]),
        "value": ["a"]
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)


def test_mix_of_valid_invalid_timestamps_and_nulls():
    df = pd.DataFrame({
        "event_id": [1, 1, 2, None, 2],
        "updated_at": ["not a date", "2023-01-02", "2023-01-01", "2023-01-01", "bad"],
        "value": ["a", "b", "c", "d", "e"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1, None, 2],
        "updated_at": ["2023-01-02", "2023-01-01", "2023-01-01"],
        "value": ["b", "d", "c"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_preserves_original_order():
    df = pd.DataFrame({
        "event_id": [1, 1, 1],
        "updated_at": pd.to_datetime(["2023-01-03", "2023-01-02", "2023-01-01"]),
        "value": ["a", "b", "c"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1],
        "updated_at": pd.to_datetime(["2023-01-03"]),
        "value": ["a"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_custom_column_names():
    df = pd.DataFrame({
        "id": [1, 1, 2],
        "ts": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01"]),
        "info": ["x", "y", "z"]
    })
    result = deduplicate_events(df, id_col="id", timestamp_col="ts")
    expected = pd.DataFrame({
        "id": [1, 2],
        "ts": pd.to_datetime(["2023-01-02", "2023-01-01"]),
        "info": ["y", "z"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_input_dataframe_not_mutated():
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02"]),
        "value": ["a", "b"]
    })
    original = df.copy()
    deduplicate_events(df)
    pd.testing.assert_frame_equal(df, original)