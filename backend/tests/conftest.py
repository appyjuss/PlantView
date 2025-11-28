"""
Test configuration for PlantView authentication tests.
Sets up database fixtures for testing with SQLAlchemy.
"""
import pytest
import os
import sys
from pathlib import Path

# Add project root (parent of backend/) to path so "import backend.*" works
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, project_root)

# Force tests to use an in-memory SQLite DB by default to avoid connecting to
# any local Postgres or remote Supabase instance. This can be overridden with
# the `TEST_DATABASE_URL` environment variable when needed.
os.environ.setdefault('DATABASE_URL', os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:'))

from backend.main import app
from backend.core.models import db, User


@pytest.fixture(scope='session')
def test_app():
    """Create and configure a test Flask app instance."""
    app.config['TESTING'] = True
    app.config['ENV'] = 'testing'
    app.config['RATELIMIT_ENABLED'] = False
    
    # Use in-memory SQLite for testing OR test PostgreSQL
    # For better production parity, use PostgreSQL test database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'TEST_DATABASE_URL',
        'sqlite:///:memory:'  # Fallback to in-memory SQLite
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app


@pytest.fixture(scope='session')
def init_db(test_app):
    """Initialize the test database."""
    with test_app.app_context():
        # Create all tables
        db.create_all()
        yield db
        # Clean up after all tests
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(test_app, init_db):
    """Provide a test client with app context."""
    with test_app.test_client() as client:
        with test_app.app_context():
            # Clear all data before each test
            for table in reversed(db.metadata.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()
            yield client


@pytest.fixture
def authenticated_user(test_app, init_db):
    """Create a test user for authentication tests."""
    from werkzeug.security import generate_password_hash
    
    with test_app.app_context():
        user = User(
            email='testuser@example.com',
            password_hash=generate_password_hash('TestPassword123!')
        )
        db.session.add(user)
        db.session.commit()
        # Return a proxy that reads/writes the DB on demand. This lets tests
        # access and mutate attributes (e.g., `locked_until`) while keeping a
        # stable object reference.
        class UserProxy:
            def __init__(self, uid):
                object.__setattr__(self, '_id', uid)

            @property
            def id(self):
                return object.__getattribute__(self, '_id')

            def __getattr__(self, name):
                u = User.query.get(self._id)
                if u is None:
                    raise AttributeError(name)
                return getattr(u, name)

            def __setattr__(self, name, value):
                if name == '_id':
                    object.__setattr__(self, name, value)
                    return
                u = User.query.get(self._id)
                if u is None:
                    raise AttributeError(name)
                setattr(u, name, value)
                db.session.add(u)
                db.session.commit()

        return UserProxy(user.id)


@pytest.fixture
def auth_token(test_app, authenticated_user):
    """Generate a valid JWT token for testing."""
    from backend.core.auth import create_jwt_token
    
    return create_jwt_token(authenticated_user.id, authenticated_user.email, token_type='access')


@pytest.fixture
def auth_headers(auth_token):
    """Provide authorization headers for authenticated requests."""
    return {'Authorization': f'Bearer {auth_token}'}
