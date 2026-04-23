from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "dri_model.json"


def generate_synthetic_data(rows: int = 1000, seed: int = 42):
    rng = np.random.default_rng(seed)

    weather_severity = np.clip(rng.beta(2.1, 2.6, rows) * 100, 0, 100)
    congestion_score = np.clip(rng.beta(2.0, 2.2, rows) * 100, 0, 100)
    vessel_density = np.clip(rng.beta(1.8, 2.4, rows) * 100, 0, 100)
    route_length = np.clip(rng.lognormal(mean=np.log(1800), sigma=0.55, size=rows), 100, 10000)
    visibility = np.clip(rng.normal(loc=8.0, scale=1.8, size=rows), 1, 10)

    noise = rng.normal(0, 4.5, rows)
    disruption_risk = (
        0.31 * weather_severity
        + 0.29 * congestion_score
        + 0.18 * vessel_density
        + 0.14 * (route_length / 100)
        + 1.9 * (10 - visibility)
        + noise
    )
    disruption_risk = np.clip(disruption_risk, 0, 100)

    features = np.column_stack([
        weather_severity,
        congestion_score,
        vessel_density,
        route_length,
        visibility,
    ])
    target = disruption_risk
    return features, target


def main() -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    X, y = generate_synthetic_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(
        n_estimators=220,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror",
        random_state=42,
        tree_method="hist",
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))

    model.save_model(str(MODEL_PATH))
    print(f"Saved model to {MODEL_PATH}")
    print(f"Test RMSE: {rmse:.2f}")


if __name__ == "__main__":
    main()
