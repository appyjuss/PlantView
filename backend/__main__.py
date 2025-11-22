"""Entry point for running the backend as a module."""
from .main import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
