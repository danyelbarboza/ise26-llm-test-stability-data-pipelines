import pandas as pd
import pytest
from ise26.targets import deduplicate_events


def test_no_duplicates():
    df = pd.DataFrame({
        "event_id": [1, 2, 3],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "value": ["a", "b", "c"]
    })
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)


def test_duplicates_keep_most_recent():
    df = pd.DataFrame({
        "event_id": [1, 1, 2],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "value": ["a", "b", "c"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1, 2],
        "updated_at": ["2023-01-02", "2023-01-03"],
        "value": ["b", "c"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_duplicates_tie_keeps_last():
    df = pd.DataFrame({
        "event_id": [1, 1, 1],
        "updated_at": ["2023-01-01", "2023-01-01", "2023-01-01"],
        "value": ["x", "y", "z"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1],
        "updated_at": ["2023-01-01"],
        "value": ["z"]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_null_ids_preserved():
    df = pd.DataFrame({
        "event_id": [None, None, 1, 1],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-02"],
        "value": ["a", "b", "c", "d"]
    })
    result = deduplicate_events(df)
    # null rows kept (both), non-null id1 keeps most recent (value d)
    expected = pd.DataFrame({
        "event_id": [None, None, 1],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-02"],
        "value": ["a", "b", "d"]
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_ids_and_duplicates():
    df = pd.DataFrame({
        "event_id": [1, 2, 1, None, 2],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-01"],
        "value": ["a", "b", "c", "d", "e"]
    })
    result = deduplicate_events(df)
    # id1: keep row with value c (most recent)
    # id2: keep row with value b (most recent 2023-01-02 vs 2023-01-01)
    # None: keep both null rows? There are two null rows but they are not duplicates because id is null, both preserved.
    expected = pd.DataFrame({
        "event_id": [1, 2, None],
        "updated_at": ["2023-01-03", "2023-01-02", "2023-01-04"],
        "value": ["c", "b", "d"]
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_timestamps_treated_as_old():
    df = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": ["invalid", "2023-01-02"],
        "value": ["a", "b"]
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [1],
        "updated_at": ["2023-01-02"],
        "value": ["b"]
    })
    pd.testing.assert_frame_equal(result, expected)

    # both invalid
    df2 = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": ["bad", "also_bad"],
        "value": ["x", "y"]
    })
    result2 = deduplicate_events(df2)
    expected2 = pd.DataFrame({
        "event_id": [1],
        "updated_at": ["also_bad"],
        "value": ["y"]
    })
    pd.testing.assert_frame_equal(result2, expected2)


def test_input_not_mutated():
    original = pd.DataFrame({
        "event_id": [1, 1],
        "updated_at": ["2023-01-01", "2023-01-02"],
        "value": ["a", "b"]
    })
    df_copy = original.copy()
    result = deduplicate_events(original)
    pd.testing.assert_frame_equal(original, df_copy)


def test_empty_dataframe():
    df = pd.DataFrame({"event_id": pd.Series(dtype=int), "updated_at": pd.Series(dtype=str)})
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)


def test_single_row():
    df = pd.DataFrame({
        "event_id": [42],
        "updated_at": ["2023-05-01"],
        "value": ["single"]
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)


def test_preserves_original_order():
    # Duplicates with same timestamp, ensure last row kept and order relative to non-duplicates
    df = pd.DataFrame({
        "event_id": [1, 2, 1, 3],
        "updated_at": ["2023-01-01", "2023-01-01", "2023-01-01", "2023-01-01"],
        "value": ["a", "b", "c", "d"]
    })
    result = deduplicate_events(df)
    # keep last row per id: id1 keep row3 (value c), id2 keep row2 (value b), id3 keep row4 (value d)
    expected = pd.DataFrame({
        "event_id": [1, 2, 3],
        "updated_at": ["2023-01-01", "2023-01-01", "2023-01-01"],
        "value": ["c", "b", "d"]
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_custom_column_names():
    df = pd.DataFrame({
        "my_id": [10, 10, 20],
        "my_ts": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "info": ["a", "b", "c"]
    })
    result = deduplicate_events(df, id_col="my_id", timestamp_col="my_ts")
    expected = pd.DataFrame({
        "my_id": [10, 20],
        "my_ts": ["2023-01-02", "2023-01-03"],
        "info": ["b", "c"]
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_multiple_duplicates_complex():
    # Multiple ids, some with multiple duplicates, ensure only one kept per id
    df = pd.DataFrame({
        "event_id": [1, 2, 1, 2, 3, 1],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-01", "2023-01-04", "2023-01-02"],
        "value": ["a", "b", "c", "d", "e", "f"]
    })
    result = deduplicate_events(df)
    # id1: timestamps: 2023-01-01, 2023-01-03, 2023-01-02 -> most recent 2023-01-03 (value c)
    # id2: timestamps: 2023-01-02, 2023-01-01 -> most recent 2023-01-02 (value b)
    # id3: unique -> keep
    expected = pd.DataFrame({
        "event_id": [1, 2, 3],
        "updated_at": ["2023-01-03", "2023-01-02", "2023-01-04"],
        "value": ["c", "b", "e"]
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_all_nulls_preserved():
    df = pd.DataFrame({
        "event_id": [None, None, None],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "value": ["a", "b", "c"]
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df.reset_index(drop=True))  # all null rows preserved