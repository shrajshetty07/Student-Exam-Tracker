"""
utils.py
--------
Shared utility helpers used across the machine learning pipeline
(preprocessing, training, evaluation and inference).

Keeping these helpers in one place avoids duplication between
train_regression.py, train_classifier.py, predict.py and evaluate.py.
"""

import os
import json
import logging

import joblib

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "student_dataset.csv")

REGRESSION_MODEL_PATH = os.path.join(BASE_DIR, "regression_model.pkl")
CLASSIFIER_MODEL_PATH = os.path.join(BASE_DIR, "classifier.pkl")
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "metrics.json")

FEATURE_COLUMNS = [
    "Attendance",
    "Study_Hours",
    "Assignment_Marks",
    "Quiz_Marks",
    "Lab_Marks",
    "Internal_Marks",
    "Previous_Semester_Marks",
    "Project_Marks",
]

REGRESSION_TARGET = "Final_Exam_Marks"
CLASSIFICATION_TARGET = "Pass_Fail"


# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
def get_logger(name: str) -> logging.Logger:
    """Return a configured logger that writes to logs/ml.log and stdout."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    log_dir = os.path.join(BASE_DIR, "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(os.path.join(log_dir, "ml.log"))
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


# ----------------------------------------------------------------------
# Persistence helpers
# ----------------------------------------------------------------------
def save_model(model, path: str) -> None:
    """Serialize a trained model / encoder to disk with joblib."""
    joblib.dump(model, path)


def load_model(path: str):
    """Load a previously serialized model / encoder from disk."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model file not found at {path}. Run the training scripts first: "
            f"python ml/train_regression.py && python ml/train_classifier.py"
        )
    return joblib.load(path)


def save_metrics(metrics: dict) -> None:
    """Persist evaluation metrics as JSON so the dashboard can display them."""
    existing = {}
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = {}
    existing.update(metrics)
    with open(METRICS_PATH, "w") as f:
        json.dump(existing, f, indent=2)


def load_metrics() -> dict:
    """Load previously saved evaluation metrics, or an empty dict."""
    if not os.path.exists(METRICS_PATH):
        return {}
    with open(METRICS_PATH, "r") as f:
        return json.load(f)
