import asyncio
import logging

from app.services.ais_service import stream_ais


logger = logging.getLogger(__name__)


async def start_ais_stream():
    logger.info("Starting AIS background stream task")
    asyncio.create_task(stream_ais())