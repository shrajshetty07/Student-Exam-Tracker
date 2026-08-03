"""
seed_data.py
------------
One-time helper script that loads dataset/student_dataset.csv into the
application database (departments, students, subjects, marks) so the
dashboard, reports and AI prediction pages have realistic data to show
immediately after installation.

Run with:
    python seed_data.py

Safe to re-run: uses INSERT OR IGNORE / upsert semantics under the hood.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from models.db import init_db, execute, query_one
from models.calculations import compute_full_result

DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "student_dataset.csv")

DEPT_SUBJECT_CODE_PREFIX = {
    "Computer Science": "CS", "Information Technology": "IT", "Electronics": "EC",
    "Mechanical": "ME", "Civil": "CE",
}


def get_or_create_department(name: str) -> int:
    row = query_one("SELECT department_id FROM departments WHERE name = ?", (name,))
    if row:
        return row["department_id"]
    return execute("INSERT INTO departments (name) VALUES (?)", (name,))


def get_or_create_subject(name: str, department_id: int, semester: int, code_prefix: str, code_counter: dict) -> int:
    row = query_one("SELECT subject_id FROM subjects WHERE subject_name = ? AND department_id = ?",
                     (name, department_id))
    if row:
        return row["subject_id"]
    code_counter[code_prefix] = code_counter.get(code_prefix, 300) + 1
    code = f"{code_prefix}{code_counter[code_prefix]}"
    return execute(
        "INSERT INTO subjects (subject_name, subject_code, department_id, semester, credits) VALUES (?, ?, ?, ?, 4)",
        (name, code, department_id, semester),
    )


def get_or_create_student(student_id: str, name: str, gender: str, department_id: int, semester: int):
    row = query_one("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
    if row:
        return
    email = f"{name.lower().replace(' ', '.')}@school.edu"
    execute(
        """INSERT INTO students (student_id, name, gender, department_id, semester, email, admission_year)
           VALUES (?, ?, ?, ?, ?, ?, 2023)""",
        (student_id, name, gender, department_id, semester, email),
    )


def seed():
    init_db()
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}. Run gen_dataset.py first.")
        return

    df = pd.read_csv(DATASET_PATH)
    code_counter = {}
    inserted_marks = 0

    for _, row in df.iterrows():
        department_id = get_or_create_department(row["Department"])
        code_prefix = DEPT_SUBJECT_CODE_PREFIX.get(row["Department"], "GEN")
        subject_id = get_or_create_subject(row["Subject"], department_id, int(row["Semester"]), code_prefix, code_counter)
        get_or_create_student(row["Student_ID"], row["Student_Name"], row["Gender"], department_id, int(row["Semester"]))

        existing = query_one(
            "SELECT mark_id FROM marks WHERE student_id = ? AND subject_id = ?",
            (row["Student_ID"], subject_id),
        )
        if existing:
            continue

        result = compute_full_result(
            row["Assignment_Marks"], row["Quiz_Marks"], row["Lab_Marks"],
            row["Internal_Marks"], row["Project_Marks"], row["Final_Exam_Marks"],
        )

        execute(
            """INSERT INTO marks
                (student_id, subject_id, attendance_percentage, study_hours, assignment_marks,
                 quiz_marks, lab_marks, internal_marks, previous_semester_marks, project_marks,
                 final_exam_marks, total_marks, percentage, grade, pass_fail)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                row["Student_ID"], subject_id, row["Attendance"], row["Study_Hours"],
                row["Assignment_Marks"], row["Quiz_Marks"], row["Lab_Marks"], row["Internal_Marks"],
                row["Previous_Semester_Marks"], row["Project_Marks"], row["Final_Exam_Marks"],
                result["total"], result["percentage"], result["grade"], result["pass_fail"],
            ),
        )
        inserted_marks += 1

    print(f"Seed complete. Inserted {inserted_marks} new mark records.")


if __name__ == "__main__":
    seed()
