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
    app.config['JWT_REFRESH_EXPIRATION_HOURS'] = int(os.getenv('JWT_REFRESH_EXPIRATION_HOURS', '168'))

    # Get allowed origins from config (set in main.py) or use defaults for development
    allowed_origins = getattr(app, 'cors_origins', None) or [
        'http://localhost:5173',
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000'
    ]

    # CORS: Allow specified origins for /api/* endpoints
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
        methods=["GET", "POST", "OPTIONS"]
    )

    return app


def register_static_index(app):
    """Attach a simple index route to serve the frontend entrypoint."""

    @app.route('/')
    def home():
        return send_from_directory(app.static_folder, "index.html")
