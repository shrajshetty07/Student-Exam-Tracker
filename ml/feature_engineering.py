"""
feature_engineering.py
-----------------------
Derives additional engineered features from the raw student marks data.
These engineered features are used to improve model accuracy and also
to power dashboard analytics (e.g. consistency score, engagement score).
"""

import pandas as pd


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns that help both the models and the analytics dashboard."""
    df = df.copy()

    # Overall internal performance before the final exam
    df["Internal_Performance"] = (
        df["Assignment_Marks"] + df["Quiz_Marks"] + df["Lab_Marks"] + df["Project_Marks"]
    )

    # Engagement score blends attendance with study hours (capped scaling)
    df["Engagement_Score"] = (
        0.6 * df["Attendance"] + 0.4 * (df["Study_Hours"].clip(upper=12) / 12 * 100)
    ).round(2)

    # Consistency: how close internal performance is to previous semester marks
    df["Consistency_Score"] = (
        100 - (df["Internal_Performance"] / df["Internal_Performance"].max() * 100 -
               df["Previous_Semester_Marks"]).abs()
    ).clip(lower=0, upper=100).round(2)

    # Risk flag: heuristic pre-model indicator used for quick filtering
    df["At_Risk"] = (
        (df["Attendance"] < 65) | (df["Previous_Semester_Marks"] < 45) | (df["Study_Hours"] < 2)
    )

    return df


if __name__ == "__main__":
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "dataset", "student_dataset.csv")
    sample = pd.read_csv(path).head(10)
    enriched = add_engineered_features(sample)
    print(enriched[["Student_ID", "Engagement_Score", "Consistency_Score", "At_Risk"]])
