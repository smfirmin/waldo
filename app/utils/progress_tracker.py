import json
import time
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ProgressStatus(Enum):
    STARTING = "starting"
    EXTRACTING_ARTICLE = "extracting_article"
    EXTRACTING_LOCATIONS = "extracting_locations"
    PROCESSING_LOCATIONS = "processing_locations"
    FILTERING = "filtering"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ProgressEvent:
    status: ProgressStatus
    message: str
    progress_percent: float = 0.0
    current_item: Optional[str] = None
    total_items: Optional[int] = None
    current_index: Optional[int] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class ProgressTracker:
    """Tracks progress of article processing and emits SSE events"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.events: Dict[str, ProgressEvent] = {}
        self.callbacks = []

    def add_callback(self, callback):
        """Add a callback function to receive progress events"""
        self.callbacks.append(callback)

    def emit_event(self, status: ProgressStatus, message: str, **kwargs):
        """Emit a progress event"""
        event = ProgressEvent(status=status, message=message, **kwargs)
        self.events[status.value] = event

        # Call all registered callbacks
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                # Log error but don't stop processing
                print(f"Progress callback error: {e}")

    def get_sse_data(self, event: ProgressEvent) -> str:
        """Format event data for Server-Sent Events"""
        event_data = asdict(event)
        event_data["status"] = event.status.value
        event_data["session_id"] = self.session_id

        return f"data: {json.dumps(event_data)}\n\n"

    def start_processing(self):
        """Mark the start of processing"""
        self.emit_event(
            ProgressStatus.STARTING,
            "Starting article processing...",
            progress_percent=0.0,
        )

    def start_article_extraction(self, url_or_text: str):
        """Mark the start of article extraction"""
        is_url = url_or_text.startswith(("http://", "https://"))
        message = (
            "Extracting content from URL..." if is_url else "Processing article text..."
        )

        self.emit_event(
            ProgressStatus.EXTRACTING_ARTICLE,
            message,
            progress_percent=10.0,
            current_item=url_or_text[:100] + "..."
            if len(url_or_text) > 100
            else url_or_text,
        )

    def start_location_extraction(self, article_length: int):
        """Mark the start of location extraction"""
        self.emit_event(
            ProgressStatus.EXTRACTING_LOCATIONS,
            f"Finding locations in {article_length:,} character article...",
            progress_percent=25.0,
        )

    def locations_found(self, location_count: int):
        """Report number of locations found"""
        self.emit_event(
            ProgressStatus.EXTRACTING_LOCATIONS,
            f"Found {location_count} potential locations",
            progress_percent=40.0,
            total_items=location_count,
        )

    def start_processing_locations(self, total_locations: int):
        """Mark the start of parallel geocoding and summarization"""
        self.emit_event(
            ProgressStatus.PROCESSING_LOCATIONS,
            f"Processing {total_locations} locations (geocoding + generating summaries)...",
            progress_percent=50.0,
            total_items=total_locations,
        )

    def start_filtering(self):
        """Mark the start of spatial filtering"""
        self.emit_event(
            ProgressStatus.FILTERING,
            "Applying spatial filters and removing duplicates...",
            progress_percent=80.0,
        )

    def complete(self, final_location_count: int, processing_time: float):
        """Mark processing as complete"""
        self.emit_event(
            ProgressStatus.COMPLETE,
            f"Complete! Found {final_location_count} locations in {processing_time:.1f}s",
            progress_percent=100.0,
            total_items=final_location_count,
        )

    def error(self, error_message: str):
        """Mark processing as failed"""
        self.emit_event(
            ProgressStatus.ERROR, f"Error: {error_message}", progress_percent=0.0
        )


# Global progress tracker storage
_progress_trackers: Dict[str, ProgressTracker] = {}


def get_progress_tracker(session_id: str) -> ProgressTracker:
    """Get or create a progress tracker for a session"""
    if session_id not in _progress_trackers:
        _progress_trackers[session_id] = ProgressTracker(session_id)
    return _progress_trackers[session_id]


def cleanup_progress_tracker(session_id: str):
    """Clean up a progress tracker"""
    if session_id in _progress_trackers:
        del _progress_trackers[session_id]
