import os
from flask import Flask, send_from_directory
from flask_cors import CORS


def create_app(static_folder: str = "../plantviewFrontend/dist", static_url_path: str = "/"):
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=static_folder, static_url_path=static_url_path)

    # Basic configuration
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '../uploads')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
    app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

    # CORS: allow /api/* endpoints (dev-friendly). Adjust in production.
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
    )

    return app


def register_static_index(app):
    """Attach a simple index route to serve the frontend entrypoint."""

    @app.route('/')
    def home():
        return send_from_directory(app.static_folder, "index.html")
