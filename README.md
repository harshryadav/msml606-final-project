# MSML606 Final Project — DC Airbnb Rental Filter & Ranking

This is a minimal yet functional MVP to explore Washington DC Airbnb listings, filter by price/rating/distance and neighborhood safety, and rank results using a simple weighted score. The app runs locally with Streamlit and uses no external APIs.

## What it does
- Upload or use a sample listings CSV
- Choose a destination (e.g., White House) or enter custom coordinates
- Filter by price, rating, and max distance
- Adjust weights for price/rating/distance to rank listings
- Choose a simple algorithm for ranking:
  - **Pandas sort** (default)
  - **Top-K via heap** (min-heap data structure)
  - **QuickSort** or **HeapSort** on in-memory pairs
  - **Dijkstra (min-cost pick)**: picks a single best listing by converting score to cost and running shortest path on a tiny star graph
- View results on a table and a map, download ranked CSV

Notes:
- Distance is computed locally via haversine (straight-line). No Google API.
- Expected columns in CSV: `id,name,latitude,longitude,price,rating` (or `review_scores_rating` in 0–100, which will be converted to 0–5).

If present, the app will automatically use `data/dc-listings.csv` and `data/dc-crimes.csv`:
- `dc-listings.csv`: InsideAirbnb full export (large). The app extracts only needed columns.
- `dc-crimes.csv`: Must include `LATITUDE` and `LONGITUDE` (or lowercase). Crimes near each listing are counted within a selectable radius using a simple array data structure (vectorized haversine).

## Project structure
```
msml606-final-project/
  app.py                  # Streamlit app
  requirements.txt        # Minimal dependencies
  data/
    dc-listings.csv       # InsideAirbnb DC (preferred if present)
    dc-crimes.csv         # DC crimes (preferred if present)
  src/
    __init__.py
    utils.py              # haversine + normalization
    scoring.py            # weighted score computation
    data/
      __init__.py
      loader.py           # CSV reading + cleaning (listings & crimes)
    features/
      __init__.py
      safety.py           # vectorized crime counts within radius
    algorithms/
      __init__.py
      heap_topk.py        # Top-K using a min-heap
      sorting.py          # QuickSort & HeapSort (educational)
      dijkstra.py         # star-graph min-cost pick
```

## Setup
1) Python 3.10+ recommended

2) Create and activate a virtual environment

macOS/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```
py -3 -m venv .venv
.venv\Scripts\activate
```

To deactivate later:
```
deactivate
```

3) Install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app
```
streamlit run app.py
```

Then open the URL printed in your terminal (typically `http://localhost:8501`).

## Using your own data
- Download InsideAirbnb DC listings and export a CSV with at least:
  - `id, name, latitude, longitude, price, rating`
  - Or `review_scores_rating` (0–100) instead of `rating`
- Place it at `data/dc-listings.csv` (preferred) or upload via the sidebar in the app.
- Crime CSV at `data/dc-crimes.csv` should include `LATITUDE` and `LONGITUDE`.

