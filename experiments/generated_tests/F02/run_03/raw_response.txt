import pandas as pd
import pytest
from ise26.targets import deduplicate_events


def test_empty_dataframe():
    """DataFrame vazio deve retornar DataFrame vazio."""
    df = pd.DataFrame()
    result = deduplicate_events(df)
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_single_row():
    """DataFrame com uma única linha deve retornar a mesma linha."""
    df = pd.DataFrame({
        "event_id": ["A"],
        "updated_at": [pd.Timestamp("2023-01-01")],
        "value": [1]
    })
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)


def test_no_duplicates():
    """Sem duplicatas, deve retornar o mesmo DataFrame na ordem original."""
    df = pd.DataFrame({
        "event_id": ["A", "B", "C"],
        "updated_at": [
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-02"),
            pd.Timestamp("2023-01-03")
        ],
        "value": [10, 20, 30]
    })
    result = deduplicate_events(df)
    expected = df.copy()
    pd.testing.assert_frame_equal(result, expected)


def test_simple_duplicate_keep_most_recent():
    """Duplicata com timestamps diferentes: deve manter o mais recente."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": [
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-02")
        ],
        "value": [1, 2]
    })
    result = deduplicate_events(df)
    expected = df.iloc[[1]].reset_index(drop=True)  # mantém o segundo (mais recente)
    pd.testing.assert_frame_equal(result, expected)


def test_duplicate_invalid_timestamp_kept_as_older():
    """Timestamp inválido (nulo, string não reconhecida) é tratado como mais antigo."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["invalid_date", "2023-01-01"],
        "value": [1, 2]
    })
    result = deduplicate_events(df)
    expected = df.iloc[[1]].reset_index(drop=True)  # o válido é mais recente
    pd.testing.assert_frame_equal(result, expected)


def test_duplicate_both_invalid_timestamps_keep_last():
    """Ambos timestamps inválidos: mantém o último na ordem original."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["invalid1", "invalid2"],
        "value": [1, 2]
    })
    result = deduplicate_events(df)
    expected = df.iloc[[1]].reset_index(drop=True)  # último da ordem
    pd.testing.assert_frame_equal(result, expected)


def test_null_id_preserved():
    """Linhas com id nulo são preservadas (não são deduplicadas)."""
    df = pd.DataFrame({
        "event_id": [None, None],
        "updated_at": [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02")],
        "value": [1, 2]
    })
    result = deduplicate_events(df)
    expected = df.reset_index(drop=True)  # ambas as linhas devem estar presentes
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_null_and_non_null_ids():
    """Mistura de ids nulos e não nulos: apenas os não nulos são deduplicados."""
    df = pd.DataFrame({
        "event_id": ["A", None, "A", None],
        "updated_at": [
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-02"),
            pd.Timestamp("2023-01-03"),  # mais recente para A
            pd.Timestamp("2023-01-04")
        ],
        "value": [1, 2, 3, 4]
    })
    result = deduplicate_events(df)
    # ordem original: índice 0 (A, 2023-01-01), 1 (None), 2 (A, 2023-01-03), 3 (None)
    # Após dedup: para id A, mantém índice 2 (mais recente); nulos mantidos.
    # Ordem final deve ser: índice 1 (None), 2 (A, ), 3 (None)
    expected = df.iloc[[1, 2, 3]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_timestamp_tie_keep_last_in_order():
    """Timestamps iguais: mantém a última linha na ordem original."""
    df = pd.DataFrame({
        "event_id": ["A", "A", "A"],
        "updated_at": [
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-01")
        ],
        "value": [1, 2, 3]
    })
    result = deduplicate_events(df)
    expected = df.iloc[[2]].reset_index(drop=True)  # último da ordem
    pd.testing.assert_frame_equal(result, expected)


def test_preserves_original_order_for_unique_ids():
    """Ordem original mantida para ids únicos."""
    df = pd.DataFrame({
        "event_id": ["B", "A", "C"],
        "updated_at": [
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-01"),
            pd.Timestamp("2023-01-01")
        ],
        "value": [1, 2, 3]
    })
    result = deduplicate_events(df)
    expected = df.reset_index(drop=True)  # mesma ordem
    pd.testing.assert_frame_equal(result, expected)


def test_custom_columns():
    """Funciona com nomes de colunas diferentes."""
    df = pd.DataFrame({
        "id": [1, 1, 2],
        "ts": ["2023-01-02", "2023-01-01", "2023-01-01"],
        "info": ["a", "b", "c"]
    })
    result = deduplicate_events(df, id_col="id", timestamp_col="ts")
    # Para id=1, mantém a mais recente (2023-01-02), id=2 única
    expected = df.iloc[[0, 2]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_input_not_mutated():
    """O DataFrame de entrada não deve ser modificado."""
    df = pd.DataFrame({
        "event_id": ["A", "A"],
        "updated_at": ["2023-01-01", "2023-01-02"],
        "value": [1, 2]
    })
    original = df.copy()
    _ = deduplicate_events(df)
    pd.testing.assert_frame_equal(df, original)


def test_multiple_duplicates_and_ids():
    """Cenário complexo com vários ids e duplicatas."""
    df = pd.DataFrame({
        "event_id": ["X", "Y", "X", "Y", "Z", None],
        "updated_at": [
            "2023-01-01",
            "2023-01-02",
            "2023-01-03",  # X mais recente
            "2023-01-01",  # Y mais antigo
            "2023-01-01",  # Z único
            "2023-01-01"   # nulo
        ],
        "value": [10, 20, 30, 40, 50, 60]
    })
    result = deduplicate_events(df)
    # X: índice 2 (2023-01-03), Y: índice 1 (2023-01-02) – mais recente para Y? Verificar:
    # Y tem índices 1 (2023-01-02) e 3 (2023-01-01). Mais recente: 2023-01-02 => índice 1.
    # Z: índice 4, nulo: índice 5.
    # Ordem original: índices 0(X ant), 1(Y rec), 2(X rec), 3(Y ant), 4(Z), 5(nulo)
    # Após dedup: mantém índices 1,2,4,5 na ordem original => valores [20,30,50,60]
    expected = pd.DataFrame({
        "event_id": ["Y", "X", "Z", None],
        "updated_at": ["2023-01-02", "2023-01-03", "2023-01-01", "2023-01-01"],
        "value": [20, 30, 50, 60]
    })
    pd.testing.assert_frame_equal(result, expected)


def test_all_null_ids():
    """Todos ids nulos: nenhuma linha é removida."""
    df = pd.DataFrame({
        "event_id": [None, None, None],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "value": [1, 2, 3]
    })
    result = deduplicate_events(df)
    expected = df.reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)


def test_mixed_types_and_nans():
    """ids com NaN e None são tratados como nulos e preservados."""
    df = pd.DataFrame({
        "event_id": [float("nan"), "A", None, "A"],
        "updated_at": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
        "value": [1, 2, 3, 4]
    })
    result = deduplicate_events(df)
    # Para id A, mantém índice 3 (mais recente); índices 0 e 2 (nulos) são preservados
    # ordem original: 0,2,3
    expected = df.iloc[[0, 2, 3]].reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected)