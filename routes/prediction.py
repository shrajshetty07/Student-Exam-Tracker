"""
prediction.py
-------------
AI Prediction blueprint. Lets an admin pick a student to get a live
next-exam-score + pass/fail prediction, and lists all currently
at-risk students using the batch prediction pipeline.
"""

import logging
import pandas as pd

from flask import Blueprint, render_template, request, flash

from routes.decorators import login_required
from models.student import list_students, get_student
from models.marks import list_marks_for_student
from models.subject import list_subjects
from models.db import query_all
from ml.predict import predict_student, predict_batch
from ml.utils import FEATURE_COLUMNS

logger = logging.getLogger(__name__)
prediction_bp = Blueprint("prediction", __name__, url_prefix="/prediction")


@prediction_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    students, _ = list_students(per_page=1000)
    subjects = list_subjects()
    result = None
    selected_student = None
    selected_subject = None

    if request.method == "POST":
        student_id = request.form.get("student_id")
        subject_id = request.form.get("subject_id", type=int)
        selected_student = get_student(student_id) if student_id else None

        marks_rows = list_marks_for_student(student_id) if student_id else []
        row = next((m for m in marks_rows if m["subject_id"] == subject_id), None)

        if not row:
            flash("No marks found for that student/subject combination yet. Enter marks first.", "warning")
        else:
            selected_subject = row["subject_name"]
            features = {
                "Attendance": row["attendance_percentage"],
                "Study_Hours": row["study_hours"],
                "Assignment_Marks": row["assignment_marks"],
                "Quiz_Marks": row["quiz_marks"],
                "Lab_Marks": row["lab_marks"],
                "Internal_Marks": row["internal_marks"],
                "Previous_Semester_Marks": row["previous_semester_marks"],
                "Project_Marks": row["project_marks"],
            }
            try:
                result = predict_student(features)
            except FileNotFoundError as exc:
                flash(str(exc), "danger")

    return render_template(
        "prediction.html", students=students, subjects=subjects, result=result,
        selected_student=selected_student, selected_subject=selected_subject,
    )


@prediction_bp.route("/risk-analysis")
@login_required
def risk_analysis():
    """Batch-predict risk level for every student currently with marks recorded."""
    rows = query_all(
        """
        SELECT m.*, s.name AS student_name, sub.subject_name
        FROM marks m
        JOIN students s ON s.student_id = m.student_id
        JOIN subjects sub ON sub.subject_id = m.subject_id
        """
    )

    at_risk = []
    if rows:
        df = pd.DataFrame(rows)
        rename_map = {
            "attendance_percentage": "Attendance", "study_hours": "Study_Hours",
            "assignment_marks": "Assignment_Marks", "quiz_marks": "Quiz_Marks",
            "lab_marks": "Lab_Marks", "internal_marks": "Internal_Marks",
            "previous_semester_marks": "Previous_Semester_Marks", "project_marks": "Project_Marks",
        }
        df = df.rename(columns=rename_map)
        try:
            predicted = predict_batch(df)
            predicted = predicted.sort_values("Fail_Probability", ascending=False)
            at_risk = predicted[predicted["Risk_Level"].isin(["High", "Medium"])].to_dict("records")
        except FileNotFoundError as exc:
            flash(str(exc), "danger")

    return render_template("risk_analysis.html", at_risk=at_risk)
