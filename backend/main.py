import os
# Load environment variables from .env if present
from dotenv import load_dotenv
load_dotenv()

# Use relative imports; run the app as a package to ensure imports resolve:
#   from the repository root: `python -m backend.main`
# Relative imports are preferred for intra-package imports and for clearer module
# structure. Avoid running `python main.py` from inside the package directory.
from .app import create_app, register_static_index
from .routes import auth_bp, upload_bp, limiter


# Create the Flask app and register routes
app = create_app()

# Configure security and auth settings
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', '1'))
app.config['JWT_REFRESH_EXPIRATION_HOURS'] = int(os.getenv('JWT_REFRESH_EXPIRATION_HOURS', '168'))

# Configure Supabase (optional)
app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
app.config['SUPABASE_SERVICE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY')
app.config['SUPABASE_BUCKET'] = os.getenv('SUPABASE_BUCKET', 'uploads')

# Environment and security
app.config['ENV'] = os.getenv('ENV', 'development')
app.config['TESTING'] = app.config['ENV'] == 'testing'

# CORS configuration - set before rate limiter
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
app.cors_origins = [origin.strip() for origin in ALLOWED_ORIGINS]
app.config['CORS_ORIGINS'] = app.cors_origins

# Initialize rate limiter with the app
if os.getenv('ENV') != 'testing':
    limiter.init_app(app)
else:
    # In testing mode, disable rate limiting
    app.config['RATELIMIT_ENABLED'] = False

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(upload_bp)
register_static_index(app)


if __name__ == '__main__':
    # Ensure upload directory exists (local fallback)
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    try:
        os.makedirs(upload_folder, exist_ok=True)
    except Exception:
        pass

    # Use debug only in development
    debug_mode = app.config['ENV'] == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)