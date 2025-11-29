"""Standardized API response schemas."""
from datetime import datetime
from typing import Any, Optional, Dict
from dataclasses import dataclass, asdict
import uuid


@dataclass
class DetectionResult:
    """Detection result schema."""
    class_id: int
    class_name: str
    confidence: float


@dataclass
class ResponseMeta:
    """Response metadata."""
    request_id: str
    timestamp: str
    model_version: str

    @classmethod
    def create(cls, model_version: str):
        """Create metadata with auto-generated request_id and timestamp."""
        return cls(
            request_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + 'Z',
            model_version=model_version
        )


@dataclass
class DetectionData:
    """Detection response data."""
    file_key: str
    file_url: Optional[str]
    detection: DetectionResult


class APIResponse:
    """Standardized API response wrapper."""
    
    @staticmethod
    def success(data: Any, meta: ResponseMeta) -> Dict:
        """Create success response."""
        data_dict = asdict(data) if hasattr(data, '__dataclass_fields__') else data
        return {
            'success': True,
            'data': data_dict,
            'meta': asdict(meta)
        }
    
    @staticmethod
    def error(message: str, code: str = 'ERROR', status_code: int = 400) -> tuple:
        """Create error response with status code."""
        return {
            'success': False,
            'error': {
                'code': code,
                'message': message
            }
        }, status_code
