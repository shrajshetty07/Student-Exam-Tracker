"""
main.py
-------
Core dashboard route and misc top-level pages (settings, 404 handled in app.py).
"""

from flask import Blueprint, render_template

from routes.decorators import login_required
from models.marks import dashboard_stats, grade_distribution, top_performers, subject_wise_average
from models.attendance import overall_attendance_by_department
from ml.utils import load_metrics

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    stats = dashboard_stats()
    grades = grade_distribution()
    top10 = top_performers(10)
    subject_avgs = subject_wise_average()
    attendance_by_dept = overall_attendance_by_department()
    metrics = load_metrics()

    return render_template(
        "dashboard.html",
        stats=stats,
        grades=grades,
        top10=top10,
        subject_avgs=subject_avgs,
        attendance_by_dept=attendance_by_dept,
        metrics=metrics,
    )


@main_bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html")
