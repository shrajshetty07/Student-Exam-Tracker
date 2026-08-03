"""
attendance.py
-------------
Data access functions for monthly attendance logging (separate from the
per-subject attendance_percentage snapshot stored in marks).
"""

from models.db import query_all, query_one, execute


def list_attendance_for_student(student_id: str):
    return query_all(
        """
        SELECT a.*, sub.subject_name
        FROM attendance a
        JOIN subjects sub ON sub.subject_id = a.subject_id
        WHERE a.student_id = ?
        ORDER BY a.year DESC,
                 CASE a.month
                    WHEN 'January' THEN 1 WHEN 'February' THEN 2 WHEN 'March' THEN 3
                    WHEN 'April' THEN 4 WHEN 'May' THEN 5 WHEN 'June' THEN 6
                    WHEN 'July' THEN 7 WHEN 'August' THEN 8 WHEN 'September' THEN 9
                    WHEN 'October' THEN 10 WHEN 'November' THEN 11 WHEN 'December' THEN 12
                 END DESC
        """,
        (student_id,),
    )


def add_or_update_attendance(student_id: str, subject_id: int, month: str, year: int,
                              classes_held: int, classes_attended: int):
    percentage = round((classes_attended / classes_held * 100) if classes_held else 0, 2)
    existing = query_one(
        "SELECT attendance_id FROM attendance WHERE student_id=? AND subject_id=? AND month=? AND year=?",
        (student_id, subject_id, month, year),
    )
    if existing:
        execute(
            """UPDATE attendance SET classes_held=?, classes_attended=?, percentage=?
               WHERE attendance_id=?""",
            (classes_held, classes_attended, percentage, existing["attendance_id"]),
        )
    else:
        execute(
            """INSERT INTO attendance (student_id, subject_id, month, year, classes_held,
                                        classes_attended, percentage)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (student_id, subject_id, month, year, classes_held, classes_attended, percentage),
        )
    return percentage


def delete_attendance(attendance_id: int):
    execute("DELETE FROM attendance WHERE attendance_id = ?", (attendance_id,))


def overall_attendance_by_department():
    return query_all(
        """
        SELECT d.name AS department_name, AVG(a.percentage) AS avg_attendance
        FROM attendance a
        JOIN students s ON s.student_id = a.student_id
        JOIN departments d ON d.department_id = s.department_id
        GROUP BY d.name
        """
    )
