"""
predict.py
----------
Inference layer used by the Flask application. Loads the trained
regression + classification models and exposes a single function,
predict_student(), that the /prediction route calls.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd

from ml.utils import (
    load_model, REGRESSION_MODEL_PATH, CLASSIFIER_MODEL_PATH,
    LABEL_ENCODER_PATH, FEATURE_COLUMNS, get_logger
)

logger = get_logger(__name__)

_regression_model = None
_classifier_model = None
_label_encoder = None


def _lazy_load():
    """Load models into module-level cache on first use."""
    global _regression_model, _classifier_model, _label_encoder
    if _regression_model is None:
        _regression_model = load_model(REGRESSION_MODEL_PATH)
    if _classifier_model is None:
        _classifier_model = load_model(CLASSIFIER_MODEL_PATH)
    if _label_encoder is None:
        _label_encoder = load_model(LABEL_ENCODER_PATH)


def predict_student(features: dict) -> dict:
    """
    Predict next exam score + pass/fail outcome for one student.

    features must contain all FEATURE_COLUMNS keys:
        Attendance, Study_Hours, Assignment_Marks, Quiz_Marks, Lab_Marks,
        Internal_Marks, Previous_Semester_Marks, Project_Marks

    Returns a dict with predicted_score, pass_fail, confidence and risk_level.
    """
    _lazy_load()

    row = pd.DataFrame([[features[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)

    predicted_score = float(_regression_model.predict(row)[0])
    predicted_score = round(max(0, min(50, predicted_score)), 2)

    proba = _classifier_model.predict_proba(row)[0]
    pred_class_idx = int(np.argmax(proba))
    pred_label = _label_encoder.inverse_transform([pred_class_idx])[0]
    confidence = round(float(proba[pred_class_idx]) * 100, 2)

    fail_idx = list(_label_encoder.classes_).index("Fail") if "Fail" in _label_encoder.classes_ else None
    fail_probability = round(float(proba[fail_idx]) * 100, 2) if fail_idx is not None else None

    if fail_probability is None:
        risk_level = "Unknown"
    elif fail_probability >= 60:
        risk_level = "High"
    elif fail_probability >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "predicted_score": predicted_score,
        "pass_fail": pred_label,
        "confidence": confidence,
        "fail_probability": fail_probability,
        "risk_level": risk_level,
    }


def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Run predictions for an entire DataFrame of students (used for risk analysis)."""
    _lazy_load()
    X = df[FEATURE_COLUMNS]
    df = df.copy()
    df["Predicted_Score"] = _regression_model.predict(X).round(2)
    proba = _classifier_model.predict_proba(X)
    fail_idx = list(_label_encoder.classes_).index("Fail") if "Fail" in _label_encoder.classes_ else 0
    df["Fail_Probability"] = (proba[:, fail_idx] * 100).round(2)
    df["Risk_Level"] = pd.cut(
        df["Fail_Probability"], bins=[-1, 30, 60, 101], labels=["Low", "Medium", "High"]
    )
    return df


if __name__ == "__main__":
    sample = {
        "Attendance": 72,
        "Study_Hours": 3.5,
        "Assignment_Marks": 14,
        "Quiz_Marks": 7,
        "Lab_Marks": 15,
        "Internal_Marks": 16,
        "Previous_Semester_Marks": 58,
        "Project_Marks": 7,
    }
    print(predict_student(sample))
