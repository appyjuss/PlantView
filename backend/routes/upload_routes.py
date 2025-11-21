import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from ..core.auth import require_auth
from ..core.utils import allowed_file
from ..core.storage import supabase_upload_file, supabase_get_signed_url

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/API/upload', methods=['GET', 'POST'])
@require_auth
def upload_file():
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    filename = secure_filename(file.filename)
    user_id = getattr(request, 'user_id', None)
    content_type = file.content_type or 'application/octet-stream'
    file_key = supabase_upload_file(file.stream.read(), filename, content_type, user_id)
    if not file_key:
        return jsonify({'error': 'Upload failed'}), 500
    return jsonify({'success': True, 'file_key': file_key}), 201


@upload_bp.route('/uploads/<name>')
def download_file(name):
    from ..core.auth import require_auth

    @upload_bp.route('/API/uploads/<file_key>', methods=['GET'])
    @require_auth
    def get_file(file_key):
        user_id = getattr(request, 'user_id', None)
        # Only allow access to user's own files
        if not file_key.startswith(f"{user_id}/"):
            return jsonify({'error': 'Unauthorized'}), 403
        signed_url = supabase_get_signed_url(file_key)
        if not signed_url:
            return jsonify({'error': 'File not found'}), 404
        return jsonify({'url': signed_url})
