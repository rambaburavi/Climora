import requests
import datetime

# -----------------------
# Weather code meanings
# -----------------------
def weather_code_description(code):
    mapping = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 80: "Rain showers: slight",
        81: "Rain showers: moderate", 82: "Rain showers: violent", 95: "Thunderstorm: slight/moderate",
        96: "Thunderstorm with hail: slight", 99: "Thunderstorm with hail: heavy"
    }
    return mapping.get(code, "Unknown")

# -----------------------
# Main Weather Details Function
# -----------------------
def get_weather_details(lat, lon, name, date):
    today = datetime.date.today()

    try:
        if date < today:
            # ----- Visual Crossing (Past Data) -----
            api_key = "your_api_key"
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{date}?unitGroup=metric&key={api_key}&include=hours"
            data = requests.get(url).json()
            if "days" not in data:
                return {"status": "❌ Data not available for past date", "weather": None}

            day = data["days"][0]
            weather = {
                "location": name,
                "date": str(date),
                "sunrise": day.get("sunrise", ""),
                "sunset": day.get("sunset", ""),
                "summary": day.get("description", "N/A"),
                "temperature": day.get("temp", "N/A"),
                "temp_max": day.get("tempmax", "N/A"),
                "temp_min": day.get("tempmin", "N/A"),
                "feels_like": day.get("feelslike", "N/A"),
                "humidity": day.get("humidity", "N/A"),
                "wind_speed": day.get("windspeed", "N/A"),
                "pressure": day.get("pressure", "N/A"),
                "cloud_cover": day.get("cloudcover", "N/A"),
                "uv_index": day.get("uvindex", "N/A")
            }
            return {"status": "✅ Success (Visual Crossing)", "weather": weather}

        else:
            # ----- Open-Meteo (Today / Future) -----
            base_url = "your_api_key"
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,uv_index_max,sunrise,sunset,weathercode",
                "hourly": "temperature_2m,apparent_temperature,relative_humidity_2m,cloudcover,pressure_msl,windspeed_10m",
                "timezone": "auto",
                "start_date": date,
                "end_date": date
            }
            data = requests.get(base_url, params=params).json()

            idx = data["daily"]["time"].index(str(date))
            max_temp = data["daily"]["temperature_2m_max"][idx]
            min_temp = data["daily"]["temperature_2m_min"][idx]
            sunrise = data["daily"]["sunrise"][idx]
            sunset = data["daily"]["sunset"][idx]
            uv = data["daily"]["uv_index_max"][idx]
            code = data["daily"]["weathercode"][idx]
            summary = weather_code_description(code)

            # Hourly averages
            hourly_time = data["hourly"]["time"]
            hourly_indexes = [i for i, t in enumerate(hourly_time) if t.startswith(str(date))]

            def avg(field):
                vals = [data["hourly"][field][i] for i in hourly_indexes if data["hourly"][field][i] is not None]
                return round(sum(vals) / len(vals), 1) if vals else "N/A"

            weather = {
                "location": name,
                "date": str(date),
                "sunrise": sunrise[:16],
                "sunset": sunset[:16],
                "summary": summary,
                "temperature": avg("temperature_2m"),
                "temp_max": max_temp,
                "temp_min": min_temp,
                "feels_like": avg("apparent_temperature"),
                "humidity": avg("relative_humidity_2m"),
                "wind_speed": avg("windspeed_10m"),
                "pressure": avg("pressure_msl"),
                "cloud_cover": avg("cloudcover"),
                "uv_index": uv
            }

            return {"status": "✅ Success (Open-Meteo)", "weather": weather}

    except Exception as e:
        return {"status": f"❌ Error: {str(e)}", "weather": None}
