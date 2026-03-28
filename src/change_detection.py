"""
Change detection module for detecting land-use transitions.

This module identifies significant changes in NDVI patterns,
particularly for deforestation and agricultural intensification.
"""

from typing import List, Optional

import numpy as np
import pandas as pd

try:
    import ruptures as rpt
except ImportError:
    rpt = None


def detect_change_points(
    series: np.ndarray,
    n_breakpoints: int = 3,
    algo: str = "binseg",
    min_size: int = 50,
) -> List[int]:
    """
    Detect change points in NDVI time series using binary segmentation.

    Parameters
    ----------
    series : np.ndarray
        1D array of NDVI values.
    n_breakpoints : int, default=3
        Number of change points to detect.
    algo : str, default="binseg"
        Algorithm: "binseg" (binary segmentation) or "pelt" (Pruned Exact Linear Time).
    min_size : int, default=50
        Minimum segment size to avoid detecting noise.

    Returns
    -------
    List[int]
        Indices of detected change points (sorted).

    Raises
    ------
    ImportError
        If ruptures package is not installed.
    ValueError
        If series is too short.
    """
    if rpt is None:
        raise ImportError(
            "ruptures package is required. Install with: pip install ruptures"
        )

    if len(series) < min_size:
        raise ValueError(
            f"Series too short ({len(series)} points). "
            f"Minimum {min_size} required."
        )

    # Normalize series to [0, 1] for better change detection
    series_norm = (series - series.min()) / (series.max() - series.min() + 1e-8)

    # Choose algorithm
    if algo == "binseg":
        algo_obj = rpt.Binseg(model="l2", min_size=min_size, jump=1).fit(
            series_norm.reshape(-1, 1)
        )
    elif algo == "pelt":
        algo_obj = rpt.Pelt(model="l2", min_size=min_size, jump=1).fit(
            series_norm.reshape(-1, 1)
        )
    else:
        raise ValueError(f"Unknown algorithm: {algo}")

    # Predict breakpoints
    breakpoints = algo_obj.predict(n_bkps=n_breakpoints)

    # Remove the last breakpoint (always at end of series)
    if breakpoints[-1] == len(series):
        breakpoints = breakpoints[:-1]

    return sorted(breakpoints)


def estimate_deforestation_onset(
    df: pd.DataFrame, change_points: List[int]
) -> Optional[dict]:
    """
    Estimate when deforestation or major land-use change began.

    Analyzes the first significant change point to identify the onset
    of deforestation or land-use transition.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'date' and 'ndvi' columns (sorted by date).
    change_points : List[int]
        Indices of detected change points from detect_change_points().

    Returns
    -------
    dict or None
        If deforestation detected, returns:
        - "onset_date": approximate date of change onset
        - "onset_year": year of change
        - "magnitude": difference in NDVI before/after
        - "type": classification (pasture_to_crop, crop_to_pasture, etc.)
        Returns None if no clear deforestation signal.
    """
    if not change_points or len(change_points) == 0:
        return None

    # Analyze first change point
    idx = change_points[0]
    if idx < 20 or idx >= len(df) - 20:
        return None

    # Get NDVI before and after change
    before = df.iloc[max(0, idx - 50) : idx]["ndvi"].mean()
    after = df.iloc[idx : min(len(df), idx + 50)]["ndvi"].mean()

    magnitude = before - after

    # Classify the type of change
    if magnitude > 0.1:
        change_type = "high_ndvi_loss"  # Possible deforestation
    elif magnitude < -0.05:
        change_type = "ndvi_gain"  # Possible reforestation or intensification
    else:
        change_type = "moderate_shift"

    onset_date = df.iloc[idx]["date"]
    onset_year = int(onset_date.year)

    return {
        "onset_date": onset_date,
        "onset_year": onset_year,
        "magnitude": magnitude,
        "type": change_type,
        "change_point_index": idx,
    }


def calculate_intensity_score(
    df: pd.DataFrame, period_years: Optional[tuple] = None
) -> float:
    """
    Calculate agricultural intensification score (0–1).

    Score is based on:
    - Frequency of high NDVI values (> 0.8)
    - Consistency of peaks
    - Overall NDVI level

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'date' and 'ndvi' columns.
    period_years : tuple, optional
        (start_year, end_year) to analyze. If None, uses full range.

    Returns
    -------
    float
        Intensification score from 0 (low) to 1 (high).
    """
    df = df.copy()

    # Filter by period if specified
    if period_years:
        start_yr, end_yr = period_years
        df = df[
            (df["date"].dt.year >= start_yr)
            & (df["date"].dt.year <= end_yr)
        ]

    if len(df) == 0:
        return 0.0

    # Component 1: Frequency of high NDVI (>0.8)
    high_ndvi_freq = (df["ndvi"] > 0.8).sum() / len(df)

    # Component 2: Mean NDVI level (normalized to 0–1)
    mean_ndvi_norm = df["ndvi"].mean()

    # Component 3: NDVI consistency (inverse of coefficient of variation)
    cv = df["ndvi"].std() / (df["ndvi"].mean() + 1e-8)
    consistency = 1 / (1 + cv)

    # Weighted combination
    intensity = (
        0.4 * high_ndvi_freq
        + 0.4 * mean_ndvi_norm
        + 0.2 * consistency
    )

    return np.clip(intensity, 0, 1)


def segment_by_change_points(
    df: pd.DataFrame, change_points: List[int]
) -> List[pd.DataFrame]:
    """
    Segment the time series by change points.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'date' and 'ndvi' columns.
    change_points : List[int]
        Indices of detected change points.

    Returns
    -------
    List[pd.DataFrame]
        List of segments between change points.
    """
    segments = []
    indices = [0] + sorted(change_points) + [len(df)]

    for i in range(len(indices) - 1):
        segment = df.iloc[indices[i] : indices[i + 1]].copy()
        if len(segment) > 0:
            segments.append(segment)

    return segments


def classify_change_severity(magnitude: float, threshold: float = 0.15) -> str:
    """
    Classify the severity of NDVI change.

    Parameters
    ----------
    magnitude : float
        NDVI change magnitude (can be negative).
    threshold : float, default=0.15
        Threshold for "severe" classification.

    Returns
    -------
    str
        Classification: "severe", "moderate", "minor", "gain"
    """
    abs_magnitude = abs(magnitude)

    if magnitude > 0.05:
        return "gain"
    elif abs_magnitude < 0.05:
        return "minor"
    elif abs_magnitude < threshold:
        return "moderate"
    else:
        return "severe"
