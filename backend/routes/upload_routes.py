import os
from flask import Blueprint, request, jsonify, current_app, make_response, Response
from werkzeug.utils import secure_filename

from ..core.auth import require_auth
from ..core.utils import allowed_file
from ..core.storage import supabase_upload_file, supabase_get_signed_url, create_upload_record, get_user_uploads
from .. import prediction as predictor

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    """
    DEPRECATED: Use /api/detect instead.
    This endpoint is maintained for backward compatibility.
    """
    from .detect_routes import detect_image
    
    # Get the response from detect endpoint
    result = detect_image()
    
    # Add deprecation headers
    if isinstance(result, Response):
        resp = result
    elif isinstance(result, tuple):
        response_data, status_code = result
        resp = make_response(response_data, status_code)
    else:
        resp = make_response(result)
    
    resp.headers['X-Deprecated-Endpoint'] = 'true'
    resp.headers['X-Use-Instead'] = '/api/detect'
    resp.headers['Warning'] = '299 - "This endpoint is deprecated. Please use /api/detect instead."'
    
    return resp


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



@upload_bp.route('/api/uploads', methods=['GET'])
@require_auth
def list_uploads():
    """Return a list of uploads for the authenticated user with signed URLs and detection results."""
    try:
        user_id = getattr(request, 'user_id', None)
        records = get_user_uploads(user_id)
        out = []
        for r in records:
            try:
                file_url = supabase_get_signed_url(r.file_path)
                if not file_url:
                    current_app.logger.warning(f"Failed to generate signed URL for upload id={r.id} key={r.file_path}")
            except Exception:
                current_app.logger.exception("Failed to get signed URL for upload id=%s key=%s", r.id, r.file_path)
                file_url = None
            out.append({
                'id': r.id,
                'file_key': r.file_path,
                'file_url': file_url,
                'detection': r.detection_result,
                'created_at': r.uploaded_at.isoformat() if getattr(r, 'uploaded_at', None) else None,
                'filename': r.filename,
            })
        return jsonify(out)
    except Exception:
        current_app.logger.exception('Exception while listing uploads for user=%s', getattr(request, 'user_id', None))
        return jsonify({'error': 'Could not list uploads'}), 500
