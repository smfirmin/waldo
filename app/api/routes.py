from flask import Blueprint, request, jsonify, Response
from pydantic import ValidationError
import time
import uuid
import logging
import json

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
from app.utils.progress_tracker import (
    get_progress_tracker,
    cleanup_progress_tracker,
    ProgressEvent,
)
from config import Config

bp = Blueprint("api", __name__, url_prefix="/api")

# Configure logging
logger = logging.getLogger(__name__)

# Initialize services
article_extractor = ArticleExtractor()
geocoding_service = GeocodingService()
location_processor = LocationProcessor(geocoding_service)


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


@bp.route("/progress/<session_id>", methods=["GET"])
def progress_stream(session_id: str):
    """Server-Sent Events endpoint for real-time progress updates"""

    def event_stream():
        progress_tracker = get_progress_tracker(session_id)
        event_queue = []

        def sse_callback(event: ProgressEvent):
            event_queue.append(event)

        # Register callback to receive events
        progress_tracker.add_callback(sse_callback)

        try:
            # Send initial connection confirmation
            yield (
                "data: "
                + json.dumps(
                    {
                        "status": "connected",
                        "session_id": session_id,
                        "timestamp": time.time(),
                    }
                )
                + "\n\n"
            )

            # Stream events as they come in
            while True:
                if event_queue:
                    event = event_queue.pop(0)
                    yield progress_tracker.get_sse_data(event)

                    # If complete or error, break the stream
                    if event.status.value in ["complete", "error"]:
                        break
                else:
                    # Keep connection alive with heartbeat
                    yield (
                        "data: "
                        + json.dumps({"heartbeat": True, "timestamp": time.time()})
                        + "\n\n"
                    )
                    time.sleep(0.5)

        finally:
            # Clean up when connection closes
            cleanup_progress_tracker(session_id)

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


@bp.route("/extract", methods=["POST"])
def extract_locations():
    """Extract locations from article URL or text and return with coordinates"""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(f"Processing request {request_id}")

    # Initialize progress tracker
    progress_tracker = get_progress_tracker(request_id)
    progress_tracker.start_processing()

    try:
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning(f"Request {request_id}: No JSON data provided")
            progress_tracker.error("No data provided in request body")
            return create_error_response(
                "MISSING_DATA", "No data provided in request body"
            )

        # Check for required fields
        if "input" not in data:
            logger.warning(f"Request {request_id}: Missing 'input' field")
            progress_tracker.error("Required field 'input' is missing")
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
        progress_tracker.start_article_extraction(article_request.input)

        if article_request.is_url():
            try:
                logger.info(f"Request {request_id}: Extracting content from URL")
                title, article_text = article_extractor.extract_from_url(
                    article_request.get_url()
                )
            except Exception as e:
                logger.error(f"Request {request_id}: URL extraction failed: {str(e)}")
                progress_tracker.error(f"Failed to extract content from URL: {str(e)}")
                return create_error_response(
                    "URL_EXTRACTION_FAILED",
                    "Failed to extract content from URL",
                    details=str(e),
                    status_code=422,
                )

            if not article_text or not article_text.strip():
                logger.warning(f"Request {request_id}: No content found at URL")
                progress_tracker.error("No readable content found at the provided URL")
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
        progress_tracker.start_location_extraction(len(article_text))

        try:
            extracted_locations = location_extractor.extract_locations(article_text)
            progress_tracker.locations_found(len(extracted_locations))
            logger.info(
                f"Request {request_id}: Extracted {len(extracted_locations)} locations"
            )
        except RateLimitError as e:
            logger.warning(f"Request {request_id}: Rate limit exceeded")
            progress_tracker.error(
                "API rate limit exceeded. Please try again in a few moments."
            )
            return create_error_response(
                "RATE_LIMIT_EXCEEDED",
                "API rate limit exceeded. Please try again in a few moments.",
                details=str(e),
                status_code=429,
                retry_after=60,  # Suggest retry after 60 seconds
            )

        if not extracted_locations:
            processing_time = time.time() - start_time
            progress_tracker.complete(0, processing_time)
            response = ArticleResponse(
                article_title=title,
                article_text=article_text,
                locations=[],
                processing_time=processing_time,
                request_id=request_id,
            )
            return jsonify(response.model_dump())

        # Process locations through geocoding and summarization pipeline
        progress_tracker.start_processing_locations(len(extracted_locations))
        locations, geo_data_list = location_processor.process_locations_pipeline(
            extracted_locations, article_text, summarizer, response, request_id
        )

        # Apply spatial hierarchical filtering
        progress_tracker.start_filtering()
        locations = location_processor.apply_spatial_filtering(
            locations, geo_data_list, response, request_id
        )

        processing_time = time.time() - start_time
        progress_tracker.complete(len(locations), processing_time)

        # Update the existing response object (which may have warnings) instead of creating new one
        response.locations = locations
        response.processing_time = processing_time

        # Add session_id to response for frontend to connect to SSE
        response_data = response.model_dump()
        response_data["session_id"] = request_id
        return jsonify(response_data)

    except ValidationError as e:
        return jsonify({"error": "Invalid request data", "details": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
