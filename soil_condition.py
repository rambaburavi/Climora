import datetime
import requests
import numpy as np
from sentinelhub import SHConfig, BBox, CRS, SentinelHubRequest, MimeType, bbox_to_dimensions
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Sentinel Hub Config
config = SHConfig()
config.sh_client_id = "2ed23a6a-5abb-42bf-906e-805690e56802"
config.sh_client_secret = "N14niwGjlJ3s90x1qxZbqmVr2W7kF5zp"

# NDVI Evalscript
evalscript = """//VERSION=3
function setup() {
  return {
    input: ["B08", "B04"],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
"""

# MAIN FUNCTION
def estimate_soil_condition(latitude, longitude, base_date):
    bbox = BBox([longitude - 0.01, latitude - 0.01, longitude + 0.01, latitude + 0.01], crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox, resolution=60)

    ndvi_mean, used_date = None, None

    # Search past 15 days for valid NDVI
    for i in range(15):
        date = base_date - datetime.timedelta(days=i)
        request = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[{
                "type": "sentinel-2-l1c",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{date}T00:00:00Z",
                        "to": f"{date}T23:59:59Z"
                    }
                }
            }],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            config=config
        )
        try:
            ndvi_data = request.get_data()[0].squeeze()
            mean_val = np.nanmean(ndvi_data)
            if not np.isnan(mean_val):
                ndvi_mean = round(float(mean_val), 2)
                used_date = date
                break
        except:
            continue

    rain, humidity = None, None

    # Fetch Weather if NDVI is available
    if used_date:
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&hourly=precipitation,relative_humidity_2m"
            f"&start_date={used_date}&end_date={used_date}&timezone=auto"
        )
        try:
            res = requests.get(weather_url)
            weather = res.json()
            rain_vals = weather.get("hourly", {}).get("precipitation", [])
            humidity_vals = weather.get("hourly", {}).get("relative_humidity_2m", [])
            if rain_vals and humidity_vals:
                rain = round(sum(rain_vals), 1)
                humidity = round(sum(humidity_vals) / len(humidity_vals), 1)
        except:
            pass

    # Estimate Condition
    if ndvi_mean is None:
        condition = "❌ Could not estimate – NDVI unavailable"
        status = "error"
    elif ndvi_mean > 0.5:
        condition = "Very Moist"
        status = "success"
    elif ndvi_mean > 0.3:
        condition = "Moist"
        status = "success"
    else:
        condition = "Dry"
        status = "success"

    return {
        "used_date": str(used_date) if used_date else None,
        "ndvi_mean": ndvi_mean,
        "rain": rain,
        "humidity": humidity,
        "estimated_condition": condition,
        "status": status
    }

# Example test (optional)
if __name__ == "__main__":
    lat, lon = 11.01, 77.02
    base_date = datetime.date.today()
    result = estimate_soil_condition(lat, lon, base_date)
    print(result)
