# MSML606 Final Project — DC Airbnb Rental Filter & Ranking

This is a minimal yet functional MVP to explore Washington DC Airbnb listings, filter by price/rating/distance, and rank results using a simple weighted score. The app runs locally with Streamlit and uses no external APIs.

## What it does
- Upload or use a sample listings CSV
- Choose a destination (e.g., White House) or enter custom coordinates
- Filter by price, rating, and max distance
- Adjust weights for price/rating/distance to rank listings
- View results on a table and a map, download ranked CSV

Notes:
- Distance is computed locally via haversine (straight-line). No Google API.
- Expected columns in CSV: `id,name,latitude,longitude,price,rating` (or `review_scores_rating` in 0–100, which will be converted to 0–5).

## Project structure
```
msml606-final-project/
  app.py                  # Streamlit app
  requirements.txt        # Minimal dependencies
  data/
    listings.csv          # Small sample so the app runs out of the box
  src/
    __init__.py
    utils.py              # haversine + normalization helpers
    data_loader.py        # CSV reading + cleaning
    scoring.py            # weighted score computation
```

## Setup
1) Python 3.10+ recommended
2) Install dependencies:
```
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
- Place it at `data/listings.csv` or upload via the sidebar in the app.

