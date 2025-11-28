import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from prediction import predict_disease

ALLOWED_EXTENSIONS = {'png', 'jpg', "jpeg"}
# use absolute uploads path (relative to this file) and ensure it exists
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
app = Flask(__name__, static_folder = "../plantviewFrontend/dist", static_url_path='/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
cors = CORS(app,
            resources={r"/API/*": {"origins": "http://localhost:5173"}},
            supports_credentials=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/API/upload', methods=['GET', 'POST'])
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