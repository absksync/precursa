import asyncio
from app.services.ais_service import stream_ais

async def start_ais_stream():
    asyncio.create_task(stream_ais())