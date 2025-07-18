from flask import Blueprint, request, jsonify, render_template
from pydantic import ValidationError
import time
import concurrent.futures
from typing import List

from app.models.data_models import ArticleRequest, ArticleResponse, LocationData
from app.services.article_extractor import ArticleExtractor
from app.services.location_extractor import LocationExtractor
from app.services.geocoding import GeocodingService
from app.services.summarizer import EventSummarizer
from config import Config

bp = Blueprint("main", __name__)

# Initialize services
article_extractor = ArticleExtractor()
geocoding_service = GeocodingService()


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


@bp.route("/api/extract", methods=["POST"])
def extract_locations():
    """Extract locations from article URL and return with coordinates"""
    start_time = time.time()

    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        article_request = ArticleRequest(**data)

        # Extract article content
        title, article_text = article_extractor.extract_from_url(
            str(article_request.url)
        )

        if not article_text.strip():
            return jsonify({"error": "No article content found"}), 400

        # Initialize AI services
        location_extractor, summarizer = get_ai_services()

        # Extract locations using AI
        location_names = location_extractor.extract_locations(article_text)

        if not location_names:
            processing_time = time.time() - start_time
            response = ArticleResponse(
                article_title=title,
                article_text=article_text,
                locations=[],
                processing_time=processing_time,
            )
            return jsonify(response.model_dump())

        # Process locations in parallel: geocoding + summarization
        def process_location(location_name: str) -> LocationData:
            # Geocode location
            coords = geocoding_service.geocode_location(location_name)
            if not coords:
                return None

            # Generate summary for this location
            summary = summarizer.summarize_events_at_location(
                article_text, location_name
            )

            return LocationData(
                name=location_name,
                latitude=coords[0],
                longitude=coords[1],
                events_summary=summary,
            )

        # Use ThreadPoolExecutor for parallel processing
        locations = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_location = {
                executor.submit(process_location, name): name for name in location_names
            }

            for future in concurrent.futures.as_completed(future_to_location):
                location_data = future.result()
                if location_data:  # Only add successfully geocoded locations
                    locations.append(location_data)

        processing_time = time.time() - start_time

        response = ArticleResponse(
            article_title=title,
            article_text=article_text,
            locations=locations,
            processing_time=processing_time,
        )

        return jsonify(response.model_dump())

    except ValidationError as e:
        return jsonify({"error": "Invalid request data", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@bp.route("/map", methods=["GET"])
def show_map():
    """Serve the interactive map page"""
    return render_template("map.html")


@bp.route("/", methods=["GET"])
def index():
    """Serve the main page"""
    return render_template("map.html")
