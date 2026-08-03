"""
preprocess.py
-------------
Loads the raw student dataset and prepares it for both the regression
(next exam score prediction) and classification (pass/fail prediction)
models.

Responsibilities:
    * Load CSV into a pandas DataFrame
    * Handle missing values
    * Encode categorical target (Pass/Fail) with LabelEncoder
    * Return clean feature matrix (X) and targets (y_reg, y_clf)
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder

from ml.utils import DATASET_PATH, FEATURE_COLUMNS, REGRESSION_TARGET, CLASSIFICATION_TARGET, get_logger

logger = get_logger(__name__)


def load_dataset() -> pd.DataFrame:
    """Load the student dataset CSV file into a DataFrame."""
    logger.info("Loading dataset from %s", DATASET_PATH)
    df = pd.read_csv(DATASET_PATH)
    logger.info("Loaded %d rows, %d columns", df.shape[0], df.shape[1])
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate rows and impute missing numeric values with the column mean."""
    df = df.drop_duplicates().copy()
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    return df


def get_feature_matrix(df: pd.DataFrame):
    """Return the feature matrix X used by both models."""
    return df[FEATURE_COLUMNS].copy()


def get_regression_target(df: pd.DataFrame):
    """Return the continuous target used for score prediction."""
    return df[REGRESSION_TARGET].copy()


def get_classification_target(df: pd.DataFrame, encoder: LabelEncoder = None):
    """
    Return the encoded Pass/Fail target.
    If an encoder is not supplied, a new LabelEncoder is fit and returned.
    """
    if encoder is None:
        encoder = LabelEncoder()
        y = encoder.fit_transform(df[CLASSIFICATION_TARGET])
    else:
        y = encoder.transform(df[CLASSIFICATION_TARGET])
    return y, encoder


def prepare_data():
    """
    Convenience function used by the training scripts.
    Returns: X, y_reg, y_clf, label_encoder
    """
    df = clean_dataset(load_dataset())
    X = get_feature_matrix(df)
    y_reg = get_regression_target(df)
    y_clf, encoder = get_classification_target(df)
    return X, y_reg, y_clf, encoder


if __name__ == "__main__":
    X, y_reg, y_clf, encoder = prepare_data()
    print("Feature matrix shape:", X.shape)
    print("Regression target sample:", y_reg.head().tolist())
    print("Classification classes:", list(encoder.classes_))
