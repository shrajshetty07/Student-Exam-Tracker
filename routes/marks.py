"""
marks.py
--------
Marks management blueprint: view all marks (with filters), enter/update
marks for a student+subject (auto-calculates total/percentage/grade/GPA/pass-fail).
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash

from routes.decorators import login_required
from models.marks import list_all_marks, upsert_marks, delete_mark
from models.student import list_students, get_all_departments, get_student
from models.subject import list_subjects, get_subject

logger = logging.getLogger(__name__)
marks_bp = Blueprint("marks", __name__, url_prefix="/marks")


@marks_bp.route("/")
@login_required
def index():
    department_id = request.args.get("department_id", type=int)
    semester = request.args.get("semester", type=int)
    subject_id = request.args.get("subject_id", type=int)
    pass_fail = request.args.get("pass_fail") or None

    rows = list_all_marks(department_id, semester, subject_id, pass_fail)
    departments = get_all_departments()
    subjects = list_subjects()

    return render_template(
        "marks.html", marks=rows, departments=departments, subjects=subjects,
        department_id=department_id, semester=semester, subject_id=subject_id, pass_fail=pass_fail,
    )


@marks_bp.route("/entry", methods=["GET", "POST"])
@login_required
def entry():
    students, _ = list_students(per_page=1000)
    subjects = list_subjects()

    if request.method == "POST":
        student_id = request.form.get("student_id")
        subject_id = request.form.get("subject_id", type=int)

        if not student_id or not subject_id:
            flash("Please select both a student and a subject.", "danger")
            return render_template("marks_entry.html", students=students, subjects=subjects)

        data = {
            "attendance_percentage": request.form.get("attendance_percentage", 0, type=float),
            "study_hours": request.form.get("study_hours", 0, type=float),
            "assignment_marks": request.form.get("assignment_marks", 0, type=float),
            "quiz_marks": request.form.get("quiz_marks", 0, type=float),
            "lab_marks": request.form.get("lab_marks", 0, type=float),
            "internal_marks": request.form.get("internal_marks", 0, type=float),
            "previous_semester_marks": request.form.get("previous_semester_marks", 0, type=float),
            "project_marks": request.form.get("project_marks", 0, type=float),
            "final_exam_marks": request.form.get("final_exam_marks", 0, type=float),
        }

        result = upsert_marks(student_id, subject_id, data)
        logger.info("Marks saved for %s / subject %s -> %s", student_id, subject_id, result)
        flash(
            f"Marks saved. Total: {result['total']}/130, Percentage: {result['percentage']}%, "
            f"Grade: {result['grade']}, Result: {result['pass_fail']}", "success"
        )
        return redirect(url_for("marks.index"))

    return render_template("marks_entry.html", students=students, subjects=subjects)


@marks_bp.route("/<student_id>/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete(student_id, subject_id):
    delete_mark(student_id, subject_id)
    flash("Mark record deleted.", "success")
    return redirect(url_for("marks.index"))
