from app import create_app
import auth


def test_jwt_create_and_verify():
    app = create_app()
    app.config['SECRET_KEY'] = 'test-secret'
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_EXPIRATION_HOURS'] = 1

    with app.app_context():
        token = auth.create_jwt_token('123', 'me@example.com')
        payload = auth.verify_jwt_token(token)
        assert payload is not None
        assert payload.get('user_id') == '123'
        assert payload.get('email') == 'me@example.com'
