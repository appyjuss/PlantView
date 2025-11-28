import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from ..core.auth import require_auth
from ..core.utils import allowed_file
from ..core.storage import supabase_upload_file, supabase_get_signed_url, create_upload_record
from .. import prediction as predictor

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    """Upload a file to storage."""
    try:
        # Log key request metadata for debugging frontend vs test-client differences.
        try:
            headers = dict(request.headers)
        except Exception:
            headers = {}
        auth_header = headers.get('Authorization') or headers.get('authorization')
        masked_auth = None
        if auth_header:
            # keep last 6 chars for debugging, mask the rest
            masked_auth = '***' + auth_header[-6:]
        current_app.logger.warning("/api/upload called: Origin=%s Content-Length=%s Content-Type=%s Authorization=%s",
                                   headers.get('Origin') or headers.get('origin'),
                                   request.content_length,
                                   headers.get('Content-Type') or headers.get('content-type'),
                                   masked_auth)

        # Optional: verbose header logging for browser debugging. Controlled by env var VERBOSE_UPLOAD_HEADERS.
        try:
            from datetime import datetime
            if os.getenv('VERBOSE_UPLOAD_HEADERS', '').lower() in ('1', 'true', 'yes'):
                # Prepare masked headers (exclude full Authorization value)
                verbose_headers = {}
                for k, v in headers.items():
                    if k.lower() == 'authorization':
                        # keep only last 8 chars
                        verbose_headers[k] = ('***' + v[-8:]) if v else v
                    else:
                        verbose_headers[k] = v

                # Form field names and uploaded filenames (no file bytes)
                files_info = {}
                for name, fs in request.files.items():
                    try:
                        files_info[name] = {'filename': getattr(fs, 'filename', None), 'content_type': getattr(fs, 'content_type', None), 'size': None}
                    except Exception:
                        files_info[name] = {'filename': None, 'content_type': None, 'size': None}

                log_entry = {
                    'time': datetime.utcnow().isoformat() + 'Z',
                    'remote_addr': request.remote_addr,
                    'method': request.method,
                    'path': request.path,
                    'content_length': request.content_length,
                    'headers': verbose_headers,
                    'files': files_info
                }

                # Log the verbose headers (masked) to application logger only
                try:
                    current_app.logger.warning('Verbose upload headers: %s', str(log_entry))
                except Exception:
                    current_app.logger.exception('Failed to log verbose upload headers')
        except Exception:
            current_app.logger.exception('Error in verbose header logging')

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        filename = secure_filename(file.filename)
        # Log uploaded file metadata (filename and mime) at warning level
        try:
            current_app.logger.warning("Uploaded file: filename=%s content_type=%s", filename, file.content_type)
        except Exception:
            current_app.logger.exception("Failed to log uploaded file metadata")
        user_id = getattr(request, 'user_id', None)
        content_type = file.content_type or 'application/octet-stream'

        try:
            # Read and upload (this reads the file into memory; ensure frontend file sizes are acceptable)
            file_contents = file.stream.read()
            current_app.logger.warning("Uploading file for user=%s filename=%s size=%s bytes", user_id, filename, len(file_contents))
            file_key = supabase_upload_file(file_contents, filename, content_type, user_id)
            if not file_key:
                current_app.logger.error("supabase_upload_file returned falsy for user=%s filename=%s", user_id, filename)
                return jsonify({'error': 'Upload failed'}), 500

            # Run model inference on the uploaded image bytes (CPU inference)
            try:
                detection = predictor.predict_disease_from_bytes(file_contents)
            except Exception:
                current_app.logger.exception("Model prediction failed for user=%s filename=%s", user_id, filename)
                detection = None

            # Persist record with detection_result (may be None on model failure)
            try:
                record = create_upload_record(user_id=user_id, filename=filename, file_path=file_key, detection_result=detection)
            except Exception:
                current_app.logger.exception("Failed to create upload record for user=%s filename=%s", user_id, filename)

            # Try to generate a signed URL for immediate client access and include it in response
            try:
                file_url = supabase_get_signed_url(file_key)
                if not file_url:
                    current_app.logger.warning("signed_url not available immediately for file_key=%s user=%s", file_key, user_id)
            except Exception:
                current_app.logger.exception("Error generating signed URL for file_key=%s user=%s", file_key, user_id)
                file_url = None

            return jsonify({'success': True, 'file_key': file_key, 'file_url': file_url, 'detection': detection}), 201
        except Exception:
            current_app.logger.exception("Exception while uploading file for user=%s filename=%s", user_id, filename)
            return jsonify({'error': 'Upload failed'}), 500
    except Exception:
        current_app.logger.exception("Unhandled exception in upload_file")
        return jsonify({'error': 'Upload failed'}), 500


@upload_bp.route('/api/uploads/<path:file_key>', methods=['GET'])
@require_auth
def get_file(file_key):
    """Download a file from storage."""
    try:
        user_id = getattr(request, 'user_id', None)

        # Only allow access to user's own files
        if not file_key.startswith(f"{user_id}/"):
            return jsonify({'error': 'Unauthorized'}), 403

        signed_url = supabase_get_signed_url(file_key)
        if not signed_url:
            current_app.logger.warning("signed_url not found for file_key=%s user=%s", file_key, user_id)
            return jsonify({'error': 'File not found'}), 404

        return jsonify({'url': signed_url})
    except Exception:
        current_app.logger.exception("Exception while getting file for key=%s", file_key)
        return jsonify({'error': 'File not found'}), 500
