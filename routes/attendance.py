"""
attendance.py
-------------
Attendance module blueprint: add monthly attendance, view attendance percentage.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash

from routes.decorators import login_required
from models.attendance import add_or_update_attendance, overall_attendance_by_department
from models.student import list_students
from models.subject import list_subjects

logger = logging.getLogger(__name__)
attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


@attendance_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    students, _ = list_students(per_page=1000)
    subjects = list_subjects()

    if request.method == "POST":
        student_id = request.form.get("student_id")
        subject_id = request.form.get("subject_id", type=int)
        month = request.form.get("month")
        year = request.form.get("year", type=int)
        classes_held = request.form.get("classes_held", 0, type=int)
        classes_attended = request.form.get("classes_attended", 0, type=int)

        if not all([student_id, subject_id, month, year]):
            flash("All fields are required.", "danger")
        elif classes_attended > classes_held:
            flash("Classes attended cannot exceed classes held.", "danger")
        else:
            pct = add_or_update_attendance(student_id, subject_id, month, year, classes_held, classes_attended)
            flash(f"Attendance saved: {pct}%", "success")
        return redirect(url_for("attendance.index"))

    by_department = overall_attendance_by_department()
    return render_template(
        "attendance.html", students=students, subjects=subjects, months=MONTHS,
        by_department=by_department,
    )
