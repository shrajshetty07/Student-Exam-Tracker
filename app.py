"""
app.py
------
Application entry point. Creates the Flask app, registers blueprints,
initializes the database, seeds a default admin account, and starts
the development server.

Run with:
    python app.py
"""

import os
import logging

from flask import Flask, render_template

from config import config_map
from models.db import init_db
from models.admin import get_admin_by_username, create_admin


def create_app(env: str = None):
    env = env or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map.get(env, config_map["default"]))

    _configure_logging(app)

    with app.app_context():
        init_db()
        seed_default_admin(app)

    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context_processors(app)

    return app


def _configure_logging(app):
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "app.log")),
            logging.StreamHandler(),
        ],
    )


def seed_default_admin(app):
    """Create the default admin account on first run, using a securely hashed password."""
    username = app.config["DEFAULT_ADMIN_USERNAME"]
    if not get_admin_by_username(username):
        create_admin(
            username=username,
            email=app.config["DEFAULT_ADMIN_EMAIL"],
            password=app.config["DEFAULT_ADMIN_PASSWORD"],
            full_name="System Administrator",
            role="admin",
        )
        logging.getLogger(__name__).info(
            "Seeded default admin account '%s'. Change the password after first login!", username
        )


def _register_blueprints(app):
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.students import students_bp
    from routes.subjects import subjects_bp
    from routes.marks import marks_bp
    from routes.attendance import attendance_bp
    from routes.reports import reports_bp
    from routes.analytics import analytics_bp
    from routes.prediction import prediction_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(prediction_bp)


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        logging.getLogger(__name__).exception("Internal server error")
        return render_template("404.html", server_error=True), 500


def _register_context_processors(app):
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {"current_year": datetime.now().year, "app_name": "EduTrack AI"}


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))
