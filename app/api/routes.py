from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import time
import uuid
import logging

from app.models.data_models import (
    ArticleRequest,
    ArticleResponse,
)
from app.services.article_extractor import ArticleExtractor
from app.services.location_extractor import LocationExtractor, RateLimitError
from app.services.geocoding import GeocodingService
from app.services.summarizer import EventSummarizer
from app.services.location_processor import LocationProcessor
from app.utils.response_helpers import create_error_response
from config import Config

bp = Blueprint("api", __name__, url_prefix="/api")

# Configure logging
logger = logging.getLogger(__name__)

# Initialize services
article_extractor = ArticleExtractor()
geocoding_service = GeocodingService()
location_processor = LocationProcessor(geocoding_service)

# Request timeout constants
REQUEST_TIMEOUT = 120  # 2 minutes max
AI_TIMEOUT = 60  # 1 minute for AI operations
WEB_TIMEOUT = 30  # 30 seconds for web requests


# Initialize AI services with API key
def get_ai_services():
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY not configured")

    location_extractor = LocationExtractor(api_key)
    summarizer = EventSummarizer(api_key)
    return location_extractor, summarizer


@bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "waldo"})


@bp.route("/extract", methods=["POST"])
def extract_locations():
    """Extract locations from article URL or text and return with coordinates"""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(f"Processing request {request_id}")

    try:
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning(f"Request {request_id}: No JSON data provided")
            return create_error_response(
                "MISSING_DATA", "No data provided in request body"
            )

        # Check for required fields
        if "input" not in data:
            logger.warning(f"Request {request_id}: Missing 'input' field")
            return create_error_response(
                "MISSING_INPUT", "Required field 'input' is missing"
            )

        article_request = ArticleRequest(**data)
        logger.info(
            f"Request {request_id}: Input type={'URL' if article_request.is_url() else 'text'}, length={len(article_request.input)}"
        )

        # Create response object with tracking
        response = ArticleResponse(
            article_title="",
            article_text="",
            locations=[],
            processing_time=0.0,
            request_id=request_id,
        )

        # Handle URL or text input
        if article_request.is_url():
            try:
                logger.info(f"Request {request_id}: Extracting content from URL")
                title, article_text = article_extractor.extract_from_url(
                    article_request.get_url()
                )
            except Exception as e:
                logger.error(f"Request {request_id}: URL extraction failed: {str(e)}")
                return create_error_response(
                    "URL_EXTRACTION_FAILED",
                    "Failed to extract content from URL",
                    details=str(e),
                    status_code=422,
                )

            if not article_text or not article_text.strip():
                logger.warning(f"Request {request_id}: No content found at URL")
                return create_error_response(
                    "NO_CONTENT",
                    "No readable content found at the provided URL",
                    status_code=422,
                )
        else:
            # Use provided text directly
            title = "Article Text"  # Default title for text input
            article_text = article_request.get_text()
            logger.info(f"Request {request_id}: Processing provided text")

        # Check for text length after extraction
        if len(article_text) > 50000:  # 50KB processing limit
            logger.warning(f"Request {request_id}: Text too long for processing")
            response.add_warning(
                "TEXT_TRUNCATED", "Article text was truncated to 50KB for processing"
            )
            article_text = article_text[:50000]

        response.article_title = title
        response.article_text = article_text

        # Initialize AI services
        location_extractor, summarizer = get_ai_services()

        # Extract locations using AI
        try:
            extracted_locations = location_extractor.extract_locations(article_text)
            logger.info(
                f"Request {request_id}: Extracted {len(extracted_locations)} locations"
            )
        except RateLimitError as e:
            logger.warning(f"Request {request_id}: Rate limit exceeded")
            return create_error_response(
                "RATE_LIMIT_EXCEEDED",
                "API rate limit exceeded. Please try again in a few moments.",
                details=str(e),
                status_code=429,
                retry_after=60,  # Suggest retry after 60 seconds
            )

        if not extracted_locations:
            processing_time = time.time() - start_time
            response = ArticleResponse(
                article_title=title,
                article_text=article_text,
                locations=[],
                processing_time=processing_time,
            )
            return jsonify(response.model_dump())

        # Process locations through geocoding and summarization pipeline
        locations, geo_data_list = location_processor.process_locations_pipeline(
            extracted_locations, article_text, summarizer, response, request_id
        )

        # Apply spatial hierarchical filtering
        locations = location_processor.apply_spatial_filtering(
            locations, geo_data_list, response, request_id
        )

        processing_time = time.time() - start_time

        response = ArticleResponse(
            article_title=title,
            article_text=article_text,
            locations=locations,
            processing_time=processing_time,
        )

        return jsonify(response.model_dump())

    except ValidationError as e:
        return jsonify({"error": "Invalid request data", "details": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
