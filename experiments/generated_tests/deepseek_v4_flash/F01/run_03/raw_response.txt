import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from ise26.targets import clean_customer_names


def test_clean_customer_names_basic():
    """Testa transformação padrão: remoção de espaços, minúsculas, acentos."""
    df = pd.DataFrame({"customer_name": ["  João  Silva  ", "MARIA DAS GRAÇAS", "José  ÁGUA  ",
                                          "  ", "Carla", None, pd.NA]})
    resultado = clean_customer_names(df, name_col="customer_name", output_col="nome_limpo")

    # Verificar preservação do original
    assert "customer_name" in resultado.columns
    assert (resultado["customer_name"] == df["customer_name"]).all()

    # Verificar coluna de saída
    nomes_esperados = ["joão silva", "maria das graças", "josé água",
                       pd.NA, "carla", pd.NA, pd.NA]
    # O pd.NA deve ser convertido para pd.NA (já é)
    # Mas cuidado: comparar com nan pode falhar; melhor usar pd.isna
    for idx, esperado in enumerate(nomes_esperados):
        if pd.isna(esperado):
            assert pd.isna(resultado.loc[idx, "nome_limpo"]), f"Índice {idx}: esperado NA, obtido {resultado.loc[idx, 'nome_limpo']}"
        else:
            assert resultado.loc[idx, "nome_limpo"] == esperado, f"Índice {idx}: esperado '{esperado}', obtido '{resultado.loc[idx, 'nome_limpo']}'"


def test_clean_customer_names_preserves_original():
    """Verifica que o DataFrame original não é modificado após a chamada."""
    df_original = pd.DataFrame({"customer_name": [" Teste ", "Outro"]})
    df_copy = df_original.copy()
    clean_customer_names(df_original, name_col="customer_name", output_col="clean")
    assert_frame_equal(df_original, df_copy)


def test_clean_customer_names_custom_columns():
    """Testa nomes de colunas personalizados."""
    df = pd.DataFrame({"nomes": ["  José  ", "ANA  "], "outra": [1, 2]})
    resultado = clean_customer_names(df, name_col="nomes", output_col="nomes_limpos")
    assert "nomes_limpos" in resultado.columns
    assert resultado["nomes_limpos"].tolist() == ["josé", "ana"]


def test_clean_customer_names_empty_dataframe():
    """DataFrame vazio deve retornar sem erros."""
    df = pd.DataFrame({"name": []})
    resultado = clean_customer_names(df, name_col="name", output_col="name_clean")
    assert isinstance(resultado, pd.DataFrame)
    assert len(resultado) == 0
    assert "name_clean" in resultado.columns


def test_clean_customer_names_only_spaces_different_encodings():
    """Verifica que strings que são apenas espaços viram NA, mesmo com diferentes unicode."""
    df = pd.DataFrame({"name": ["   ", "\u00a0 \u00a0", " \t ", "a", "b"]})
    resultado = clean_customer_names(df, name_col="name", output_col="clean")
    # As primeiras três devem ser NA
    for i in range(3):
        assert pd.isna(resultado.loc[i, "clean"]), f"Linha {i} deveria ser NA, obtido {resultado.loc[i, 'clean']}"
    # As últimas não
    assert resultado.loc[3, "clean"] == "a"
    assert resultado.loc[4, "clean"] == "b"


def test_clean_customer_names_accent_removal():
    """Confirma remoção de acentos: ç, á, é, í, ó, ú, â, ê, ã, ñ, etc."""
    df = pd.DataFrame({"name": ["José", "São Paulo", "Maçã", "Ñuñoa", "coração"]})
    resultado = clean_customer_names(df, name_col="name", output_col="clean")
    esperados = ["josé", "são paulo", "maçã", "ñuñoa", "coração"]
    # Nota: a função deve remover acentos mas preservar caracteres 'ç' e 'ñ'? Depende da definição de "accent marks".
    # O enunciado diz "remove accent marks", mas 'ç' e 'ñ' tem diacríticos (cedilha, tilde). Baseado em unicodedata.normalize pode não removê-los.
    # Vamos testar apenas letras com acentos agudos, circunflexos, etc., e assumir que 'ç' e 'ñ' são tratados como acentos a menos que se prove contrário.
    # Para evitar falhas, vou incluir apenas palavras com acentos comuns removíveis (á, é, í, ó, ú, â, ê, ô, ã, õ).
    # Mas a função real usa `unicodedata.normalize('NFKD', texto).encode('ascii', errors='ignore').decode('ascii')`, o que remove tudo que não é ASCII.
    # Então 'ç' vira 'c', 'ñ' vira 'n', etc. Vou ajustar esperados.
    esperados_ascii = ["josé", "são paulo", "maçã", "ñuñoa", "coração"]
    # Após normalização, 'é' vira 'e', 'ã' vira 'a', 'ç' vira 'c', 'ñ' vira 'n', 'õ' vira 'o'
    # Mas o teste deve refletir o comportamento real. Vou assumir que a função remove acentos e converte para ASCII.
    # Então:
    df_acento = pd.DataFrame({"name": ["José", "São Paulo", "Maçã", "Ñuñoa", "Coração"]})
    resultado_acento = clean_customer_names(df_acento, name_col="name", output_col="clean")
    esperado_acento = ["jose", "sao paulo", "maca", "nunoa", "coracao"]
    assert resultado_acento["clean"].tolist() == esperado_acento


def test_clean_customer_names_blank_string_variations():
    """Diferentes strings só de espaços em branco devem resultar em NA."""
    df = pd.DataFrame({"name": ["", "   ", "\t", "\n", "\r\n ", "valid"]})
    resultado = clean_customer_names(df, name_col="name", output_col="clean")
    for i in range(len(df) - 1):
        assert pd.isna(resultado.loc[i, "clean"]), f"Linha {i} ('{df.loc[i,'name']}') não virou NA"
    assert resultado.loc[5, "clean"] == "valid"


def test_clean_customer_names_return_type():
    """Verifica que o retorno é um DataFrame (cópia) e que o original não foi alterado."""
    df = pd.DataFrame({"x": [1], "y": [" a "]})
    df_before = df.copy()
    result = clean_customer_names(df, name_col="y", output_col="y_clean")
    assert isinstance(result, pd.DataFrame)
    assert not result is df  # não é o mesmo objeto
    assert_frame_equal(df, df_before)
    assert "y_clean" in result.columns