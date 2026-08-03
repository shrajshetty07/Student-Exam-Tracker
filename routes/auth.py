"""
auth.py
-------
Authentication blueprint: login, logout and profile/password management.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.admin import get_admin_by_username, verify_password, update_last_login, get_admin_by_id, update_password, update_profile
from routes.decorators import login_required

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "admin_id" in session:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("login.html")

        admin = get_admin_by_username(username)
        if admin and verify_password(admin, password):
            session.permanent = True
            session["admin_id"] = admin["admin_id"]
            session["admin_name"] = admin["full_name"]
            session["admin_role"] = admin["role"]
            update_last_login(admin["admin_id"])
            logger.info("Admin '%s' logged in", username)
            flash(f"Welcome back, {admin['full_name']}!", "success")
            next_url = request.args.get("next") or url_for("main.dashboard")
            return redirect(next_url)

        logger.warning("Failed login attempt for username '%s'", username)
        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    admin = get_admin_by_id(session["admin_id"])

    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_profile":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            if full_name and email:
                update_profile(admin["admin_id"], full_name, email)
                session["admin_name"] = full_name
                flash("Profile updated successfully.", "success")
            else:
                flash("Name and email are required.", "danger")
        elif action == "change_password":
            current = request.form.get("current_password", "")
            new = request.form.get("new_password", "")
            confirm = request.form.get("confirm_password", "")
            if not verify_password(admin, current):
                flash("Current password is incorrect.", "danger")
            elif len(new) < 6:
                flash("New password must be at least 6 characters.", "danger")
            elif new != confirm:
                flash("New passwords do not match.", "danger")
            else:
                update_password(admin["admin_id"], new)
                flash("Password changed successfully.", "success")
        return redirect(url_for("auth.profile"))

    admin = get_admin_by_id(session["admin_id"])
    return render_template("profile.html", admin=admin)
