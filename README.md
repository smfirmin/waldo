# Waldo - News Article Geocoding & Mapping API

A Flask API that extracts locations from news articles and visualizes them on an interactive map with AI-generated event summaries.

## Features

- Extract article content from URLs
- AI-powered location extraction using Google Gemini
- Geocoding locations to coordinates
- Interactive map visualization with Leaflet.js
- Event summaries for each location marker

## Development Setup

### Prerequisites

- Python 3.11+
- Google Gemini API key

### Installation

1. **Clone the repository and navigate to the project directory**

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the development server**
   ```bash
   python run.py
   ```
   The application will be available at http://localhost:8000

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Run linting
ruff check .
```

## Docker Deployment

### Build and run with Docker

```bash
# Build the image
docker build -t waldo .

# Run the container
docker run -p 8000:8000 -e GEMINI_API_KEY=your_api_key_here waldo
```

## API Endpoints

- `POST /api/extract` - Extract locations from article URL
- `GET /map/<extraction_id>` - View interactive map
- `GET /health` - Health check

## Project Structure

```
waldo/
├── app/
│   ├── services/          # Core business logic
│   ├── models/           # Data models
│   └── templates/        # HTML templates
├── tests/               # Unit tests
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── Dockerfile          # Container configuration
└── README.md           # This file
```