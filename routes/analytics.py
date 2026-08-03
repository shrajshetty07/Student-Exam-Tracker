"""
analytics.py
------------
Analytics dashboard blueprint: subject analysis, grade distribution,
pass/fail breakdown, top performers, risk students, and full ML model
evaluation analytics (accuracy, precision, recall, F1, confusion matrix,
ROC curve, feature importance).
"""

from flask import Blueprint, render_template, jsonify

from routes.decorators import login_required
from models.marks import grade_distribution, top_performers, subject_wise_average, dashboard_stats
from models.db import query_all
from ml.utils import load_metrics

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/")
@login_required
def index():
    stats = dashboard_stats()
    grades = grade_distribution()
    top10 = top_performers(10)
    subject_avgs = subject_wise_average()
    metrics = load_metrics()

    semester_comparison = query_all(
        """
        SELECT s.semester, AVG(m.percentage) AS avg_percentage, COUNT(*) AS n
        FROM marks m JOIN students s ON s.student_id = m.student_id
        GROUP BY s.semester ORDER BY s.semester
        """
    )

    pass_fail_counts = query_all(
        "SELECT pass_fail, COUNT(*) AS cnt FROM marks GROUP BY pass_fail"
    )

    return render_template(
        "analytics.html",
        stats=stats,
        grades=grades,
        top10=top10,
        subject_avgs=subject_avgs,
        metrics=metrics,
        semester_comparison=semester_comparison,
        pass_fail_counts=pass_fail_counts,
    )


@analytics_bp.route("/api/metrics")
@login_required
def api_metrics():
    """JSON endpoint used by the analytics page to refresh ML metrics without a reload."""
    return jsonify(load_metrics())
