"""
NDVI temporal analysis module.

This module performs time series analysis on NDVI data to extract
temporal patterns, seasonal cycles, and land-use classification.
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
from scipy import signal


def smooth_series(
    series: pd.Series, window: int = 32, method: str = "rolling"
) -> pd.Series:
    """
    Smooth a time series using a rolling window average.

    Parameters
    ----------
    series : pd.Series
        Input time series (typically NDVI values).
    window : int, default=32
        Size of the rolling window (~16 months for 8–16 day observations).
    method : str, default="rolling"
        Smoothing method: "rolling" or "savgol" (Savitzky-Golay).

    Returns
    -------
    pd.Series
        Smoothed time series.
    """
    if method == "rolling":
        return series.rolling(window=window, center=True, min_periods=1).mean()

    elif method == "savgol":
        # Savitzky-Golay filter requires odd window
        if window % 2 == 0:
            window += 1
        return pd.Series(
            signal.savgol_filter(series, window, polyorder=2, mode="nearest"),
            index=series.index,
        )

    else:
        raise ValueError(f"Unknown smoothing method: {method}")


def identify_peaks(
    series: pd.Series, prominence: float = 0.1, min_height: float = 0.5
) -> np.ndarray:
    """
    Identify peaks in NDVI time series.

    Peaks represent periods of maximum vegetation (crop peaks or wet season).

    Parameters
    ----------
    series : pd.Series
        Input time series with NDVI values.
    prominence : float, default=0.1
        Minimum peak prominence (relative height above surroundings).
    min_height : float, default=0.5
        Minimum NDVI value to be considered a peak.

    Returns
    -------
    np.ndarray
        Array of indices corresponding to peaks.
    """
    peaks, _ = signal.find_peaks(
        series, prominence=prominence, height=min_height
    )
    return peaks


def extract_annual_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract annual NDVI statistics.

    Groups the time series by year and computes mean, max, min, and amplitude
    for each year.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'date' and 'ndvi' columns.

    Returns
    -------
    pd.DataFrame
        Annual metrics with columns:
        - "year": year
        - "mean_ndvi": mean NDVI for the year
        - "max_ndvi": maximum NDVI for the year
        - "min_ndvi": minimum NDVI for the year
        - "amplitude": max - min
    """
    df = df.copy()
    df["year"] = df["date"].dt.year

    annual = (
        df.groupby("year")["ndvi"]
        .agg(
            mean_ndvi=("mean"),
            max_ndvi=("max"),
            min_ndvi=("min"),
        )
        .reset_index()
    )

    annual["amplitude"] = annual["max_ndvi"] - annual["min_ndvi"]

    return annual


def detect_seasonal_cycles(df: pd.DataFrame, year_range: Optional[Tuple[int, int]] = None) -> dict:
    """
    Detect and analyze seasonal cycles in NDVI time series.

    Estimates the number of peaks (cycles) per year and their characteristics.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'date' and 'ndvi' columns.
    year_range : Tuple[int, int], optional
        (start_year, end_year) to analyze. If None, uses full range.

    Returns
    -------
    dict
        Analysis results containing:
        - "cycles_per_year": average number of cycles per year
        - "cycle_duration_days": average duration of one cycle
        - "crop_type_inferred": classification (single_crop, double_crop, pasture, etc.)
    """
    df = df.copy()

    # Filter by year if specified
    if year_range:
        start_yr, end_yr = year_range
        df = df[(df["date"].dt.year >= start_yr) & (df["date"].dt.year <= end_yr)]

    # Identify peaks
    peaks = identify_peaks(df["ndvi"], prominence=0.08)

    if len(peaks) == 0:
        return {
            "cycles_per_year": 0,
            "cycle_duration_days": 0,
            "crop_type_inferred": "unknown",
        }

    # Calculate average days between peaks
    peak_dates = df.iloc[peaks]["date"].values
    if len(peak_dates) > 1:
        days_between = np.diff(peak_dates).astype("timedelta64[D]").astype(int)
        avg_cycle_days = days_between.mean()
    else:
        avg_cycle_days = 365  # Single peak suggests annual cycle

    # Estimate cycles per year
    years = df["date"].dt.year.max() - df["date"].dt.year.min() + 1
    cycles_per_year = len(peaks) / max(years, 1)

    # Infer crop type based on cycles per year
    if cycles_per_year < 0.5:
        crop_type = "pasture"
    elif 0.5 <= cycles_per_year < 1.5:
        crop_type = "single_crop"
    elif 1.5 <= cycles_per_year < 2.5:
        crop_type = "double_crop"
    else:
        crop_type = "perennial"

    return {
        "cycles_per_year": cycles_per_year,
        "cycle_duration_days": avg_cycle_days,
        "crop_type_inferred": crop_type,
    }


def classify_periods(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify the time series into three temporal periods.

    Periods:
    - 2000–2002: Initial transition
    - 2003–2010: Established agriculture
    - 2010–2026: Intensive agriculture

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'date' and 'ndvi' columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with additional 'period' column categorizing each observation.
    """
    df = df.copy()
    df["year"] = df["date"].dt.year

    def assign_period(year: int) -> str:
        if year <= 2002:
            return "2000–2002: Transition"
        elif year <= 2010:
            return "2003–2010: Established"
        else:
            return "2010–2026: Intensive"

    df["period"] = df["year"].apply(assign_period)
    return df.drop("year", axis=1)


def calculate_annual_change_rate(annual_df: pd.DataFrame) -> float:
    """
    Calculate the year-over-year change rate in mean NDVI.

    Parameters
    ----------
    annual_df : pd.DataFrame
        Annual metrics DataFrame from extract_annual_metrics().

    Returns
    -------
    float
        Average annual change rate in NDVI (can be negative).
    """
    if len(annual_df) < 2:
        return 0.0

    annual_df = annual_df.sort_values("year")
    changes = annual_df["mean_ndvi"].diff().dropna()

    return changes.mean()


def get_period_statistics(df: pd.DataFrame) -> dict:
    """
    Calculate statistics for each temporal period.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'date' and 'ndvi' columns.

    Returns
    -------
    dict
        Period-wise statistics with mean, max, min NDVI.
    """
    df = df.copy()
    df = classify_periods(df)

    stats = {}
    for period in df["period"].unique():
        period_data = df[df["period"] == period]["ndvi"]
        stats[period] = {
            "mean": period_data.mean(),
            "max": period_data.max(),
            "min": period_data.min(),
            "std": period_data.std(),
        }

    return stats
