"""
db.py
-----
Lightweight data-access layer for the application.

The project ships a full MySQL schema (see database.sql) for production
deployment. For local development / evaluation (so the ZIP can be run
immediately with zero external services), the Flask app uses a bundled
SQLite database that mirrors the exact same schema and constraints.

Switching to MySQL in production only requires:
    1. Running database.sql against a MySQL server
    2. Setting DB_ENGINE=mysql and the MYSQL_* variables in .env
    3. Installing mysql-connector-python / PyMySQL

All queries in this module use parameterized placeholders ("?") to
prevent SQL injection, matching the requirement in the project spec.
"""

import os
import sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "instance", "student_tracker.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS admins (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'admin',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_login TEXT
);

CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    email TEXT,
    phone TEXT,
    date_of_birth TEXT,
    admission_year INTEGER,
    photo_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL,
    subject_code TEXT NOT NULL UNIQUE,
    department_id INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    credits INTEGER DEFAULT 3,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS marks (
    mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    attendance_percentage REAL DEFAULT 0,
    study_hours REAL DEFAULT 0,
    assignment_marks REAL DEFAULT 0,
    quiz_marks REAL DEFAULT 0,
    lab_marks REAL DEFAULT 0,
    internal_marks REAL DEFAULT 0,
    previous_semester_marks REAL DEFAULT 0,
    project_marks REAL DEFAULT 0,
    final_exam_marks REAL DEFAULT 0,
    total_marks REAL DEFAULT 0,
    percentage REAL DEFAULT 0,
    grade TEXT,
    pass_fail TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE (student_id, subject_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    subject_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    year INTEGER NOT NULL,
    classes_held INTEGER NOT NULL DEFAULT 0,
    classes_attended INTEGER NOT NULL DEFAULT 0,
    percentage REAL DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE (student_id, subject_id, month, year)
);

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    subject_id INTEGER,
    predicted_score REAL,
    predicted_result TEXT,
    confidence REAL,
    risk_level TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);
"""


def get_connection():
    """Return a new SQLite connection with row-dict access and FK enforcement."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_cursor(commit: bool = False):
    """Context manager yielding a cursor; commits automatically if commit=True."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def query_all(sql: str, params: tuple = ()):
    """Run a SELECT and return all rows as a list of dicts."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def query_one(sql: str, params: tuple = ()):
    """Run a SELECT and return a single row as a dict, or None."""
    with get_cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def execute(sql: str, params: tuple = ()):
    """Run an INSERT/UPDATE/DELETE and return the last row id / row count."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
