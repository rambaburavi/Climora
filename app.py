from flask import Flask, request, jsonify, send_from_directory
from final_core import (
    location_to_coordinates,
    get_rainfall_report,
    generate_satellite_image,
    estimate_soil_condition,
    get_weather_details,
    get_weekly_temperature,
    get_hourly_forecast
)
from datetime import datetime
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

@app.route("/images/<filename>")
def serve_image(filename):
    image_dir = os.path.abspath(".")
    return send_from_directory(image_dir, filename)

@app.route("/", methods=["GET"])
def home():
    return "✅ Project Weather API is running!"

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong!"})

@app.route("/weather", methods=["POST"])
def full_weather_report():
    try:
        data = request.get_json()
        location = data.get("location")
        date_str = data.get("date")

        if not location or not date_str:
            return jsonify({"status": "error", "message": "Missing 'location' or 'date'."}), 400

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}), 400

        print("📍 Resolving coordinates...")
        lat, lon, full_place = location_to_coordinates(location)
        if not lat or not lon:
            return jsonify({"status": "error", "message": "Could not resolve location."}), 400

        # Fetching all modules
        print("📡 Calling get_rainfall_report...")
        start = time.time()
        rainfall = get_rainfall_report(lat, lon, full_place, date)
        print("⏱️ Rainfall done in", round(time.time() - start, 2), "s")

        print("🛰️ Calling generate_satellite_image...")
        start = time.time()
        satellite = generate_satellite_image(lat, lon, date)
        print("⏱️ Satellite done in", round(time.time() - start, 2), "s")

        print("🌱 Calling estimate_soil_condition...")
        start = time.time()
        soil = estimate_soil_condition(lat, lon, date)
        print("⏱️ Soil condition done in", round(time.time() - start, 2), "s")

        print("🌤️ Calling get_weather_details...")
        start = time.time()
        weather = get_weather_details(lat, lon, full_place, date)
        print("⏱️ Weather details done in", round(time.time() - start, 2), "s")

        print("📊 Calling get_weekly_temperature...")
        start = time.time()
        weekly = get_weekly_temperature(lat, lon, full_place, date)
        print("⏱️ Weekly summary done in", round(time.time() - start, 2), "s")

        print("⏰ Calling get_hourly_forecast...")
        start = time.time()
        today_hourly = get_hourly_forecast(lat, lon, date)
        print("⏱️ Hourly forecast done in", round(time.time() - start, 2), "s")

        # Construct full satellite image URL
        image_path = satellite.get("image_path")
        if image_path:
            satellite["image_url"] = f"{request.host_url.rstrip('/')}/images/{os.path.basename(image_path)}"

        # Final result object
        result = {
            "rainfall": rainfall,  # ✅ make sure this includes today & past days
            "satellite_image": satellite,
            "soil_condition": soil,
            "weather_details": weather,
            "weekly_summary": weekly,
            "hourly_forecast": today_hourly
        }

        # Debug: Check if rainfall has today + past_1_day etc.
        print("✅ Final JSON keys:", result.keys())
        print("🌧️ Rainfall Data (debug):", rainfall)

        return jsonify({"status": "success", "data": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/hourly_forecast", methods=["POST"])
def hourly_forecast():
    try:
        data = request.get_json()
        print("📥 Hourly forecast request received:", data)
        location = data.get("location")
        date_str = data.get("date")
        print("🧪 location:", location, "| date:", date_str)

        if not location or not date_str:
            return jsonify({"status": "error", "message": "Missing 'location' or 'date'."}), 400

        lat, lon, full_place = location_to_coordinates(location)
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

        hourly = get_hourly_forecast(lat, lon, date)
        rainfall = get_rainfall_report(lat, lon, full_place, date)  # ✅ included
        print("🌧️ Rainfall report fetched:", rainfall)

        return jsonify({
            "status": "success",
            "hourly": hourly,
            "rainfall": rainfall
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
