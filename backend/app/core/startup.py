import asyncio
import logging

from app.services.ais_service import stream_ais
from app.services.lstm_service import load_model as load_lstm_model
from app.services.ml_service import load_model


logger = logging.getLogger(__name__)


async def start_ais_stream():
    logger.info("Starting AIS background stream task")
    asyncio.create_task(stream_ais())


def preload_ml_model() -> None:
    logger.info("Preloading ML DRI model")
    load_model()
    logger.info("Preloading LSTM DRI model")
    load_lstm_model()