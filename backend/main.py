import os
from pathlib import Path

# Load environment variables from .env if present
from dotenv import load_dotenv

# Load .env from project root (parent of backend/)
project_root = Path(__file__).parent.parent
# Load .env from repository root (if present)
load_dotenv(project_root / '.env')
# Also load .env from the backend folder (common local dev location)
load_dotenv(Path(__file__).parent / '.env')

# Use relative imports; run the app as a package to ensure imports resolve:
#   from the repository root: `python -m backend.main`
# Relative imports are preferred for intra-package imports and for clearer module
# structure. Avoid running `python main.py` from inside the package directory.
from .app import create_app, register_static_index
from .routes import auth_bp, upload_bp, detect_bp
from .core.cli import register_cli_commands


# Create the Flask app and register routes
app = create_app()

# Configure Supabase (optional) from env or loaded .env files
app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL') or app.config.get('SUPABASE_URL')
# Support either name: SUPABASE_SERVICE_KEY or SUPABASE_SERVICE_ROLE_KEY
app.config['SUPABASE_SERVICE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_SERVICE_ROLE_KEY') or app.config.get('SUPABASE_SERVICE_KEY') or app.config.get('SUPABASE_SERVICE_ROLE_KEY')
app.config['SUPABASE_SERVICE_ROLE_KEY'] = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY') or app.config.get('SUPABASE_SERVICE_ROLE_KEY') or app.config.get('SUPABASE_SERVICE_KEY')
app.config['SUPABASE_BUCKET'] = os.getenv('SUPABASE_BUCKET', app.config.get('SUPABASE_BUCKET', 'uploads'))

# Environment and security
app.config['ENV'] = os.getenv('ENV', 'development')
app.config['TESTING'] = app.config['ENV'] == 'testing'

# CORS configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
app.cors_origins = [origin.strip() for origin in ALLOWED_ORIGINS]
app.config['CORS_ORIGINS'] = app.cors_origins

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(detect_bp)
register_static_index(app)

# Register CLI commands
register_cli_commands(app)


if __name__ == '__main__':
    # Ensure upload directory exists (local fallback)
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    try:
        os.makedirs(upload_folder, exist_ok=True)
    except Exception:
        # Ignore directory creation errors - upload folder is optional
        # when using Supabase storage or if folder already exists
        pass

    # Use debug only in development
    debug_mode = app.config['ENV'] == 'development'
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)
