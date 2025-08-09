from __future__ import annotations

import pandas as pd
import numpy as np


def read_listings(uploaded_df: pd.DataFrame | None) -> pd.DataFrame:
    if uploaded_df is not None:
        df = uploaded_df
    else:
        try:
            df = pd.read_csv("data/listings.csv")
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
        df["rating"] = df["review_scores_rating"].astype(float) / 20.0

    keep = ["id", "name", "latitude", "longitude", "price_num", "rating"]
    df = df[[c for c in keep if c in df.columns]].dropna(subset=["latitude", "longitude", "price_num", "rating"])
    return df.reset_index(drop=True)

