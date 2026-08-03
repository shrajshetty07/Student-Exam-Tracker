"""
students.py
-----------
Student management blueprint: list (search/filter/pagination), add, edit, delete.
"""

import math
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash

from routes.decorators import login_required
from models.student import (
    list_students, get_student, create_student, update_student, delete_student,
    student_exists, get_all_departments, create_department_if_missing, generate_next_student_id,
)
from models.marks import list_marks_for_student
from models.attendance import list_attendance_for_student

logger = logging.getLogger(__name__)
students_bp = Blueprint("students", __name__, url_prefix="/students")


@students_bp.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip()
    department_id = request.args.get("department_id", type=int)
    semester = request.args.get("semester", type=int)
    page = max(1, request.args.get("page", 1, type=int))
    per_page = 10

    rows, total = list_students(search, department_id, semester, page, per_page)
    total_pages = max(1, math.ceil(total / per_page))
    departments = get_all_departments()

    return render_template(
        "students.html",
        students=rows,
        departments=departments,
        search=search,
        department_id=department_id,
        semester=semester,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@students_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    departments = get_all_departments()

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip() or generate_next_student_id()
        name = request.form.get("name", "").strip()
        gender = request.form.get("gender", "")
        department_name = request.form.get("department_name", "").strip()
        semester = request.form.get("semester", type=int)
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("date_of_birth", "")
        admission_year = request.form.get("admission_year", type=int)

        errors = []
        if not name:
            errors.append("Student name is required.")
        if gender not in ("Male", "Female", "Other"):
            errors.append("Please select a valid gender.")
        if not department_name:
            errors.append("Department is required.")
        if not semester or not (1 <= semester <= 8):
            errors.append("Semester must be between 1 and 8.")
        if student_exists(student_id):
            errors.append(f"Student ID {student_id} already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("add_student.html", departments=departments, form=request.form)

        department_id = create_department_if_missing(department_name)
        create_student({
            "student_id": student_id, "name": name, "gender": gender,
            "department_id": department_id, "semester": semester,
            "email": email, "phone": phone, "date_of_birth": dob,
            "admission_year": admission_year,
        })
        logger.info("Created student %s (%s)", student_id, name)
        flash(f"Student {name} added successfully.", "success")
        return redirect(url_for("students.index"))

    return render_template("add_student.html", departments=departments, form={})


@students_bp.route("/<student_id>/edit", methods=["GET", "POST"])
@login_required
def edit(student_id):
    student = get_student(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("students.index"))

    departments = get_all_departments()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        gender = request.form.get("gender", "")
        department_name = request.form.get("department_name", "").strip()
        semester = request.form.get("semester", type=int)
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("date_of_birth", "")
        admission_year = request.form.get("admission_year", type=int)

        errors = []
        if not name:
            errors.append("Student name is required.")
        if not semester or not (1 <= semester <= 8):
            errors.append("Semester must be between 1 and 8.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("edit_student.html", student=student, departments=departments)

        department_id = create_department_if_missing(department_name)
        update_student(student_id, {
            "name": name, "gender": gender, "department_id": department_id,
            "semester": semester, "email": email, "phone": phone,
            "date_of_birth": dob, "admission_year": admission_year,
        })
        logger.info("Updated student %s", student_id)
        flash("Student updated successfully.", "success")
        return redirect(url_for("students.index"))

    return render_template("edit_student.html", student=student, departments=departments)


@students_bp.route("/<student_id>/delete", methods=["POST"])
@login_required
def delete(student_id):
    student = get_student(student_id)
    if student:
        delete_student(student_id)
        logger.info("Deleted student %s", student_id)
        flash(f"Student {student['name']} deleted.", "success")
    return redirect(url_for("students.index"))


@students_bp.route("/<student_id>/profile")
@login_required
def view_profile(student_id):
    student = get_student(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("students.index"))
    marks = list_marks_for_student(student_id)
    attendance = list_attendance_for_student(student_id)
    return render_template("student_profile.html", student=student, marks=marks, attendance=attendance)
