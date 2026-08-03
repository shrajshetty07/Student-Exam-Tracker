"""
train_regression.py
--------------------
Trains a RandomForestRegressor that predicts a student's next / final
exam score (out of 50) from their attendance, study habits and internal
assessment marks. The trained model is serialized to regression_model.pkl.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

from ml.preprocess import prepare_data
from ml.utils import save_model, save_metrics, REGRESSION_MODEL_PATH, get_logger

logger = get_logger(__name__)


def train_regression_model():
    logger.info("Starting regression model training")
    X, y_reg, _, _ = prepare_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_reg, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    logger.info("Regression MAE=%.3f RMSE=%.3f R2=%.3f", mae, rmse, r2)

    save_model(model, REGRESSION_MODEL_PATH)

    feature_importance = dict(zip(X.columns, model.feature_importances_.round(4).tolist()))

    save_metrics({
        "regression": {
            "mae": round(float(mae), 3),
            "rmse": round(float(rmse), 3),
            "r2_score": round(float(r2), 3),
            "feature_importance": feature_importance,
            "n_estimators": 300,
            "test_size": 0.2,
        }
    })

    logger.info("Regression model saved to %s", REGRESSION_MODEL_PATH)
    return model, {"mae": mae, "rmse": rmse, "r2": r2}


if __name__ == "__main__":
    train_regression_model()
