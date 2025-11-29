import os
import uuid
from datetime import datetime
import requests
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from ..core.auth import require_auth
from ..core.storage import supabase_upload_file, supabase_get_signed_url, create_upload_record
from ..core.utils import allowed_file, validate_content_type, validate_file_size, MODEL_VERSION
from ..core.schemas import APIResponse, ResponseMeta, DetectionData, DetectionResult
from .. import prediction as predictor

detect_bp = Blueprint('detect', __name__)


@detect_bp.route('/api/detect', methods=['POST'])
@require_auth
def detect_image():
    """
    Detect plant disease from uploaded image or Supabase URL.
    
    Accepts:
    - multipart/form-data with 'file' field
    - JSON with 'signed_url' or 'image_url' field (Supabase signed URL)
    
    Returns:
    - 200: {success: true, data: {file_key, file_url, detection}, meta: {request_id, timestamp, model_version}}
    - 400: {success: false, error: {code, message}}
    """
    request_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    user_id = getattr(request, 'user_id', None)
    
    try:
        # Log incoming request
        current_app.logger.info(
            f"Detection request received: request_id={request_id} user_id={user_id} "
            f"timestamp={start_time.isoformat()} content_type={request.content_type}"
        )

        file_contents = None
        filename = None
        content_type = None
        file_size = None

        # Handle multipart/form-data file upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return APIResponse.error('No file selected', 'NO_FILE_SELECTED')
            
            filename = secure_filename(file.filename)
            content_type = file.content_type
            
            # Validate file extension
            if not allowed_file(filename):
                return APIResponse.error(
                    f"Invalid file extension. Allowed: png, jpg, jpeg, webp",
                    'INVALID_FILE_TYPE'
                )
            
            # Validate content type
            is_valid, error_msg = validate_content_type(content_type)
            if not is_valid:
                return APIResponse.error(error_msg, 'INVALID_CONTENT_TYPE')
            
            # Validate file size
            is_valid, size_or_error = validate_file_size(file)
            if not is_valid:
                return APIResponse.error(size_or_error, 'FILE_TOO_LARGE')
            
            file_size = size_or_error
            file_contents = file.read()
            
            current_app.logger.info(
                f"File upload validated: request_id={request_id} filename={filename} "
                f"content_type={content_type} size={file_size}"
            )

        # Handle JSON with signed_url or image_url
        elif request.is_json or request.form:
            data = request.get_json(silent=True) or {}
            signed_url = data.get('signed_url') or data.get('image_url') or request.form.get('signed_url') or request.form.get('image_url')
            
            if not signed_url:
                return APIResponse.error('No file or signed_url/image_url provided', 'MISSING_INPUT')
            
            current_app.logger.info(
                f"Processing image from URL: request_id={request_id} url={signed_url[:100]}"
            )
            
            # If URL is relative (starts with '/'), prefix SUPABASE_URL
            fetch_url = signed_url
            if fetch_url.startswith('/'):
                base = os.getenv('SUPABASE_URL') or current_app.config.get('SUPABASE_URL')
                if base:
                    fetch_url = base.rstrip('/') + fetch_url

            try:
                resp = requests.get(fetch_url, timeout=30)
            except Exception as e:
                current_app.logger.exception(f'Failed to fetch signed URL: request_id={request_id}')
                return APIResponse.error(f'Could not fetch image from URL: {str(e)}', 'DOWNLOAD_FAILED')

            if resp.status_code != 200:
                current_app.logger.warning(f'Signed URL fetch returned status {resp.status_code}: request_id={request_id}')
                return APIResponse.error(f'Could not fetch image from URL (status {resp.status_code})', 'DOWNLOAD_FAILED')

            file_contents = resp.content
            content_type = resp.headers.get('Content-Type', 'image/jpeg')
            filename = fetch_url.split('/')[-1].split('?')[0] or f'reprocess_{uuid.uuid4().hex[:8]}.jpg'
            file_size = len(file_contents)
            
        else:
            return APIResponse.error(
                'Request must be multipart/form-data with file or JSON with signed_url/image_url',
                'INVALID_REQUEST_FORMAT'
            )

        # Upload to Supabase storage
        file_key = None
        file_url = None
        try:
            file_key = supabase_upload_file(file_contents, filename, content_type, user_id)
            current_app.logger.info(f"File uploaded to storage: request_id={request_id} file_key={file_key}")
        except Exception:
            current_app.logger.exception(f'Supabase upload failed: request_id={request_id}')
            # Continue with prediction even if upload fails

        # Get signed URL
        if file_key:
            try:
                file_url = supabase_get_signed_url(file_key)
            except Exception:
                current_app.logger.exception(f'Failed to generate signed URL: request_id={request_id}')

        # Perform prediction
        detection = None
        try:
            detection = predictor.predict_disease_from_bytes(file_contents)
            current_app.logger.info(
                f"Prediction completed: request_id={request_id} class_id={detection.get('class_id')} "
                f"class_name={detection.get('class_name')} confidence={detection.get('confidence')} "
                f"model_version={MODEL_VERSION}"
            )
        except Exception:
            current_app.logger.exception(f'Model prediction failed: request_id={request_id}')
            return APIResponse.error('Model prediction failed', 'PREDICTION_FAILED', 500)

        # Create upload record
        try:
            record = create_upload_record(user_id=user_id, filename=filename, file_path=file_key or '', detection_result=detection)
        except Exception:
            current_app.logger.exception(f'Failed to create upload record: request_id={request_id}')

        # Create standardized response
        detection_result = DetectionResult(
            class_id=detection['class_id'],
            class_name=detection['class_name'],
            confidence=detection['confidence']
        )
        
        detection_data = DetectionData(
            file_key=file_key or '',
            file_url=file_url,
            detection=detection_result
        )
        
        meta = ResponseMeta.create(MODEL_VERSION)
        meta.request_id = request_id  # Use the request_id we generated at the start
        
        return jsonify(APIResponse.success(detection_data, meta)), 200

    except Exception as e:
        current_app.logger.exception(f'Unhandled exception in /api/detect: request_id={request_id}')
        return APIResponse.error(f'Internal server error: {str(e)}', 'INTERNAL_ERROR', 500)
