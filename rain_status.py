import requests
import datetime

API_KEY = "your_api_key"  # Your Visual Crossing API key

def get_rainfall_report(lat, lon, place_name, base_date):
    report = {
        "location": place_name,
        "date": str(base_date),
        "past_3_days": [],
        "today_rainfall": None
    }

    # ⏪ Loop through past 3 days
    for i in range(3, 0, -1):
        day = base_date - datetime.timedelta(days=i)
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{day}?unitGroup=metric&key={API_KEY}&include=days"

        try:
            res = requests.get(url).json()
            rain = res["days"][0].get("precip", None)
            if rain is not None:
                rain = round(rain, 1)
                status = "it rained" if rain > 0 else "no rain"
                report["past_3_days"].append({
                    "date": str(day),
                    "rainfall_mm": rain,
                    "status": status
                })
            else:
                report["past_3_days"].append({
                    "date": str(day),
                    "rainfall_mm": None,
                    "status": "no data"
                })
        except:
            report["past_3_days"].append({
                "date": str(day),
                "rainfall_mm": None,
                "status": "error"
            })

    # 📅 Today
    url_today = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{base_date}?unitGroup=metric&key={API_KEY}&include=days"

    try:
        res = requests.get(url_today).json()
        rain_today = res["days"][0].get("precip", None)
        if rain_today is not None:
            rain_today = round(rain_today, 1)
            status = "it rained" if rain_today > 0 else "no rain"
            report["today_rainfall"] = {
                "date": str(base_date),
                "rainfall_mm": rain_today,
                "status": status
            }
        else:
            report["today_rainfall"] = {
                "date": str(base_date),
                "rainfall_mm": None,
                "status": "no data"
            }
    except:
        report["today_rainfall"] = {
            "date": str(base_date),
            "rainfall_mm": None,
            "status": "error"
        }

    return report

