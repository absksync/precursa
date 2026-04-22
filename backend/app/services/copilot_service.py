import requests
from app.core.config import settings


def get_ai_explanation(shipment):
    try:
        prompt = f"""
You are a logistics AI assistant.

Analyze this shipment and explain the disruption risk in a simple and professional way.

Shipment Data:
- Origin: {shipment['origin']}
- Destination: {shipment['destination']}
- DRI: {shipment['dri']}
- Weather Risk: {shipment.get('weather_risk', 'N/A')}

Respond in 2-3 short sentences explaining:
- Why the risk is high/low
- What factors are causing it
- Keep it concise and industry-friendly
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={settings.GEMINI_API_KEY}"

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        response = requests.post(url, json=body)
        data = response.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]

        return text

    except Exception as e:
        print("Gemini Error:", e)
        return "Unable to generate explanation."