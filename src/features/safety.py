from __future__ import annotations

import numpy as np
import pandas as pd


def _haversine_vectorized(lat: float, lon: float, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    lat1 = np.radians(lat)
    lon1 = np.radians(lon)
    lat2 = np.radians(lats)
    lon2 = np.radians(lons)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def compute_crime_count_near_listings(
    listings_df: pd.DataFrame, crimes_df: pd.DataFrame, radius_km: float
) -> pd.Series:
    if crimes_df is None or crimes_df.empty:
        return pd.Series(0, index=listings_df.index)
    crime_lats = crimes_df["latitude"].to_numpy(dtype=float)
    crime_lons = crimes_df["longitude"].to_numpy(dtype=float)
    counts = []
    for lat, lon in zip(listings_df["latitude"], listings_df["longitude"]):
        dists = _haversine_vectorized(float(lat), float(lon), crime_lats, crime_lons)
        counts.append(int(np.sum(dists <= radius_km)))
    return pd.Series(counts, index=listings_df.index, dtype=int)

