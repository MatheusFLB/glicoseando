"""
Data processing module for NDVI time series data.

This module handles loading and processing NDVI data from JSON format
returned by the AgroAPI SATVeg endpoint.
"""

import json
from pathlib import Path
from typing import Optional

import pandas as pd


def load_ndvi_data(filepath: str | Path) -> pd.DataFrame:
    """
    Load NDVI time series data from JSON file.

    Parameters
    ----------
    filepath : str or Path
        Path to the JSON file containing NDVI data.
        Expected format: {"listaSerie": [...], "listaDatas": [...]}

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - 'date' (datetime): Observation date
        - 'ndvi' (float): NDVI value for that date

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the JSON structure is invalid.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate JSON structure
    if "listaSerie" not in data or "listaDatas" not in data:
        raise ValueError(
            "JSON must contain 'listaSerie' and 'listaDatas' keys."
        )

    series = data["listaSerie"]
    dates = data["listaDatas"]

    if len(series) != len(dates):
        raise ValueError(
            f"Mismatch in data length: "
            f"series={len(series)}, dates={len(dates)}"
        )

    # Create DataFrame
    df = pd.DataFrame({"date": dates, "ndvi": series})

    # Convert date strings to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Sort by date
    df = df.sort_values("date").reset_index(drop=True)

    return df


def clean_ndvi_data(
    df: pd.DataFrame, min_ndvi: float = -1.0, max_ndvi: float = 1.0
) -> pd.DataFrame:
    """
    Clean NDVI data by removing invalid values.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with 'ndvi' column.
    min_ndvi : float, default=-1.0
        Minimum valid NDVI value.
    max_ndvi : float, default=1.0
        Maximum valid NDVI value.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with invalid values removed.
    """
    df = df.copy()
    n_before = len(df)

    # Remove rows with NDVI outside valid range
    df = df[(df["ndvi"] >= min_ndvi) & (df["ndvi"] <= max_ndvi)]

    # Remove rows with NaN values
    df = df.dropna()

    n_after = len(df)
    if n_before > n_after:
        removed = n_before - n_after
        print(f"Removed {removed} invalid NDVI values.")

    return df.reset_index(drop=True)


def resample_to_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resample NDVI data to monthly averages.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with 'date' and 'ndvi' columns.

    Returns
    -------
    pd.DataFrame
        Resampled DataFrame with monthly aggregations.
    """
    df = df.copy()
    df.set_index("date", inplace=True)
    monthly = df["ndvi"].resample("MS").mean()
    return monthly.reset_index().rename(columns={"ndvi": "ndvi"})


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Generate summary statistics for NDVI data.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with 'date' and 'ndvi' columns.

    Returns
    -------
    dict
        Summary statistics including:
        - "n_observations": number of observations
        - "date_range": (start_date, end_date)
        - "mean_ndvi": mean value
        - "std_ndvi": standard deviation
        - "min_ndvi": minimum value
        - "max_ndvi": maximum value
    """
    return {
        "n_observations": len(df),
        "date_range": (df["date"].min(), df["date"].max()),
        "mean_ndvi": df["ndvi"].mean(),
        "std_ndvi": df["ndvi"].std(),
        "min_ndvi": df["ndvi"].min(),
        "max_ndvi": df["ndvi"].max(),
    }
