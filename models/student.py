"""
student.py
----------
Data access functions for the students table (CRUD + search/filter/pagination).
"""

from models.db import query_all, query_one, execute


def get_all_departments():
    return query_all("SELECT * FROM departments ORDER BY name")


def get_department_id_by_name(name: str):
    row = query_one("SELECT department_id FROM departments WHERE name = ?", (name,))
    return row["department_id"] if row else None


def create_department_if_missing(name: str) -> int:
    dept_id = get_department_id_by_name(name)
    if dept_id:
        return dept_id
    return execute("INSERT INTO departments (name) VALUES (?)", (name,))


def list_students(search: str = "", department_id=None, semester=None, page: int = 1, per_page: int = 10):
    """Return (rows, total_count) applying search/filter/pagination."""
    where_clauses = []
    params = []

    if search:
        where_clauses.append("(s.name LIKE ? OR s.student_id LIKE ? OR s.email LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like])

    if department_id:
        where_clauses.append("s.department_id = ?")
        params.append(department_id)

    if semester:
        where_clauses.append("s.semester = ?")
        params.append(semester)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    count_sql = f"""
        SELECT COUNT(*) AS cnt FROM students s {where_sql}
    """
    total = query_one(count_sql, tuple(params))["cnt"]

    offset = (page - 1) * per_page
    data_sql = f"""
        SELECT s.*, d.name AS department_name
        FROM students s
        JOIN departments d ON d.department_id = s.department_id
        {where_sql}
        ORDER BY s.created_at DESC
        LIMIT ? OFFSET ?
    """
    rows = query_all(data_sql, tuple(params) + (per_page, offset))
    return rows, total


def get_student(student_id: str):
    return query_one(
        """
        SELECT s.*, d.name AS department_name
        FROM students s
        JOIN departments d ON d.department_id = s.department_id
        WHERE s.student_id = ?
        """,
        (student_id,),
    )


def student_exists(student_id: str) -> bool:
    return get_student(student_id) is not None


def create_student(data: dict):
    execute(
        """
        INSERT INTO students
            (student_id, name, gender, department_id, semester, email, phone,
             date_of_birth, admission_year, photo_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["student_id"], data["name"], data["gender"], data["department_id"],
            data["semester"], data.get("email"), data.get("phone"),
            data.get("date_of_birth"), data.get("admission_year"), data.get("photo_url"),
        ),
    )


def update_student(student_id: str, data: dict):
    execute(
        """
        UPDATE students
        SET name = ?, gender = ?, department_id = ?, semester = ?, email = ?,
            phone = ?, date_of_birth = ?, admission_year = ?, photo_url = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE student_id = ?
        """,
        (
            data["name"], data["gender"], data["department_id"], data["semester"],
            data.get("email"), data.get("phone"), data.get("date_of_birth"),
            data.get("admission_year"), data.get("photo_url"), student_id,
        ),
    )


def delete_student(student_id: str):
    execute("DELETE FROM students WHERE student_id = ?", (student_id,))


def count_students() -> int:
    return query_one("SELECT COUNT(*) AS cnt FROM students")["cnt"]


def generate_next_student_id() -> str:
    row = query_one("SELECT student_id FROM students ORDER BY student_id DESC LIMIT 1")
    if not row:
        return "STU1001"
    try:
        num = int(row["student_id"].replace("STU", "")) + 1
    except ValueError:
        num = 1001
    return f"STU{num}"
