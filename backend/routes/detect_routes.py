import os
import requests
from flask import Blueprint, request, jsonify, current_app

from ..core.auth import require_auth
from ..core.storage import supabase_upload_file, supabase_get_signed_url, create_upload_record
from .. import prediction as predictor

detect_bp = Blueprint('detect', __name__)


@detect_bp.route('/api/detect', methods=['POST'])
@require_auth
def detect_image():
    """Accept an image file or a Supabase signed URL, run inference, store metadata, and return result."""
    try:
        user_id = getattr(request, 'user_id', None)

        # Prefer file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            file_contents = file.read()
            content_type = file.content_type or 'application/octet-stream'
            filename = file.filename

            # Try upload to Supabase (best-effort)
            try:
                file_key = supabase_upload_file(file_contents, filename, content_type, user_id)
            except Exception:
                current_app.logger.exception('Supabase upload failed during /api/detect')
                file_key = None

            try:
                detection = predictor.predict_disease_from_bytes(file_contents)
            except Exception:
                current_app.logger.exception('Model prediction failed in /api/detect')
                detection = None

            try:
                record = create_upload_record(user_id=user_id, filename=filename, file_path=file_key or '', detection_result=detection)
            except Exception:
                current_app.logger.exception('Failed to create upload record in /api/detect')

            try:
                file_url = supabase_get_signed_url(file_key) if file_key else None
            except Exception:
                current_app.logger.exception('Failed to generate signed URL in /api/detect')
                file_url = None

            return jsonify({'success': True, 'detection': detection, 'file_key': file_key, 'file_url': file_url}), 200

        # Otherwise accept a signed URL in JSON body or form
        data = request.get_json(silent=True) or {}
        signed_url = data.get('signed_url') or request.form.get('signed_url')
        if not signed_url:
            return jsonify({'error': 'No file or signed_url provided'}), 400

        # If URL is relative (starts with '/'), prefix SUPABASE_URL
        fetch_url = signed_url
        if fetch_url.startswith('/'):
            base = os.getenv('SUPABASE_URL') or current_app.config.get('SUPABASE_URL')
            if base:
                fetch_url = base.rstrip('/') + fetch_url

        try:
            resp = requests.get(fetch_url, timeout=30)
        except Exception:
            current_app.logger.exception('Failed to fetch signed URL in /api/detect')
            return jsonify({'error': 'Could not fetch signed_url'}), 400

        if resp.status_code != 200:
            current_app.logger.warning('Signed URL fetch returned status %s', resp.status_code)
            return jsonify({'error': 'Could not fetch signed_url'}), 400

        file_contents = resp.content
        content_type = resp.headers.get('Content-Type', 'application/octet-stream')
        # Derive filename from URL
        filename = fetch_url.split('/')[-1].split('?')[0] or 'upload'

        try:
            file_key = supabase_upload_file(file_contents, filename, content_type, user_id)
        except Exception:
            current_app.logger.exception('Supabase upload failed in /api/detect (signed_url)')
            file_key = None

        try:
            detection = predictor.predict_disease_from_bytes(file_contents)
        except Exception:
            current_app.logger.exception('Model prediction failed in /api/detect (signed_url)')
            detection = None

        try:
            record = create_upload_record(user_id=user_id, filename=filename, file_path=file_key or '', detection_result=detection)
        except Exception:
            current_app.logger.exception('Failed to create upload record in /api/detect (signed_url)')

        try:
            file_url = supabase_get_signed_url(file_key) if file_key else None
        except Exception:
            current_app.logger.exception('Failed to generate signed URL in /api/detect (signed_url)')
            file_url = None

        return jsonify({'success': True, 'detection': detection, 'file_key': file_key, 'file_url': file_url}), 200

    except Exception:
        current_app.logger.exception('Unhandled exception in /api/detect')
        return jsonify({'error': 'Internal server error'}), 500
