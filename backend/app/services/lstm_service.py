import logging
from pathlib import Path
from typing import Dict, List

import numpy as np

try:
    from tensorflow.keras.models import load_model as tf_load_model
except Exception:  # pragma: no cover - optional dependency
    tf_load_model = None


logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "lstm_dri_model.h5"
SEQ_LEN = 10
FEATURE_DIM = 4
_MODEL_INSTANCE = None


def _clip(value: float, low: float, high: float) -> float:
    return float(max(low, min(high, value)))


def _normalize(sequence: np.ndarray) -> np.ndarray:
    scale = np.array([100.0, 100.0, 100.0, 10.0], dtype=float)
    return sequence / scale


def _reshape_sequence(sequence: List[List[float]]) -> np.ndarray:
    arr = np.array(sequence, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != FEATURE_DIM:
        raise ValueError("sequence must have shape (timesteps, 4)")

    if arr.shape[0] > SEQ_LEN:
        arr = arr[-SEQ_LEN:, :]
    elif arr.shape[0] < SEQ_LEN:
        pad_rows = SEQ_LEN - arr.shape[0]
        pad = np.repeat(arr[[0], :], pad_rows, axis=0)
        arr = np.vstack([pad, arr])

    return arr


def _infer_trend(sequence: np.ndarray) -> str:
    def proxy(row: np.ndarray) -> float:
        weather, congestion, density, visibility = row.tolist()
        return 0.35 * weather + 0.35 * congestion + 0.2 * density + 0.1 * (100.0 - (visibility * 10.0))

    start = proxy(sequence[0])
    end = proxy(sequence[-1])
    delta = end - start
    if delta > 3:
        return "increasing"
    if delta < -3:
        return "decreasing"
    return "stable"


def load_model():
    global _MODEL_INSTANCE

    if _MODEL_INSTANCE is not None:
        return _MODEL_INSTANCE

    if tf_load_model is None:
        logger.warning("tensorflow is not installed; LSTM DRI scoring disabled")
        return None

    if not MODEL_PATH.exists():
        logger.warning("LSTM model file missing at %s", MODEL_PATH)
        return None

    try:
        _MODEL_INSTANCE = tf_load_model(str(MODEL_PATH))
        return _MODEL_INSTANCE
    except Exception as exc:
        logger.warning("Failed to load LSTM model: %s", exc)
        return None


def predict_dri(sequence: List[List[float]]) -> Dict[str, object]:
    model = load_model()
    if model is None:
        raise RuntimeError("LSTM model unavailable")

    raw = _reshape_sequence(sequence)
    normalized = _normalize(raw)
    pred = float(model.predict(np.expand_dims(normalized, axis=0), verbose=0)[0][0])
    lstm_dri = _clip(pred, 0.0, 100.0)
    trend = _infer_trend(raw)

    return {
        "lstm_dri": round(lstm_dri, 2),
        "trend": trend,
    }
