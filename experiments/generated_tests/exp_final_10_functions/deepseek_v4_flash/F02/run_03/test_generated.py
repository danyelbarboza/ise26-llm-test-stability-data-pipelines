import pandas as pd
import numpy as np
from ise26.targets import deduplicate_events


def test_basic_deduplication():
    """Keep the most recent row for a given event_id."""
    df = pd.DataFrame({
        "event_id": ["A", "A", "B"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01"]),
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A", "B"],
        "updated_at": pd.to_datetime(["2023-01-02", "2023-01-01"]),
    }, index=[0, 2])
    pd.testing.assert_frame_equal(result, expected.reset_index(drop=True))


def test_ties_keep_last_row():
    """When timestamps tie, keep the last row in original order."""
    df = pd.DataFrame({
        "event_id": ["X", "X", "Y"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-01", "2023-01-02"]),
    })
    result = deduplicate_events(df)
    # For X: rows 0 and 1 have same timestamp, keep row 1 (last)
    expected = pd.DataFrame({
        "event_id": ["X", "Y"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02"]),
    }, index=[1, 2])
    pd.testing.assert_frame_equal(result, expected.reset_index(drop=True))


def test_preserve_null_identifiers():
    """Rows with null event_id are all preserved."""
    df = pd.DataFrame({
        "event_id": [None, None, "A"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01"]),
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": [None, None, "A"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-01"]),
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_timestamps_treated_as_older():
    """Invalid timestamps are older than valid ones, so valid timestamp row is kept."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["invalid", "2023-01-01"],  # first invalid, second valid
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": ["2023-01-01"],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_invalid_timestamp_makes_row_older_even_if_later_in_order():
    """If invalid timestamp appears later, it is older and should be dropped."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["2023-01-01", "invalid"],  # later row invalid
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": ["2023-01-01"],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_mix_null_and_nonnull():
    """Both null ids (all kept) and non-null ids (deduplicated) work together."""
    df = pd.DataFrame({
        "event_id": [None, "B", None, "B"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-01"]),
    })
    result = deduplicate_events(df)
    # Null rows kept, B duplicates keep most recent (2023-01-02 at row 1)
    expected = pd.DataFrame({
        "event_id": [None, "B", None],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
    })
    pd.testing.assert_frame_equal(result, expected)


def test_no_mutation_of_input():
    """The input DataFrame should not be modified."""
    original = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-02"]),
    })
    df_copy = original.copy()
    deduplicate_events(original)
    pd.testing.assert_frame_equal(original, df_copy)


def test_custom_column_names():
    """Function should work with custom id_col and timestamp_col."""
    df = pd.DataFrame({
        "my_id": ["A", "A", "B"],
        "my_ts": ["2023-01-02", "2023-01-01", "2023-01-01"],
    })
    result = deduplicate_events(df, id_col="my_id", timestamp_col="my_ts")
    expected = pd.DataFrame({
        "my_id": ["A", "B"],
        "my_ts": ["2023-01-02", "2023-01-01"],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_empty_dataframe():
    """Empty DataFrame returns empty DataFrame."""
    df = pd.DataFrame({"event_id": [], "updated_at": pd.to_datetime([])})
    result = deduplicate_events(df)
    expected = pd.DataFrame({"event_id": [], "updated_at": pd.to_datetime([])})
    pd.testing.assert_frame_equal(result, expected)


def test_single_row():
    """Single row is preserved unchanged."""
    df = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": pd.to_datetime(["2023-01-01"]),
    })
    result = deduplicate_events(df)
    pd.testing.assert_frame_equal(result, df)


def test_multiple_ids_with_valid_timestamps():
    """Multiple ids, each with several records, keeps most recent per id."""
    df = pd.DataFrame({
        "event_id": ["A", "A", "A", "B", "B"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-03", "2023-01-02", "2023-01-01", "2023-01-02"]),
    })
    result = deduplicate_events(df)
    expected = pd.DataFrame({
        "event_id": ["A", "B"],
        "updated_at": pd.to_datetime(["2023-01-03", "2023-01-02"]),
    })
    pd.testing.assert_frame_equal(result, expected)


def test_null_ids_are_not_grouped_with_nonnull():
    """Null id row is not considered duplicate of any non-null id, so both kept."""
    df = pd.DataFrame({
        "event_id": [None, "A"],
        "updated_at": pd.to_datetime(["2023-01-01", "2023-01-01"]),
    })
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)