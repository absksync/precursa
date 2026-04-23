import json
import logging
from pathlib import Path
from typing import Dict, Iterable

import numpy as np

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover - dependency may be absent in some environments
    XGBRegressor = None


logger = logging.getLogger(__name__)

FEATURE_ORDER = ["weather_severity", "congestion_score", "vessel_density", "route_length", "visibility"]
MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "dri_model.json"
_MODEL_INSTANCE: XGBRegressor | None = None


def _coerce_features(features: Dict[str, object]) -> np.ndarray:
    values = []
    for name in FEATURE_ORDER:
        raw = features.get(name, 0)
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            values.append(0.0)
    return np.array([values], dtype=float)


def load_model() -> XGBRegressor | None:
    global _MODEL_INSTANCE

    if _MODEL_INSTANCE is not None:
        return _MODEL_INSTANCE

    if XGBRegressor is None:
        logger.warning("xgboost is not installed; ML DRI scoring disabled")
        return None

    if not MODEL_PATH.exists():
        logger.warning("ML model file missing at %s", MODEL_PATH)
        return None

    model = XGBRegressor()
    try:
        model.load_model(str(MODEL_PATH))
        _MODEL_INSTANCE = model
        return _MODEL_INSTANCE
    except Exception as exc:
        logger.warning("Failed to load ML DRI model: %s", exc)
        return None


def predict_dri(features: Dict[str, object]) -> Dict[str, float]:
    model = load_model()
    if model is None:
        raise RuntimeError("ML model unavailable")

    matrix = _coerce_features(features)
    prediction = float(model.predict(matrix)[0])
    predicted_dri = float(max(0.0, min(100.0, prediction)))

    feature_array = matrix[0]
    feature_scale = float(np.clip(np.mean(feature_array / np.array([100.0, 100.0, 100.0, 10000.0, 10.0])), 0.0, 1.0))
    model_scale = float(np.clip(predicted_dri / 100.0, 0.0, 1.0))
    confidence = float(np.clip(0.55 + (0.25 * model_scale) + (0.2 * feature_scale), 0.0, 0.95))

    return {
        "predicted_dri": round(predicted_dri, 2),
        "confidence": round(confidence, 2),
    }
