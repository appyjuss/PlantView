import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify, session
from werkzeug.utils import secure_filename
from flask_cors import CORS
from prediction import predict_disease

ALLOWED_EXTENSIONS = {'png', 'jpg', "jpeg"}
# use absolute uploads path (relative to this file) and ensure it exists
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
app = Flask(__name__, static_folder = "../plantviewFrontend/dist", static_url_path='/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set a secret key for sessions (for production, use env var)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

cors = CORS(app,
            resources={r"/API/*": {"origins": "http://localhost:5173"}},
            supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/api/login', methods=['POST'])
def login():
    """Simple login endpoint that sets an httpOnly cookie for testing auth."""
    data = request.get_json() or {}
    email = data.get('email', '')
    password = data.get('password', '')
    
    # For testing: accept any non-empty email/password
    if email and password:
        # Store user info in session (Flask will create httpOnly cookie)
        session['user_id'] = email  # In real app, validate and store user ID
        session['email'] = email
        
        resp = jsonify({
            "status": "success",
            "message": f"Logged in as {email}",
            "user": {"id": email, "email": email, "name": email.split('@')[0]}
        })
        return resp, 200
    else:
        return jsonify({"status": "error", "message": "Missing email or password"}), 400


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout endpoint that clears the session cookie."""
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"}), 200


@app.route('/api/current-user', methods=['GET'])
def current_user():
    """Get current user from session; returns 401 if not authenticated."""
    if 'email' in session:
        return jsonify({
            "user": {"id": session.get('user_id'), "email": session.get('email'), "name": session.get('email', '').split('@')[0]}
        }), 200
    else:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401

@app.route('/api/upload', methods=['GET', 'POST'])
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
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            
            try:
                result = predict_disease(save_path)
                # debug log to confirm it's a dict/json-serializable
                print("Prediction result (type):", type(result), result)
            except Exception as e:
                print("Error during prediction:", e)
                return jsonify({"error": "Prediction failed", "details": str(e)}), 500

            # ensure we return JSON response
            return jsonify({
                "file": filename,
                "file_url": url_for('download_file', name=filename, _external=True),
                "prediction": result
            }), 200
    return ''


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)

# Ensure Flask app runs when executed directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)