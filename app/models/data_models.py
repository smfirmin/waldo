from pydantic import BaseModel, field_validator
from typing import List, Optional
import re
import uuid
from datetime import datetime


class LocationData(BaseModel):
    name: str
    latitude: float
    longitude: float
    events_summary: Optional[str] = None
    confidence: Optional[float] = None
    resolution_method: Optional[str] = None
    original_text: Optional[str] = None


class ExtractedLocation(BaseModel):
    original_text: str
    standardized_name: str
    context: str
    confidence: str  # high/medium/low
    location_type: str  # city/state/country/landmark/region/nickname/generic
    disambiguation_hints: List[str] = []


class ArticleRequest(BaseModel):
    input: str

    @field_validator("input")
    @classmethod
    def validate_input_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Input cannot be empty")
        return v.strip()

    @field_validator("input")
    @classmethod
    def validate_input_length(cls, v):
        if len(v) > 100000:  # 100KB limit
            raise ValueError("Input too large. Maximum size is 100KB.")
        return v

    @field_validator("input")
    @classmethod
    def validate_safe_url(cls, v):
        if cls._is_url_like(v):
            # Check for suspicious URLs
            suspicious_patterns = [
                r"localhost",
                r"127\.0\.0\.1",
                r"192\.168\.",
                r"10\.",
                r"172\.(1[6-9]|2[0-9]|3[0-1])\.",
                r"file://",
                r"ftp://",
            ]
            for pattern in suspicious_patterns:
                if re.search(pattern, v, re.IGNORECASE):
                    raise ValueError("URL not allowed for security reasons")
        return v

    @classmethod
    def _is_url_like(cls, v: str) -> bool:
        """Quick check if string looks like a URL"""
        return v.strip().lower().startswith(("http://", "https://"))

    def is_url(self) -> bool:
        """Check if input is a URL using regex pattern"""
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return bool(url_pattern.match(self.input))

    def get_text(self) -> str:
        """Return the text content (input if not URL)"""
        if self.is_url():
            raise ValueError("Cannot get text from URL - use extract_from_url instead")
        return self.input

    def get_url(self) -> str:
        """Return the URL (input if URL)"""
        if not self.is_url():
            raise ValueError("Input is not a valid URL")
        return self.input


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[str] = None
    request_id: str
    timestamp: str
    retry_after: Optional[int] = None

    @classmethod
    def create(
        cls,
        error_code: str,
        message: str,
        details: Optional[str] = None,
        retry_after: Optional[int] = None,
    ) -> "ErrorResponse":
        return cls(
            error_code=error_code,
            message=message,
            details=details,
            request_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            retry_after=retry_after,
        )


class ProcessingWarning(BaseModel):
    code: str
    message: str


class ArticleResponse(BaseModel):
    article_title: Optional[str] = None
    article_text: str
    locations: List[LocationData]
    processing_time: float
    warnings: List[ProcessingWarning] = []
    request_id: str = ""

    def add_warning(self, code: str, message: str):
        """Add a warning to the response"""
        self.warnings.append(ProcessingWarning(code=code, message=message))
