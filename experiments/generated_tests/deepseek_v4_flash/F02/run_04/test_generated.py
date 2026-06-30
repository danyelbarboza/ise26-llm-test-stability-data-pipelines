import pytest
import pandas as pd
from ise26.targets import deduplicate_events

def test_basic_deduplication():
    """Must keep most recent row per event_id when timestamps differ."""
    df = pd.DataFrame({
        "event_id": [1, 1, 2],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-01"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1, 2],
        "updated_at": ["2023-01-02", "2023-01-01"]
    }, index=[0, 1])
    pd.testing.assert_frame_equal(result, expected)


def test_null_ids_preserved():
    """Rows with null event_id are kept unchanged."""
    df = pd.DataFrame({
        "event_id": [None, None, 1, 1],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-02"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [None, None, 1],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-02"]
    }, index=[0, 1, 2])
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_timestamps_treated_as_older():
    """Invalid timestamps are older, valid timestamps dominate."""
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": ["invalid", "2023-01-01"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1],
        "updated_at": ["2023-01-01"]
    }, index=[0])
    pd.testing.assert_frame_equal(result, expected)


def test_timestamp_tie_keeps_last_row():
    """When timestamps tie, last row in original order is kept."""
    df = pd.DataFrame({
        "event_id": [1, 1, 1],
        "updated_at": ["2023-01-01", "2023-01-01", "2023-01-01"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1],
        "updated_at": ["2023-01-01"]
    }, index=[0])
    pd.testing.assert_frame_equal(result, expected)


def test_no_mutation_of_input():
    """Original DataFrame must not be modified."""
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": ["2023-01-01", "2023-01-02"]
    })
    df_copy = df.copy()
    deduplicate_events(df)
    pd.testing.assert_frame_equal(df, df_copy)


def test_custom_columns():
    """Works with non-default column names."""
    df = pd.DataFrame({
        "id": [1, 1, 2],
        "ts": ["2023-01-01", "2023-01-02", "2023-01-01"]
    })
    result = deduplicate_events(df, id_col="id", timestamp_col="ts")
    expected = pd.DataFrame({
        "id": [1, 2],
        "ts": ["2023-01-02", "2023-01-01"]
    }, index=[0, 1])
    pd.testing.assert_frame_equal(result, expected)


def test_empty_dataframe():
    """Empty input returns empty DataFrame with same columns."""
    df = pd.DataFrame(columns=["event_id", "updated_at"])
    result = deduplicate_events(df)
    expected = pd.DataFrame(columns=["event_id", "updated_at"])
    pd.testing.assert_frame_equal(result, expected)


def test_single_row():
    """Single row is kept unchanged."""
    df = pd.DataFrame({
        "event_id": [1],
        "updated_at": ["2023-01-01"]
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)


def test_mixed_scenario():
    """Combination of duplicates, nulls, and ties."""
    df = pd.DataFrame({
        "event_id": [1, None, 2, 1, 2, None],
        "updated_at": ["2023-01-01", "2023-01-01", "2023-01-02",
                       "2023-01-03", "2023-01-01", "2023-01-02"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1, None, 2, None],
        "updated_at": ["2023-01-03", "2023-01-01", "2023-01-02",
                       "2023-01-02"]
    }, index=[0,1,2,3])
    pd.testing.assert_frame_equal(result, expected)


def test_all_null_ids():
    """All rows have null event_id – none removed."""
    df = pd.DataFrame({
        "event_id": [None, None],
        "updated_at": ["2023-01-01", "2023-01-02"]
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)