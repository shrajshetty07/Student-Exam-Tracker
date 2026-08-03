"""
admin.py
--------
Data access functions for admin authentication.
"""

from werkzeug.security import generate_password_hash, check_password_hash

from models.db import query_one, execute


def get_admin_by_username(username: str):
    return query_one("SELECT * FROM admins WHERE username = ?", (username,))


def get_admin_by_id(admin_id: int):
    return query_one("SELECT * FROM admins WHERE admin_id = ?", (admin_id,))


def create_admin(username: str, email: str, password: str, full_name: str, role: str = "admin"):
    password_hash = generate_password_hash(password)
    return execute(
        """INSERT INTO admins (username, email, password_hash, full_name, role)
           VALUES (?, ?, ?, ?, ?)""",
        (username, email, password_hash, full_name, role),
    )


def verify_password(admin_row: dict, password: str) -> bool:
    return check_password_hash(admin_row["password_hash"], password)


def update_last_login(admin_id: int):
    execute("UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE admin_id = ?", (admin_id,))


def update_password(admin_id: int, new_password: str):
    password_hash = generate_password_hash(new_password)
    execute("UPDATE admins SET password_hash = ? WHERE admin_id = ?", (password_hash, admin_id))


def update_profile(admin_id: int, full_name: str, email: str):
    execute("UPDATE admins SET full_name = ?, email = ? WHERE admin_id = ?", (full_name, email, admin_id))
