"""
marks.py
--------
Data access functions for the marks table. Automatically computes
total, percentage, grade and pass/fail on every insert/update using
models.calculations.
"""

from models.db import query_all, query_one, execute
from models.calculations import compute_full_result


def list_marks_for_student(student_id: str):
    return query_all(
        """
        SELECT m.*, sub.subject_name, sub.subject_code
        FROM marks m
        JOIN subjects sub ON sub.subject_id = m.subject_id
        WHERE m.student_id = ?
        ORDER BY sub.subject_name
        """,
        (student_id,),
    )


def list_all_marks(department_id=None, semester=None, subject_id=None, pass_fail=None):
    where = []
    params = []
    if department_id:
        where.append("s.department_id = ?")
        params.append(department_id)
    if semester:
        where.append("s.semester = ?")
        params.append(semester)
    if subject_id:
        where.append("m.subject_id = ?")
        params.append(subject_id)
    if pass_fail:
        where.append("m.pass_fail = ?")
        params.append(pass_fail)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    return query_all(
        f"""
        SELECT m.*, s.name AS student_name, sub.subject_name
        FROM marks m
        JOIN students s ON s.student_id = m.student_id
        JOIN subjects sub ON sub.subject_id = m.subject_id
        {where_sql}
        ORDER BY m.updated_at DESC
        """,
        tuple(params),
    )


def get_mark(student_id: str, subject_id: int):
    return query_one(
        "SELECT * FROM marks WHERE student_id = ? AND subject_id = ?",
        (student_id, subject_id),
    )


def upsert_marks(student_id: str, subject_id: int, data: dict):
    """Insert or update a mark record, recomputing total/percentage/grade/pass-fail."""
    result = compute_full_result(
        data.get("assignment_marks", 0), data.get("quiz_marks", 0), data.get("lab_marks", 0),
        data.get("internal_marks", 0), data.get("project_marks", 0), data.get("final_exam_marks", 0),
    )

    existing = get_mark(student_id, subject_id)
    if existing:
        execute(
            """
            UPDATE marks
            SET attendance_percentage = ?, study_hours = ?, assignment_marks = ?, quiz_marks = ?,
                lab_marks = ?, internal_marks = ?, previous_semester_marks = ?, project_marks = ?,
                final_exam_marks = ?, total_marks = ?, percentage = ?, grade = ?, pass_fail = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ? AND subject_id = ?
            """,
            (
                data.get("attendance_percentage", 0), data.get("study_hours", 0),
                data.get("assignment_marks", 0), data.get("quiz_marks", 0),
                data.get("lab_marks", 0), data.get("internal_marks", 0),
                data.get("previous_semester_marks", 0), data.get("project_marks", 0),
                data.get("final_exam_marks", 0), result["total"], result["percentage"],
                result["grade"], result["pass_fail"], student_id, subject_id,
            ),
        )
    else:
        execute(
            """
            INSERT INTO marks
                (student_id, subject_id, attendance_percentage, study_hours, assignment_marks,
                 quiz_marks, lab_marks, internal_marks, previous_semester_marks, project_marks,
                 final_exam_marks, total_marks, percentage, grade, pass_fail)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id, subject_id, data.get("attendance_percentage", 0), data.get("study_hours", 0),
                data.get("assignment_marks", 0), data.get("quiz_marks", 0), data.get("lab_marks", 0),
                data.get("internal_marks", 0), data.get("previous_semester_marks", 0),
                data.get("project_marks", 0), data.get("final_exam_marks", 0),
                result["total"], result["percentage"], result["grade"], result["pass_fail"],
            ),
        )
    return result


def delete_mark(student_id: str, subject_id: int):
    execute("DELETE FROM marks WHERE student_id = ? AND subject_id = ?", (student_id, subject_id))


def dashboard_stats():
    """Aggregate stats used on the main dashboard cards."""
    total_students = query_one("SELECT COUNT(*) AS cnt FROM students")["cnt"]
    total_subjects = query_one("SELECT COUNT(*) AS cnt FROM subjects")["cnt"]

    perf = query_one(
        """
        SELECT
            AVG(percentage) AS avg_percentage,
            MAX(percentage) AS highest,
            MIN(percentage) AS lowest,
            SUM(CASE WHEN pass_fail = 'Pass' THEN 1 ELSE 0 END) AS pass_count,
            SUM(CASE WHEN pass_fail = 'Fail' THEN 1 ELSE 0 END) AS fail_count,
            COUNT(*) AS total_records
        FROM marks
        """
    )

    avg_attendance = query_one("SELECT AVG(attendance_percentage) AS avg_att FROM marks")

    pass_pct = 0
    if perf["total_records"]:
        pass_pct = round(perf["pass_count"] / perf["total_records"] * 100, 2)

    return {
        "total_students": total_students,
        "total_subjects": total_subjects,
        "avg_percentage": round(perf["avg_percentage"] or 0, 2),
        "highest_score": round(perf["highest"] or 0, 2),
        "lowest_score": round(perf["lowest"] or 0, 2),
        "pass_percentage": pass_pct,
        "failed_students": perf["fail_count"] or 0,
        "avg_attendance": round(avg_attendance["avg_att"] or 0, 2),
        "total_mark_records": perf["total_records"] or 0,
    }


def grade_distribution():
    rows = query_all(
        "SELECT grade, COUNT(*) AS cnt FROM marks GROUP BY grade ORDER BY grade"
    )
    return rows


def top_performers(limit: int = 10):
    return query_all(
        """
        SELECT s.student_id, s.name, AVG(m.percentage) AS avg_percentage
        FROM marks m
        JOIN students s ON s.student_id = m.student_id
        GROUP BY s.student_id, s.name
        ORDER BY avg_percentage DESC
        LIMIT ?
        """,
        (limit,),
    )


def subject_wise_average():
    return query_all(
        """
        SELECT sub.subject_name, AVG(m.percentage) AS avg_percentage, COUNT(*) AS n
        FROM marks m
        JOIN subjects sub ON sub.subject_id = m.subject_id
        GROUP BY sub.subject_name
        ORDER BY avg_percentage DESC
        """
    )
