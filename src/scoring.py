from typing import Tuple

import pandas as pd

from .utils import normalize_series


def compute_weighted_score(df: pd.DataFrame, weights: Tuple[float, float, float]) -> pd.Series:
    w_price, w_rating, w_distance = weights
    total = max(w_price + w_rating + w_distance, 1e-9)
    w_price, w_rating, w_distance = w_price / total, w_rating / total, w_distance / total

    price_s = normalize_series(df["price_num"], higher_is_better=False)
    rating_s = normalize_series(df["rating"], higher_is_better=True)
    dist_s = normalize_series(df["distance_km"], higher_is_better=False)

    return w_price * price_s + w_rating * rating_s + w_distance * dist_s

