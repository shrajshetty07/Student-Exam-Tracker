"""
train_classifier.py
--------------------
Trains a RandomForestClassifier that predicts whether a student will
Pass or Fail based on attendance, study habits and internal assessment
marks. Also computes full evaluation analytics: accuracy, precision,
recall, F1, confusion matrix and ROC curve points.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc
)

from ml.preprocess import prepare_data
from ml.utils import save_model, save_metrics, CLASSIFIER_MODEL_PATH, LABEL_ENCODER_PATH, get_logger

logger = get_logger(__name__)


def train_classifier_model():
    logger.info("Starting classification model training")
    X, _, y_clf, encoder = prepare_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_clf, test_size=0.2, random_state=42, stratify=y_clf
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()

    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)

    logger.info(
        "Classifier Accuracy=%.3f Precision=%.3f Recall=%.3f F1=%.3f AUC=%.3f",
        acc, precision, recall, f1, roc_auc
    )

    save_model(model, CLASSIFIER_MODEL_PATH)
    save_model(encoder, LABEL_ENCODER_PATH)

    feature_importance = dict(zip(X.columns, model.feature_importances_.round(4).tolist()))

    # Downsample ROC points for compact storage / chart rendering
    step = max(1, len(fpr) // 30)
    roc_points = [{"fpr": round(float(f), 4), "tpr": round(float(t), 4)}
                  for f, t in zip(fpr[::step], tpr[::step])]

    save_metrics({
        "classification": {
            "accuracy": round(float(acc), 3),
            "precision": round(float(precision), 3),
            "recall": round(float(recall), 3),
            "f1_score": round(float(f1), 3),
            "confusion_matrix": cm,
            "labels": encoder.classes_.tolist(),
            "roc_auc": round(float(roc_auc), 3),
            "roc_points": roc_points,
            "feature_importance": feature_importance,
        }
    })

    logger.info("Classifier model saved to %s", CLASSIFIER_MODEL_PATH)
    return model, encoder, {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}


if __name__ == "__main__":
    train_classifier_model()
