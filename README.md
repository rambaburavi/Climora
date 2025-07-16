# Climora
Your Weather Assistant 
This is a weather project built using Python and Flask. It collects and shows useful information about a place's weather, rainfall, soil condition, and satellite image.

## What It Does
- Shows the **live or custom weather** details for any location.
- Gives a **satellite image** of the selected place.
- Checks **rainfall** for the past 3 days and today's rain forecast.
- Fetches **soil condition** (like pH, clay, sand, etc.).
- Gives a **weekly weather summary**.
- Also gives **hourly forecast** for better planning.

---

## Tech Used
- **Python & Flask** – For backend
- **Sentinel Hub API** – For satellite images
- **SoilGrids API** – For soil data
- **Visual Crossing Weather API** – For weather and rainfall data
- **Geopy** – For converting place names to latitude and longitude

---

## Project Files
- `app.py` – Main Flask server
- `satellite_image.py` – Gets satellite image of a place
- `soil_condition.py` – Gets soil info for a location
- `rain_status.py` – Shows past and today’s rain status
- `weather_details.py` – Gives today’s weather
- `weekly_temperature.py` – Gives weekly and hourly weather
- `final_core.py` – Connects all logic together

---

##   How to Run

1. Clone the repo:
2. Install required packages:
           flask
           requests
           geopy
           pillow
           matplotlib
           python-dotenv
3. Run the Flask server:app.py
4. Open browser and go to `http://localhost:5000`
## Notes
- Make sure to add your API keys inside the scripts (for Sentinel Hub, SoilGrids, and Visual Crossing).
- You can use it as a backend and connect with any frontend like React or Streamlit.


