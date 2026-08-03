"""
subject.py
----------
Data access functions for the subjects table.
"""

from models.db import query_all, query_one, execute


def list_subjects(department_id=None, semester=None):
    where = []
    params = []
    if department_id:
        where.append("sub.department_id = ?")
        params.append(department_id)
    if semester:
        where.append("sub.semester = ?")
        params.append(semester)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    return query_all(
        f"""
        SELECT sub.*, d.name AS department_name
        FROM subjects sub
        JOIN departments d ON d.department_id = sub.department_id
        {where_sql}
        ORDER BY sub.semester, sub.subject_name
        """,
        tuple(params),
    )


def get_subject(subject_id: int):
    return query_one(
        """
        SELECT sub.*, d.name AS department_name
        FROM subjects sub
        JOIN departments d ON d.department_id = sub.department_id
        WHERE sub.subject_id = ?
        """,
        (subject_id,),
    )


def create_subject(data: dict):
    return execute(
        """
        INSERT INTO subjects (subject_name, subject_code, department_id, semester, credits)
        VALUES (?, ?, ?, ?, ?)
        """,
        (data["subject_name"], data["subject_code"], data["department_id"],
         data["semester"], data.get("credits", 3)),
    )


def update_subject(subject_id: int, data: dict):
    execute(
        """
        UPDATE subjects
        SET subject_name = ?, subject_code = ?, department_id = ?, semester = ?, credits = ?
        WHERE subject_id = ?
        """,
        (data["subject_name"], data["subject_code"], data["department_id"],
         data["semester"], data.get("credits", 3), subject_id),
    )


def delete_subject(subject_id: int):
    execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id,))


def count_subjects() -> int:
    return query_one("SELECT COUNT(*) AS cnt FROM subjects")["cnt"]
