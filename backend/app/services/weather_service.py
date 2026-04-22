import requests
from app.core.config import settings


def get_weather_risk(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.WEATHER_API_KEY}"

        response = requests.get(url)
        data = response.json()

        # 🔥 Extract richer data
        wind_speed = data.get("wind", {}).get("speed", 0)
        clouds = data.get("clouds", {}).get("all", 0)
        rain = data.get("rain", {}).get("1h", 0)

        # 🔥 Build dynamic score
        risk = 0

        # Wind impact
        if wind_speed > 10:
            risk += 40
        elif wind_speed > 5:
            risk += 20

        # Cloud impact
        if clouds > 80:
            risk += 20
        elif clouds > 50:
            risk += 10

        # Rain impact
        if rain > 5:
            risk += 30
        elif rain > 1:
            risk += 15

        # Normalize
        risk = min(100, risk + 10)

        print(f"Weather Debug → wind:{wind_speed}, clouds:{clouds}, rain:{rain}, risk:{risk}")

        return risk

    except Exception as e:
        print("Weather API error:", e)
        return 20