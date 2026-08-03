"""
reports.py
----------
Reporting blueprint. Generates:
    * Individual student report cards (HTML view + PDF download)
    * Semester report (all students, HTML + CSV/Excel export)
    * Attendance report
    * Top performers report
    * Subject-wise analysis report

Export formats: PDF (reportlab), CSV (pandas), Excel (openpyxl via pandas).
"""

import io
import logging
from datetime import datetime

import pandas as pd
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from routes.decorators import login_required
from models.student import get_student, list_students, get_all_departments
from models.marks import list_marks_for_student, list_all_marks, top_performers, subject_wise_average
from models.calculations import compute_ranks

logger = logging.getLogger(__name__)
reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@login_required
def index():
    students, _ = list_students(per_page=1000)
    departments = get_all_departments()
    return render_template("reports.html", students=students, departments=departments)


# ------------------------------------------------------------------
# Student Report Card
# ------------------------------------------------------------------
@reports_bp.route("/report-card/<student_id>")
@login_required
def report_card(student_id):
    student = get_student(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("reports.index"))
    marks = list_marks_for_student(student_id)

    overall_percentage = round(sum(m["percentage"] for m in marks) / len(marks), 2) if marks else 0
    overall_result = "Pass" if all(m["pass_fail"] == "Pass" for m in marks) and marks else "Fail"

    return render_template(
        "report_card.html", student=student, marks=marks,
        overall_percentage=overall_percentage, overall_result=overall_result,
        generated_on=datetime.now().strftime("%d %B %Y"),
    )


@reports_bp.route("/report-card/<student_id>/pdf")
@login_required
def report_card_pdf(student_id):
    student = get_student(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("reports.index"))
    marks = list_marks_for_student(student_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#4f46e5"))

    elements = [
        Paragraph("AI-Powered Student Exam Performance Tracker", title_style),
        Paragraph("Official Student Report Card", styles["Heading2"]),
        Spacer(1, 12),
        Paragraph(f"<b>Student:</b> {student['name']} ({student['student_id']})", styles["Normal"]),
        Paragraph(f"<b>Department:</b> {student['department_name']} &nbsp;&nbsp; "
                   f"<b>Semester:</b> {student['semester']}", styles["Normal"]),
        Spacer(1, 16),
    ]

    table_data = [["Subject", "Assign.", "Quiz", "Lab", "Internal", "Project", "Final", "Total", "%", "Grade", "Result"]]
    for m in marks:
        table_data.append([
            m["subject_name"], m["assignment_marks"], m["quiz_marks"], m["lab_marks"],
            m["internal_marks"], m["project_marks"], m["final_exam_marks"],
            m["total_marks"], f"{m['percentage']}%", m["grade"], m["pass_fail"],
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    overall_percentage = round(sum(m["percentage"] for m in marks) / len(marks), 2) if marks else 0
    overall_result = "Pass" if all(m["pass_fail"] == "Pass" for m in marks) and marks else "Fail"
    elements.append(Paragraph(f"<b>Overall Percentage:</b> {overall_percentage}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>Overall Result:</b> {overall_result}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles["Italic"]))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True,
                      download_name=f"report_card_{student_id}.pdf")


# ------------------------------------------------------------------
# Semester Report (all students)
# ------------------------------------------------------------------
@reports_bp.route("/semester")
@login_required
def semester_report():
    department_id = request.args.get("department_id", type=int)
    semester = request.args.get("semester", type=int)
    rows = list_all_marks(department_id=department_id, semester=semester)
    departments = get_all_departments()
    return render_template("semester_report.html", marks=rows, departments=departments,
                            department_id=department_id, semester=semester)


@reports_bp.route("/semester/export/<fmt>")
@login_required
def semester_report_export(fmt):
    department_id = request.args.get("department_id", type=int)
    semester = request.args.get("semester", type=int)
    rows = list_all_marks(department_id=department_id, semester=semester)
    df = pd.DataFrame(rows)
    return _export_dataframe(df, "semester_report", fmt)


# ------------------------------------------------------------------
# Top Performers Report
# ------------------------------------------------------------------
@reports_bp.route("/top-performers")
@login_required
def top_performers_report():
    limit = request.args.get("limit", 10, type=int)
    rows = top_performers(limit)
    ranked = compute_ranks([{"student_id": r["student_id"], "name": r["name"],
                              "percentage": round(r["avg_percentage"], 2)} for r in rows])
    return render_template("top_performers.html", rows=ranked)


# ------------------------------------------------------------------
# Subject Analysis Report
# ------------------------------------------------------------------
@reports_bp.route("/subject-analysis")
@login_required
def subject_analysis():
    rows = subject_wise_average()
    return render_template("subject_analysis.html", rows=rows)


# ------------------------------------------------------------------
# Attendance Report
# ------------------------------------------------------------------
@reports_bp.route("/attendance")
@login_required
def attendance_report():
    from models.attendance import overall_attendance_by_department
    rows = overall_attendance_by_department()
    return render_template("attendance_report.html", rows=rows)


# ------------------------------------------------------------------
# Generic CSV/Excel export helper
# ------------------------------------------------------------------
def _export_dataframe(df: pd.DataFrame, filename: str, fmt: str):
    buffer = io.BytesIO()
    if fmt == "csv":
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(buffer, mimetype="text/csv", as_attachment=True,
                          download_name=f"{filename}.csv")
    elif fmt == "excel":
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Report")
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True, download_name=f"{filename}.xlsx",
        )
    else:
        flash("Unsupported export format.", "danger")
        return redirect(url_for("reports.index"))
