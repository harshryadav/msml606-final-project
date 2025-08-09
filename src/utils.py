import math
from typing import Tuple

import numpy as np
import pandas as pd


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def normalize_series(x: pd.Series, higher_is_better: bool) -> pd.Series:
    if x.nunique() <= 1:
        return pd.Series(0.5, index=x.index)
    x_min, x_max = float(x.min()), float(x.max())
    scaled = (x - x_min) / (x_max - x_min)
    return scaled if higher_is_better else (1.0 - scaled)

