"""
NDVI analysis module for temporal pattern detection.

This module provides functions for analyzing NDVI time series data,
including peak detection and annual metrics extraction.
"""

from typing import List

import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def identify_peaks(
    series: np.ndarray, prominence: float = 0.08
) -> List[int]:
    """
    Identify vegetation peaks in NDVI series using prominence criteria.

    Peaks are detected using scipy's find_peaks with prominence threshold,
    representing local maximum NDVI values during growing seasons.

    Parameters
    ----------
    series : np.ndarray
        1D array of NDVI values.
    prominence : float, default=0.08
        Minimum peak prominence to be considered significant.

    Returns
    -------
    List[int]
        Indices of detected peaks in the series.
    """
    if len(series) < 5:
        return []

    peaks_idx, _ = find_peaks(series, prominence=prominence)
    return peaks_idx.tolist()


def extract_annual_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract annual NDVI statistics from daily time series.

    Groups NDVI observations by year and calculates mean, max, and min
    values for each year.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'date' (datetime) and 'ndvi' (float) columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: year, mean_ndvi, max_ndvi, min_ndvi.
    """
    df = df.copy()
    df["year"] = df["date"].dt.year

    annual_stats = df.groupby("year").agg(
        mean_ndvi=("ndvi", "mean"),
        max_ndvi=("ndvi", "max"),
        min_ndvi=("ndvi", "min"),
    ).reset_index()

    return annual_stats
