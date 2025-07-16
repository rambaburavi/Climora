import requests

def get_hourly_temperature(lat, lon, date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "start_date": str(date),
        "end_date": str(date),
        "timezone": "auto"
    }

    try:
        res = requests.get(url, params=params).json()

        times = res["hourly"]["time"]
        temps = res["hourly"]["temperature_2m"]

        hourly_data = []
        for t, temp in zip(times, temps):
            day, hour = t.split("T")
            if day == str(date):  # Ensure exact date match
                hourly_data.append({
                    "hour": hour,
                    "temperature": round(temp, 1)
                })

        return {
            "status": "success",
            "date": str(date),
            "hourly_temperatures": hourly_data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "hourly_temperatures": []
        }
