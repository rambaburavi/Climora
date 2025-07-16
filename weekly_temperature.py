import requests
import datetime

VISUAL_CROSSING_API_KEY = "PG6HXMUZTJCLQBRUKBGVBRC9N"

# 🌧️ Get past temperature from Visual Crossing with fallback
def get_past_temperature(lat, lon, date):
    url = (
        f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        f"{lat},{lon}/{date}?unitGroup=metric&key={VISUAL_CROSSING_API_KEY}&include=days"
    )
    try:
        res = requests.get(url, timeout=10).json()
        day_data = res["days"][0]
        return {
            "date": str(date),
            "temp_min": round(day_data.get("tempmin", 0), 1),
            "temp_max": round(day_data.get("tempmax", 0), 1),
            "status": "success (VC)"
        }
    except:
        print(f"[⚠️ VC Failed] Falling back to Open-Meteo for {date}...")
        try:
            fallback = get_future_temperature(lat, lon, date, date)[0]
            fallback["status"] = "fallback (OM)"
            return fallback
        except:
            return {
                "date": str(date),
                "temp_min": None,
                "temp_max": None,
                "status": "error (VC+OM)"
            }

# ☀️ Get future/present temperature from Open-Meteo
def get_future_temperature(lat, lon, start_date, end_date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "start_date": str(start_date),
        "end_date": str(end_date)
    }
    try:
        res = requests.get(url, params=params, timeout=10).json()
        dates = res["daily"]["time"]
        max_vals = res["daily"]["temperature_2m_max"]
        min_vals = res["daily"]["temperature_2m_min"]
        return [
            {
                "date": dates[i],
                "temp_min": round(min_vals[i], 1),
                "temp_max": round(max_vals[i], 1),
                "status": "success (OM)"
            }
            for i in range(len(dates))
        ]
    except:
        return [{
            "date": str(start_date),
            "temp_min": None,
            "temp_max": None,
            "status": "error (OM)"
        }]

# ⏰ Get hourly temperature from Open-Meteo
def get_hourly_data(lat, lon, date):
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
        res = requests.get(url, params=params, timeout=10).json()
        times = res["hourly"]["time"]
        temps = res["hourly"]["temperature_2m"]
        return [
            {"hour": t.split("T")[1][:5], "temperature": round(temp, 1)}
            for t, temp in zip(times, temps)
        ]
    except:
        return []

# 🔁 Main Function: Weekly Temperature with Hourly
def get_weekly_temperature(lat, lon, place_name, base_date):
    today = datetime.date.today()
    summary = {
        "location": place_name,
        "base_date": str(base_date),
        "previous_week": [],
        "current_week": [],
        "next_week": []
    }

    # 🔹 Previous Week (base_date -7 to base_date -1)
    for i in range(7, 0, -1):
        day = base_date - datetime.timedelta(days=i)
        if day < today:
            temp = get_past_temperature(lat, lon, day)
        else:
            temp = get_future_temperature(lat, lon, day, day)[0]
        temp["hourly_temperatures"] = get_hourly_data(lat, lon, day)
        summary["previous_week"].append(temp)

    # 🔸 Current Week (base_date to base_date +6)
    for i in range(0, 7):
        day = base_date + datetime.timedelta(days=i)
        temp = get_future_temperature(lat, lon, day, day)[0]
        temp["hourly_temperatures"] = get_hourly_data(lat, lon, day)
        summary["current_week"].append(temp)

    # 🔸 Next Week (base_date +7 to base_date +13)
    for i in range(7, 14):
        day = base_date + datetime.timedelta(days=i)
        temp = get_future_temperature(lat, lon, day, day)[0]
        temp["hourly_temperatures"] = get_hourly_data(lat, lon, day)
        summary["next_week"].append(temp)

    summary["status"] = "✅ Success (Structured Weekly + Hourly Summary)"
    return summary
