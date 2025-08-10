from __future__ import annotations

import os
import pandas as pd
import numpy as np


def read_listings(uploaded_df: pd.DataFrame | None) -> pd.DataFrame:
    if uploaded_df is not None:
        df = uploaded_df
    else:
        # Prefer real DC dataset if present
        dc_path = "data/dc-listings.csv"
        sample_path = "data/listings.csv"
        if os.path.exists(dc_path):
            df = pd.read_csv(dc_path, low_memory=False)
        else:
            try:
                df = pd.read_csv(sample_path)
            except Exception:
                # Tiny fallback sample
                df = pd.DataFrame(
                    [
                        {"id": 1, "name": "Dupont Studio", "latitude": 38.9097, "longitude": -77.0431, "price": "$120", "rating": 4.7},
                        {"id": 2, "name": "Capitol Hill Apt", "latitude": 38.8899, "longitude": -76.9940, "price": "$150", "rating": 4.8},
                        {"id": 3, "name": "Shaw Loft", "latitude": 38.9121, "longitude": -77.0219, "price": "$95", "rating": 4.5},
                        {"id": 4, "name": "Georgetown Flat", "latitude": 38.9096, "longitude": -77.0650, "price": "$210", "rating": 4.9},
                    ]
                )

    if "price" in df.columns:
        df["price_num"] = (
            df["price"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).astype(float)
        )
    else:
        df["price_num"] = np.nan

    if "rating" not in df.columns and "review_scores_rating" in df.columns:
        # Some InsideAirbnb dumps store 0–5, others 0–100. Detect automatically.
        rsr = pd.to_numeric(df["review_scores_rating"], errors="coerce")
        if rsr.max(skipna=True) and float(rsr.max()) > 5.0:
            df["rating"] = rsr / 20.0
        else:
            df["rating"] = rsr

    # added in a filter to remove all listings that have not been reviewed in the past year
    # assumed ot be bad listings host won't
    df = df[df['number_of_reviews_ltm'] >= 1]


    keep = ["id", "name", "latitude", "longitude", "price_num", "rating"]
    df = df[[c for c in keep if c in df.columns]].dropna(subset=["latitude", "longitude", "price_num", "rating"])

    # removed any places costing more than $10,000 (completely unrealistic)
    df = df[df['price_num'] <= 10000]

    return df.reset_index(drop=True)


def read_crimes(path: str = "data/dc-crimes.csv") -> pd.DataFrame:
    """Load crimes with required columns (latitude, longitude). Returns empty DataFrame if not present."""
    if not os.path.exists(path):
        return pd.DataFrame(columns=["latitude", "longitude"]).astype(float)
    df = pd.read_csv(path, low_memory=False)
    # Columns are LATITUDE, LONGITUDE in the sample
    lat_col = None
    lon_col = None
    for c in df.columns:
        lc = c.lower()
        if lc == "latitude":
            lat_col = c
        if lc == "longitude":
            lon_col = c
    if lat_col is None or lon_col is None:
        return pd.DataFrame(columns=["latitude", "longitude"]).astype(float)
    out = df[[lat_col, lon_col]].rename(columns={lat_col: "latitude", lon_col: "longitude"})
    out = out.dropna(subset=["latitude", "longitude"]).astype({"latitude": float, "longitude": float})
    return out.reset_index(drop=True)

