"""
MÓDULO DE ANÁLISE DE NDVI

Responsável por análises de séries temporais de NDVI, incluindo:
- Detecção de picos (máximos locais) de vegetação
- Extração de métricas anuais
- Identificação de padrões sazonais

INTERPRETAÇÃO DE PICOS:
Um pico de NDVI representa um momento em que a vegetação atinge seu máximo vigor
geralmente durante o crescimento máximo de uma cultura ou pastagem.

MÉTRICA IMPORTANTE: PROEMINÊNCIA (PROMINENCE)
A proeminência de um pico é a diferença entre o valor do pico e o maior vale adjacente
Picos com alta proeminência são mais significativos (diferem mais do baseline local)
"""

from typing import List

import numpy as np
import pandas as pd
from scipy.signal import find_peaks


# ==================== DETECÇÃO DE PICOS ====================
def identify_peaks(
    series: np.ndarray, prominence: float = 0.08
) -> List[int]:
    """
    Identifica picos de vegetação na série temporal de NDVI.

    Usa o método scipy.signal.find_peaks com critério de proeminência.
    Picos representam momentos de máximo vigor vegetativo durante a estação
    de crescimento, como desenvolvimento de culturas ou pico de pastagem.

    A PROEMINÊNCIA é o critério principal:
    - prominence=0.08 significa que o pico deve estar pelo menos 0.08 unidades
      acima do maior vale adjacente para ser considerado significativo
    - Valores maiores = menos picos (mais seletivo)
    - Valores menores = mais picos (mais sensível)

    Parameters
    ----------
    series : np.ndarray
        Array 1D com valores de NDVI.
    prominence : float, default=0.08
        Proeminência mínima para um pico ser considerado significativo.
        Intervalo típico: 0.05-0.15 para dados agrícolas.

    Returns
    -------
    List[int]
        Índices dos picos detectados na série.
        Se a série é muito curta (< 5 pontos), retorna lista vazia.

    Example
    -------
    >>> ndvi_values = np.array([0.3, 0.4, 0.6, 0.5, 0.3, 0.4, 0.7, 0.5])
    >>> peaks = identify_peaks(ndvi_values)
    >>> print(peaks)  # Índices dos picos
    [2, 6]
    """
    # Valida o tamanho mínimo da série para evitar erros
    if len(series) < 5:
        return []

    # Encontra picos usando a função find_peaks do scipy
    # prominence: limiar de proeminência do pico
    peaks_idx, _ = find_peaks(series, prominence=prominence)

    # Converte array numpy para lista Python
    return peaks_idx.tolist()


# ==================== EXTRAÇÃO DE MÉTRICAS ANUAIS ====================
def extract_annual_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai estatísticas anuais de NDVI a partir de série temporal diária.

    Para cada ano presente nos dados, calcula:
    - NDVI médio: valor típico de vigor vegetativo no ano
    - NDVI máximo: maior valor de NDVI (pico de vegetação)
    - NDVI mínimo: menor valor de NDVI (menor vigor vegetativo)

    Útil para:
    - Comparar produtividade entre anos
    - Detectar tendências de longo prazo
    - Identificar anos com estresse ou bom desempenho

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com colunas:
        - 'date' (datetime): data da observação
        - 'ndvi' (float): valor de NDVI

    Returns
    -------
    pd.DataFrame
        DataFrame agregado com colunas:
        - 'year': ano (int)
        - 'mean_ndvi': NDVI médio do ano (float)
        - 'max_ndvi': NDVI máximo do ano (float)
        - 'min_ndvi': NDVI mínimo do ano (float)

    Example
    -------
    >>> annual_stats = extract_annual_metrics(df)
    >>> print(annual_stats)
       year  mean_ndvi  max_ndvi  min_ndvi
    0  2000      0.612     0.845     0.234
    1  2001      0.618     0.852     0.241
    """
    df = df.copy()

    # Extrai o ano de cada data
    df["year"] = df["date"].dt.year

    # Agrupa por ano e calcula as estatísticas
    annual_stats = df.groupby("year").agg(
        mean_ndvi=("ndvi", "mean"),   # Média anual
        max_ndvi=("ndvi", "max"),     # Máximo anual (pico)
        min_ndvi=("ndvi", "min"),     # Mínimo anual (vale)
    ).reset_index()

    return annual_stats
