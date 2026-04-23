from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    from tensorflow.keras.layers import LSTM, Dense
    from tensorflow.keras.models import Sequential
except Exception as exc:  # pragma: no cover - optional dependency
    raise RuntimeError(
        "TensorFlow is required for LSTM training. Install tensorflow in a compatible Python environment (recommended: Python 3.11/3.12)."
    ) from exc


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "lstm_dri_model.h5"
SEQ_LEN = 10


def _clip(arr, low, high):
    return np.clip(arr, low, high)


def generate_synthetic_sequences(samples: int = 1500, seed: int = 21):
    rng = np.random.default_rng(seed)

    X = np.zeros((samples, SEQ_LEN, 4), dtype=np.float32)
    y = np.zeros((samples, 1), dtype=np.float32)

    for i in range(samples):
        base_weather = rng.uniform(20, 85)
        base_congestion = rng.uniform(20, 85)
        base_density = rng.uniform(10, 90)
        base_visibility = rng.uniform(3, 10)

        weather_trend = rng.uniform(-2.5, 2.8)
        congestion_trend = rng.uniform(-2.3, 2.5)
        density_trend = rng.uniform(-1.8, 2.2)
        visibility_trend = rng.uniform(-0.22, 0.18)

        for t in range(SEQ_LEN):
            noise = rng.normal(0, 2.3, size=4)
            weather = base_weather + weather_trend * t + noise[0]
            congestion = base_congestion + congestion_trend * t + noise[1]
            density = base_density + density_trend * t + noise[2]
            visibility = base_visibility + visibility_trend * t + noise[3] * 0.08

            X[i, t, 0] = _clip(weather, 0, 100)
            X[i, t, 1] = _clip(congestion, 0, 100)
            X[i, t, 2] = _clip(density, 0, 100)
            X[i, t, 3] = _clip(visibility, 1, 10)

        next_weather = _clip(base_weather + weather_trend * SEQ_LEN + rng.normal(0, 2.0), 0, 100)
        next_congestion = _clip(base_congestion + congestion_trend * SEQ_LEN + rng.normal(0, 2.0), 0, 100)
        next_density = _clip(base_density + density_trend * SEQ_LEN + rng.normal(0, 1.8), 0, 100)
        next_visibility = _clip(base_visibility + visibility_trend * SEQ_LEN + rng.normal(0, 0.2), 1, 10)

        target = (
            0.36 * next_weather
            + 0.34 * next_congestion
            + 0.2 * next_density
            + 0.1 * (100 - next_visibility * 10)
            + rng.normal(0, 3.0)
        )
        y[i, 0] = _clip(target, 0, 100)

    scale = np.array([100.0, 100.0, 100.0, 10.0], dtype=np.float32)
    X = X / scale
    return X, y


def main() -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    X, y = generate_synthetic_sequences()
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = Sequential([
        LSTM(64, input_shape=(SEQ_LEN, 4)),
        Dense(32, activation="relu"),
        Dense(1),
    ])

    model.compile(optimizer="adam", loss="mse")
    model.fit(X_train, y_train, validation_split=0.1, epochs=12, batch_size=32, verbose=0)

    preds = model.predict(X_test, verbose=0)
    rmse = float(np.sqrt(np.mean((preds - y_test) ** 2)))

    model.save(str(MODEL_PATH))
    print(f"Saved LSTM model to {MODEL_PATH}")
    print(f"LSTM Test RMSE: {rmse:.2f}")


if __name__ == "__main__":
    main()
