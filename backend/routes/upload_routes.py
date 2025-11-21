import os
from flask import Blueprint, request, redirect, url_for, flash, current_app, send_from_directory
from werkzeug.utils import secure_filename

from ..core.auth import require_auth
from ..core.utils import allowed_file

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/API/upload', methods=['GET', 'POST'])
@require_auth
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = current_app.config.get('UPLOAD_FOLDER')
            file.save(os.path.join(upload_dir, filename))
            return redirect(url_for('upload.download_file', name=filename))
    return ''


@upload_bp.route('/uploads/<name>')
def download_file(name):
    upload_dir = current_app.config.get('UPLOAD_FOLDER')
    return send_from_directory(upload_dir, name)
