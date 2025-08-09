import pandas as pd
import pydeck as pdk
import streamlit as st

from src.utils import haversine_km, normalize_series
from src.data_loader import read_listings, read_crimes
from src.crime import compute_crime_count_near_listings
from src.scoring import compute_weighted_score

"""Streamlit app for DC Airbnb MVP using small helpers from `src/`."""

# ---------- UI ----------
st.set_page_config(page_title="DC Airbnb MVP", layout="wide")
st.title("Washington DC Airbnb — MVP Rental Filter & Ranking")
st.caption("Streamlit app for DC Airbnb MVP using small helpers from `src/`.")

# Data source: upload or use data/listings.csv or sample
uploaded_file = st.sidebar.file_uploader("Upload InsideAirbnb listings CSV (optional)", type=["csv"])
df = read_listings(pd.read_csv(uploaded_file) if uploaded_file else None)
crimes_df = read_crimes()

# Destination options (no APIs, keep simple)
presets = {
    "White House": (38.8977, -77.0365),
    "Union Station": (38.8970, -77.0064),
    "Capitol Building": (38.8899, -77.0091),
    "Custom": None,
}
dest_name = st.sidebar.selectbox("Destination", list(presets.keys()), index=0)

if presets[dest_name] is None:
    dest_lat = st.sidebar.number_input("Dest Latitude", value=38.8977, format="%.6f")
    dest_lon = st.sidebar.number_input("Dest Longitude", value=-77.0365, format="%.6f")
else:
    dest_lat, dest_lon = presets[dest_name]

# Compute distance km (haversine) as a simple travel-time proxy
df["distance_km"] = [
    haversine_km(lat, lon, dest_lat, dest_lon) for lat, lon in zip(df["latitude"], df["longitude"])
]

# Crime radius and counts (simple array approach)
radius_km = st.sidebar.slider("Crime radius (km)", min_value=0.2, max_value=2.0, value=0.5, step=0.1)
crime_counts = compute_crime_count_near_listings(df, crimes_df, radius_km)
df["crime_count"] = crime_counts

# Basic filters with permissive defaults
min_price, max_price = float(df["price_num"].min()), float(df["price_num"].max())
price_range = st.sidebar.slider(
    "Price range ($)",
    min_value=int(min_price),
    max_value=int(max_price),
    value=(int(min_price), int(max_price)),
)
min_rating = st.sidebar.slider("Minimum rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
max_crimes = st.sidebar.slider(
    "Max crimes in radius",
    min_value=int(df["crime_count"].min()),
    max_value=int(max(1, int(df["crime_count"].max()))),
    value=int(max(1, int(df["crime_count"].max()))),
    step=1,
)
max_distance = st.sidebar.slider(
    "Max distance (km)",
    min_value=0.0,
    max_value=float(df["distance_km"].max()),
    value=float(df["distance_km"].max()),
    step=0.5,
)

mask = (
    (df["price_num"].between(price_range[0], price_range[1]))
    & (df["rating"] >= min_rating)
    & (df["distance_km"] <= max_distance)
    & (df["crime_count"] <= max_crimes)
)
filtered = df.loc[mask].copy()

# Weights for ranking
st.sidebar.markdown("### Weights (sum normalized automatically)")
w_price = st.sidebar.slider("Weight - Price (lower better)", 0.0, 1.0, 0.4, 0.05)
w_rating = st.sidebar.slider("Weight - Rating (higher better)", 0.0, 1.0, 0.4, 0.05)
w_distance = st.sidebar.slider("Weight - Distance (lower better)", 0.0, 1.0, 0.2, 0.05)

st.caption(f"Loaded {len(df):,} listings; {int(crimes_df.shape[0]):,} crimes. After filters: {len(filtered):,} listings.")
if filtered.empty:
    st.warning("No listings match the selected filters. Try widening price range, lowering minimum rating, increasing max distance, or raising max crimes.")
    st.stop()

# Score + sort (with optional algorithm choices)
filtered["score"] = compute_weighted_score(filtered, (w_price, w_rating, w_distance))

algo = st.sidebar.selectbox(
    "Ranking algorithm",
    ["Pandas sort (default)", "Top-K via heap", "QuickSort", "HeapSort"],
    index=0,
)

if algo == "Pandas sort (default)":
    filtered = filtered.sort_values("score", ascending=False)
else:
    # Represent as list of (score, index) pairs
    pairs = [(float(s), int(i)) for i, s in zip(filtered.index, filtered["score"]) ]
    if algo == "Top-K via heap":
        from src.algorithms.heap_topk import top_k_by_score

        max_k = max(1, min(100, len(pairs)))
        k = st.sidebar.slider("Top-K", min_value=1, max_value=max_k, value=min(20, max_k))
        topk = top_k_by_score(pairs, k)
        idx = [i for _, i in topk]
        filtered = filtered.loc[idx].sort_values("score", ascending=False)
    elif algo == "QuickSort":
        from src.algorithms.sorting import quicksort

        sorted_pairs = quicksort(pairs)
        idx = [i for _, i in sorted_pairs]
        filtered = filtered.loc[idx]
    elif algo == "HeapSort":
        from src.algorithms.sorting import heap_sort

        sorted_pairs = heap_sort(pairs)
        idx = [i for _, i in sorted_pairs]
        filtered = filtered.loc[idx]

# Results table
st.subheader("Top Results")
st.dataframe(
    filtered[["id", "name", "price_num", "rating", "distance_km", "crime_count", "score"]].round({"price_num": 0, "rating": 2, "distance_km": 2, "score": 3}),
    use_container_width=True,
    hide_index=True,
)

# Map
st.subheader("Map")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered.assign(size=100, color=((1 - normalize_series(filtered["score"], True)) * 255)).rename(columns={"longitude": "lon"}),
    get_position=["lon", "latitude"],
    get_radius=80,
    get_fill_color=[255, "color", 0],
    pickable=True,
)
view_state = pdk.ViewState(latitude=float(filtered["latitude"].mean()), longitude=float(filtered["longitude"].mean()), zoom=11)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}\nScore: {score}"}))

# Download
st.download_button("Download CSV", data=filtered.to_csv(index=False), file_name="ranked_listings.csv", mime="text/csv")

