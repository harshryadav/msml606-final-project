import pandas as pd
import pydeck as pdk
import streamlit as st

from src.utils import haversine_km, normalize_series
from src.data.loader import read_listings, read_crimes
from src.features.safety import compute_crime_count_near_listings
from src.scoring import compute_weighted_score


# Streamlit UI configurations
st.set_page_config(page_title="DC Airbnb", layout="wide")
st.title("Washington DC Airbnb — Rental Filter & Ranking")
st.caption("Streamlit application for DC Airbnb Rental Filter & Ranking.")

# load in dataset
try :
    df = read_listings(pd.read_csv("./data/dc-listings.csv"))
    crimes_df = read_crimes("./data/dc-crimes.csv")
except FileNotFoundError:
    st.error("Data files not found. Please ensure 'data/listings.csv' and 'data/crimes.csv' exist.")
    st.stop()

# common DC destination options
presets = {
    "White House": (38.8977, -77.0365),
    "U.S. Capitol Building": (38.8899, -77.0091),
    "Union Station": (38.8970, -77.0064),
    "Washington Monument": (38.8895, -77.0353),
    "Lincoln Memorial": (38.8893, -77.0502),
    "Jefferson Memorial": (38.8814, -77.0365),
    "Capitol One Arena": (38.8981, -77.0209),
    "Smithsonian National Air and Space Museum": (38.8882, -77.0199),
    "Smithsonian National Museum of Natural History": (38.8913, -77.0261),
    "Smithsonian National Museum of American History": (38.8913, -77.0300),
    "Smithsonian National Gallery of Art": (38.8913, -77.0199),
    "Smithsonian National Museum of African American History and Culture": (38.8910, -77.0325),
    "Library of Congress": (38.8887, -77.0047),
    "Supreme Court of the United States": (38.8906, -77.0044),
    "FBI Headquarters": (38.8954, -77.0260),
    "Custom": None,
}

# TODO: add the metro stations to the presets
presets_metro_dc = {
    "Metro Center": (38.8983, -77.0281),
    "L'Enfant Plaza": (38.8848, -77.0210),
    "Smithsonian": (38.8887, -77.0281),
    "Gallery Place–Chinatown": (38.8974, -77.0219),
    "Dupont Circle": (38.9096, -77.0434),
    "U Street": (38.9151, -77.0219),
    "Union Station": (38.8970, -77.0064),
    "Woodley Park–Zoo/Adams Morgan": (38.9249, -77.0528),
    "Columbia Heights": (38.9283, -77.0281),
    "Judiciary Square": (38.9004, -77.0220),
    "Farragut North": (38.9031, -77.0397),
    "Farragut West": (38.9031, -77.0392),
    "Federal Triangle": (38.8940, -77.0295),
    "Shaw–Howard U": (38.9155, -77.0210),
    "Archives–Navy Memorial–Penn Quarter": (38.8920, -77.0247),
    "Mount Vernon Square": (38.9052, -77.0235),
    "NoMa–Gallaudet U": (38.9082, -77.0039),
    "Rhode Island Ave–Brentwood": (38.9213, -76.9951),
    "Fort Totten": (38.9484, -77.0038),
    "Takoma": (38.9754, -77.0177),
    "Cleveland Park": (38.9341, -77.0636),
    "Tenleytown–AU": (38.9413, -77.0849),
    "Friendship Heights": (38.9609, -77.0849),
    "Van Ness–UDC": (38.9338, -77.0741),
    "Foggy Bottom–GWU": (38.9007, -77.0507),
    "McPherson Square": (38.9019, -77.0370),
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
# Default Value set to 0.4 to reflect research
# https://crim.sas.upenn.edu/sites/default/files/Ridgeway_Effect%20of%20Emergency%20Shelters-v5_1.2.2018.pdf
radius_km = st.sidebar.slider("Crime radius (km)", min_value=0.2, max_value=2.0, value=0.4, step=0.1)
crime_counts = compute_crime_count_near_listings(df, crimes_df, radius_km)
df["crime_count"] = crime_counts

# Basic filters with permissive defaults
min_price, max_price = float(df["price_num"].min()), float(df["price_num"].max())
average_price = float(df["price_num"].mean())
price_range = st.sidebar.slider(
    "Price range ($)",
    min_value=int(min_price),
    max_value=int(max_price),
    value=(int(min_price), int(average_price)+100),
)

# minimum rating and nights
min_rating = st.sidebar.slider("Minimum rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
min_nights, max_nights = int(df["minimum_nights"].min()), int(df["minimum_nights"].max())
nights = st.sidebar.slider("Number of nights", min_value=min_nights, max_value=max_nights, value=1, step=1)

# these set the ranges for the filters
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

# get the weighted score for each listing
st.sidebar.markdown("### Weights (sum normalized automatically)")
w_price = st.sidebar.slider("Weight - Price (lower better)", 0.0, 1.0, 0.4, 0.05)
w_rating = st.sidebar.slider("Weight - Rating (higher better)", 0.0, 1.0, 0.4, 0.05)
w_distance = st.sidebar.slider("Weight - Distance (lower better)", 0.0, 1.0, 0.2, 0.05)

st.caption(f"Loaded {len(df):,} listings; {int(crimes_df.shape[0]):,} crimes. After filters: {len(filtered):,} listings.")
if filtered.empty:
    st.warning("No listings match the selected filters. Try widening price range, lowering minimum rating, increasing max distance, or raising max crimes.")
    st.stop()

# use the weighted score to rank the listings
filtered["score"] = compute_weighted_score(filtered, (w_price, w_rating, w_distance))

# sort the listings using the remaining algorithms
algo = st.sidebar.selectbox(
    "Ranking algorithm",
    ["Top-K via heap", "HeapSort"],
    index=0,
)

# list of (score, index) pairs used for sorting and ranking:
#  - score = weighted score 
#  - index = original index in the DataFrame
pairs = [(float(s), int(i)) for i, s in zip(filtered.index, filtered["score"]) ]
if algo == "Top-K via heap":
    from src.algorithms.heap_topk import top_k_by_score

    max_k = max(1, min(100, len(pairs)))
    k = st.sidebar.slider("Top-K", min_value=1, max_value=max_k, value=min(20, max_k))
    topk = top_k_by_score(pairs, k)
    idx = [i for _, i in topk]
    filtered = filtered.loc[idx].sort_values("score", ascending=False)
elif algo == "HeapSort":
    from src.algorithms.sorting import heap_sort

    sorted_pairs = heap_sort(pairs)
    idx = [i for _, i in sorted_pairs]
    filtered = filtered.loc[idx]

# Results Table
st.subheader("Top Results")
st.dataframe(
    filtered[["score", "name", "listing_url", "price_num", "rating", "distance_km", "crime_count", "minimum_nights", "maximum_nights"]].round({"price_num": 0, "rating": 2, "distance_km": 2, "score": 3}),
    use_container_width=True,
    hide_index=True,
)

# DC Map
st.subheader("Airbnb Rental Map")
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

# Download CSV Button
st.download_button("Download CSV", data=filtered.to_csv(index=False), file_name="ranked_listings.csv", mime="text/csv")

