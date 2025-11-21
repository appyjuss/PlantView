import os

# Use relative imports; run the app as a package to ensure imports resolve:
#   from the repository root: `python -m backend.main`
# Relative imports are preferred for intra-package imports and for clearer module
# structure. Avoid running `python main.py` from inside the package directory.
from .app import create_app, register_static_index
from .routes import auth_bp, upload_bp


# Create the Flask app and register routes
app = create_app()
app.register_blueprint(auth_bp)
app.register_blueprint(upload_bp)
register_static_index(app)


if __name__ == '__main__':
    # Ensure upload directory exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception:
        pass

    # Run the Flask development server
    # In production, use a proper WSGI server (gunicorn / waitress etc.)
    app.run(host='0.0.0.0', port=5000, debug=True)