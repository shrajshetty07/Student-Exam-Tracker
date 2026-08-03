"""
subjects.py
-----------
Subject management blueprint: list, add, edit, delete.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash

from routes.decorators import login_required
from models.subject import list_subjects, get_subject, create_subject, update_subject, delete_subject
from models.student import get_all_departments, create_department_if_missing

logger = logging.getLogger(__name__)
subjects_bp = Blueprint("subjects", __name__, url_prefix="/subjects")


@subjects_bp.route("/")
@login_required
def index():
    department_id = request.args.get("department_id", type=int)
    semester = request.args.get("semester", type=int)
    subjects = list_subjects(department_id, semester)
    departments = get_all_departments()
    return render_template("subjects.html", subjects=subjects, departments=departments,
                            department_id=department_id, semester=semester)


@subjects_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    departments = get_all_departments()
    if request.method == "POST":
        subject_name = request.form.get("subject_name", "").strip()
        subject_code = request.form.get("subject_code", "").strip()
        department_name = request.form.get("department_name", "").strip()
        semester = request.form.get("semester", type=int)
        credits = request.form.get("credits", 3, type=int)

        errors = []
        if not subject_name:
            errors.append("Subject name is required.")
        if not subject_code:
            errors.append("Subject code is required.")
        if not department_name:
            errors.append("Department is required.")
        if not semester or not (1 <= semester <= 8):
            errors.append("Semester must be between 1 and 8.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("add_subject.html", departments=departments, form=request.form)

        department_id = create_department_if_missing(department_name)
        try:
            create_subject({
                "subject_name": subject_name, "subject_code": subject_code,
                "department_id": department_id, "semester": semester, "credits": credits,
            })
        except Exception as exc:
            logger.exception("Failed to create subject")
            flash(f"Could not create subject (duplicate code?): {exc}", "danger")
            return render_template("add_subject.html", departments=departments, form=request.form)

        flash(f"Subject {subject_name} added successfully.", "success")
        return redirect(url_for("subjects.index"))

    return render_template("add_subject.html", departments=departments, form={})


@subjects_bp.route("/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
def edit(subject_id):
    subject = get_subject(subject_id)
    if not subject:
        flash("Subject not found.", "danger")
        return redirect(url_for("subjects.index"))
    departments = get_all_departments()

    if request.method == "POST":
        subject_name = request.form.get("subject_name", "").strip()
        subject_code = request.form.get("subject_code", "").strip()
        department_name = request.form.get("department_name", "").strip()
        semester = request.form.get("semester", type=int)
        credits = request.form.get("credits", 3, type=int)

        department_id = create_department_if_missing(department_name)
        update_subject(subject_id, {
            "subject_name": subject_name, "subject_code": subject_code,
            "department_id": department_id, "semester": semester, "credits": credits,
        })
        flash("Subject updated successfully.", "success")
        return redirect(url_for("subjects.index"))

    return render_template("edit_subject.html", subject=subject, departments=departments)


@subjects_bp.route("/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete(subject_id):
    subject = get_subject(subject_id)
    if subject:
        delete_subject(subject_id)
        flash(f"Subject {subject['subject_name']} deleted.", "success")
    return redirect(url_for("subjects.index"))
