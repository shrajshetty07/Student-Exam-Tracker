"""
evaluate.py
-----------
Standalone script to (re)compute and print evaluation metrics for both
the regression and classification models. Also used by the Flask
/analytics route indirectly through ml/utils.load_metrics(), but this
script can be run manually for a CLI report:

    python ml/evaluate.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from ml.utils import load_metrics, get_logger

logger = get_logger(__name__)


def print_report():
    metrics = load_metrics()
    if not metrics:
        print("No metrics found. Run train_regression.py and train_classifier.py first.")
        return

    reg = metrics.get("regression", {})
    clf = metrics.get("classification", {})

    print("=" * 60)
    print("REGRESSION MODEL (Next Exam Score Prediction)")
    print("=" * 60)
    print(f"MAE  : {reg.get('mae')}")
    print(f"RMSE : {reg.get('rmse')}")
    print(f"R2   : {reg.get('r2_score')}")

    print()
    print("=" * 60)
    print("CLASSIFICATION MODEL (Pass / Fail Prediction)")
    print("=" * 60)
    print(f"Accuracy  : {clf.get('accuracy')}")
    print(f"Precision : {clf.get('precision')}")
    print(f"Recall    : {clf.get('recall')}")
    print(f"F1 Score  : {clf.get('f1_score')}")
    print(f"ROC AUC   : {clf.get('roc_auc')}")
    print(f"Confusion Matrix ({clf.get('labels')}): {clf.get('confusion_matrix')}")


if __name__ == "__main__":
    print_report()
