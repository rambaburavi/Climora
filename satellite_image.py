# satellite_image.py
import requests
import os

GOOGLE_API_KEY = "AIzaSyDCniccFISBOmTp4szMHZ3JSZ_Iyzfqidk"  # 🔁 Replace this with your real key

def generate_satellite_image(lat, lon, date):
    zoom = 20  # 🔍 Zoom level: 17–19 works well
    width = 640
    height = 640
    maptype = "satellite"

    # Ensure images directory exists
    if not os.path.exists("images"):
        os.makedirs("images")

    image_filename = f"satellite_{lat}_{lon}_{date}.png"
    image_path = os.path.join("images", image_filename)

    if os.path.exists(image_path):
        return {
            "status": "✅ Success (cached)",
            "image_path": image_path,
            "image_url": f"/images/{image_filename}",
            "used_date": date
        }

    url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={lat},{lon}&zoom={zoom}&size={width}x{height}"
        f"&maptype={maptype}&key={GOOGLE_API_KEY}"
    )

    try:
        response = requests.get(url)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            return {
                "status": "✅ Success (Google Maps)",
                "image_path": image_path,
                "image_url": f"/images/{image_filename}",
                "used_date": date
            }
        else:
            raise ValueError("❌ Invalid image response")
    except Exception as e:
        return {
            "status": f"❌ Image fetch failed: {e}",
            "image_path": None,
            "image_url": None,
            "used_date": None
        }
