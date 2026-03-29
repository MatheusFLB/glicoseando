"""
MÓDULO DE PROCESSAMENTO DE DADOS NDVI

Responsável por carregar, validar, limpar e processar dados de séries temporais
do NDVI obtidos do AgroAPI/SATVeg da Embrapa.

ESTRUTURA DOS DADOS:
Os dados de entrada (JSON) contêm:
- listaSerie: array com valores numéricos de NDVI
- listaDatas: array com datas correspondentes

OPERAÇÕES PRINCIPAIS:
1. Carregar dados do arquivo JSON
2. Validar integridade dos dados
3. Converter para DataFrame estruturado
4. Limpar valores inválidos
5. Agregar dados (ex: média mensal)
6. Gerar estatísticas descritivas
"""

import json
from pathlib import Path
from typing import Optional

import pandas as pd


# ==================== CARREGAMENTO DE DADOS ====================
def load_ndvi_data(filepath: str | Path) -> pd.DataFrame:
    """
    Carrega dados de série temporal NDVI de um arquivo JSON.

    Esta função é responsável pela leitura inicial dos dados obtidos da API SATVeg.
    Valida a estrutura do arquivo e converte os dados em um DataFrame estruturado
    e ordenado por data.

    Parameters
    ----------
    filepath : str or Path
        Caminho para o arquivo JSON contendo dados de NDVI.
        Formato esperado: {"listaSerie": [...], "listaDatas": [...]}
        - listaSerie: array de valores numéricos (0 a 1)
        - listaDatas: array de strings de datas

    Returns
    -------
    pd.DataFrame
        DataFrame estruturado com colunas:
        - 'date' (datetime): Data da observação
        - 'ndvi' (float): Valor de NDVI para aquela data

    Raises
    ------
    FileNotFoundError
        Se o arquivo não existe no caminho especificado.
    ValueError
        Se a estrutura JSON é inválida ou os arrays são incompatíveis.

    Example
    -------
    >>> df = load_ndvi_data("data/ndvi_timeseries.json")
    >>> print(df.head())
         date      ndvi
    0 2000-01-01  0.234
    1 2000-01-02  0.245
    """
    filepath = Path(filepath)

    # Valida se o arquivo existe
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Abre e carrega o arquivo JSON
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Valida a presença das chaves obrigatórias no JSON
    if "listaSerie" not in data or "listaDatas" not in data:
        raise ValueError(
            "JSON must contain 'listaSerie' and 'listaDatas' keys."
        )

    series = data["listaSerie"]  # Valores de NDVI
    dates = data["listaDatas"]   # Datas correspondentes

    # Valida se os dois arrays têm o mesmo tamanho
    if len(series) != len(dates):
        raise ValueError(
            f"Mismatch in data length: "
            f"series={len(series)}, dates={len(dates)}"
        )

    # Cria um DataFrame com os dados
    df = pd.DataFrame({"date": dates, "ndvi": series})

    # Converte strings de data para formato datetime
    df["date"] = pd.to_datetime(df["date"])

    # Ordena por data e reseta o índice
    df = df.sort_values("date").reset_index(drop=True)

    return df


# ==================== LIMPEZA DE DADOS ====================
def clean_ndvi_data(
    df: pd.DataFrame, min_ndvi: float = -1.0, max_ndvi: float = 1.0
) -> pd.DataFrame:
    """
    Limpa dados de NDVI removendo valores inválidos ou fora do intervalo esperado.

    NDVI deve estar sempre no intervalo [-1.0, 1.0]. Esta função remove:
    - Valores fora do intervalo válido
    - Valores NaN (nulos)

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada com coluna 'ndvi'.
    min_ndvi : float, default=-1.0
        Valor mínimo válido de NDVI.
    max_ndvi : float, default=1.0
        Valor máximo válido de NDVI.

    Returns
    -------
    pd.DataFrame
        DataFrame limpo com valores inválidos removidos.

    Example
    -------
    >>> df_clean = clean_ndvi_data(df)
    >>> print(f"Linhas originais: {len(df)}, Linhas limpas: {len(df_clean)}")
    """
    df = df.copy()
    n_before = len(df)

    # Remove linhas onde NDVI está fora do intervalo válido
    df = df[(df["ndvi"] >= min_ndvi) & (df["ndvi"] <= max_ndvi)]

    # Remove linhas com valores NaN (nulos)
    df = df.dropna()

    n_after = len(df)
    # Informa quantos valores foram removidos
    if n_before > n_after:
        removed = n_before - n_after
        print(f"Removed {removed} invalid NDVI values.")

    return df.reset_index(drop=True)


# ==================== AGREGAÇÃO DE DADOS ====================
def resample_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reamostra dados de NDVI para médias mensais.

    Útil para suavizar dados diários e visualizar tendências de longo prazo,
    reduzindo ruído e facilitando a detecção de padrões sazonais.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com colunas 'date' e 'ndvi'.

    Returns
    -------
    pd.DataFrame
        DataFrame reamostrado com médias mensais de NDVI.

    Example
    -------
    >>> df_monthly = resample_to_monthly(df)
    >>> print(df_monthly.head())
         date      ndvi
    0 2000-01-31  0.235
    1 2000-02-29  0.248
    """
    df = df.copy()
    df.set_index("date", inplace=True)
    # Calcula a média de NDVI por mês (começo do mês = MS)
    monthly = df["ndvi"].resample("MS").mean()
    return monthly.reset_index()


# ==================== ESTATÍSTICAS DESCRITIVAS ====================
def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Gera estatísticas descritivas da série temporal de NDVI.

    Calcula informações resumidas úteis para análise exploratória:
    - Número de observações
    - Intervalo de datas
    - Média, desvio padrão
    - Valores mínimo e máximo

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com colunas 'date' e 'ndvi'.

    Returns
    -------
    dict
        Dicionário contendo:
        - "n_observations": número de observações na série
        - "date_range": tupla (data_mínima, data_máxima)
        - "mean_ndvi": valor médio de NDVI
        - "std_ndvi": desvio padrão de NDVI
        - "min_ndvi": valor mínimo
        - "max_ndvi": valor máximo

    Example
    -------
    >>> stats = get_data_summary(df)
    >>> print(f"Observações: {stats['n_observations']}")
    >>> print(f"NDVI médio: {stats['mean_ndvi']:.3f}")
    """
    return {
        "n_observations": len(df),
        "date_range": (df["date"].min(), df["date"].max()),
        "mean_ndvi": df["ndvi"].mean(),
        "std_ndvi": df["ndvi"].std(),
        "min_ndvi": df["ndvi"].min(),
        "max_ndvi": df["ndvi"].max(),
    }
