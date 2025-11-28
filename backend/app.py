import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from .core.models import db


def create_app(static_folder: str = "../plantviewFrontend/dist", static_url_path: str = "/"):
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=static_folder, static_url_path=static_url_path)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:password@localhost:5432/plantview_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = os.getenv('DB_ECHO', 'false').lower() == 'true'

    # Basic configuration
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '../uploads')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
    app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', '1'))
    app.config['JWT_REFRESH_EXPIRATION_HOURS'] = int(os.getenv('JWT_REFRESH_EXPIRATION_HOURS', '168'))

    # Get allowed origins from environment or default values.
    allowed_origins_env = os.getenv('ALLOWED_ORIGINS')
    if allowed_origins_env:
        allowed_origins = [o.strip() for o in allowed_origins_env.split(',') if o.strip()]
    else:
        allowed_origins = [
            'http://localhost:5173',
            'http://localhost:3000',
            'http://127.0.0.1:5173',
            'http://127.0.0.1:3000'
        ]

    # CORS: Allow specified origins for API endpoints. Include both
    # lowercase and uppercase `/api/*` to tolerate frontend inconsistencies.
    CORS(
        app,
        resources={
            r"/api/*": {"origins": allowed_origins},
            r"/API/*": {"origins": allowed_origins},
        },
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
        methods=["GET", "POST", "OPTIONS"]
    )

    # Initialize database and migrations
    db.init_app(app)
    Migrate(app, db)

    return app


def register_static_index(app):
    """Attach a simple index route to serve the frontend entrypoint."""

    @app.route('/')
    def home():
        return send_from_directory(app.static_folder, "index.html")
