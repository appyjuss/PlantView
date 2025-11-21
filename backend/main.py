import os
import jwt
import json
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

ALLOWED_EXTENSIONS = {'png', 'jpg', "jpeg"}
UPLOAD_FOLDER = '../uploads'
DB_FILE = 'users.json'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

app = Flask(__name__, static_folder = "../plantviewFrontend/dist", static_url_path='/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
cors = CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
)

# Simple file-based user database
def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def create_jwt_token(user_id, email):
    """Create a JWT token valid for 24 hours"""
    payload = {
        'user_id': user_id,
        'email': email,
        # Use integer epoch seconds for iat/exp to ensure compatibility
        'iat': int(datetime.now(timezone.utc).timestamp()),
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user_id = payload['user_id']
        request.user_email = payload['email']
        return f(*args, **kwargs)
    
    return decorated

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data.get('email').strip().lower()
    password = data.get('password')
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    users = load_users()
    
    if email in users:
        return jsonify({'error': 'User already exists'}), 409
    
    user_id = str(len(users) + 1)
    users[email] = {
        'id': user_id,
        'email': email,
        'password': generate_password_hash(password),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    save_users(users)
    
    token = create_jwt_token(user_id, email)
    return jsonify({
        'token': token,
        'user': {
            'id': user_id,
            'email': email
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data.get('email').strip().lower()
    password = data.get('password')
    
    users = load_users()
    user = users.get(email)
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    token = create_jwt_token(user['id'], email)
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'email': email
        }
    }), 200

@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_token():
    """Verify current token is valid"""
    return jsonify({
        'user': {
            'id': request.user_id,
            'email': request.user_email
        }
    }), 200

@app.route('/')
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/API/upload', methods=['GET', 'POST'])
@require_auth
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return ''


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(UPLOAD_FOLDER, name)


if __name__ == '__main__':
    # Ensure upload directory exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception:
        pass

    # Run the Flask development server
    # In production, use a proper WSGI server (gunicorn / waitress etc.)
    app.run(host='0.0.0.0', port=5000, debug=True)