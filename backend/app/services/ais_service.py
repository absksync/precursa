import asyncio
import json
import websockets
from app.core.config import settings

# In-memory store
VESSELS = []


async def stream_ais():
    url = "wss://stream.aisstream.io/v0/stream"

    try:
        async with websockets.connect(url) as ws:
            subscribe_message = {
                "APIKey": settings.AIS_API_KEY,
                "BoundingBoxes": [[[1.0, 103.5], [1.5, 104.1]]]  # Singapore Strait
            }

            await ws.send(json.dumps(subscribe_message))

            async for message in ws:
                data = json.loads(message)

                if "Message" in data:
                    try:
                        vessel = data["Message"]["PositionReport"]

                        lat = vessel.get("Latitude")
                        lon = vessel.get("Longitude")

                        # ✅ Filter only valid sea region (clean demo)
                        if lat and lon:
                            if 1.0 < lat < 1.5 and 103.6 < lon < 104.1:
                                VESSELS.append({
                                    "lat": lat,
                                    "lon": lon
                                })

                        # ✅ Keep list small (UI clarity + performance)
                        if len(VESSELS) > 15:
                            VESSELS.pop(0)

                    except Exception:
                        continue

    except Exception as e:
        print("AIS Stream Error:", e)