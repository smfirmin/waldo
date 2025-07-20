# Waldo - News Article Location Mapper

A web application that extracts locations from news articles and visualizes them on an interactive map with AI-generated event summaries.

## 🚀 Live Demo

Try it out: **[https://waldo-production-d5b9.up.railway.app/](https://waldo-production-d5b9.up.railway.app/)**

## Features

- **Dual Input Support**: Extract from URLs or paste article text directly
- **AI-Powered Location Extraction**: Uses Google Gemini 2.0 Flash for intelligent location identification
- **Real-time Progress Updates**: Live progress tracking with Server-Sent Events during processing
- **Smart Geocoding**: Converts location names to coordinates with boundary detection
- **Spatial Filtering**: Removes duplicate and hierarchically contained locations
- **Interactive Map**: Modern dark-themed map with custom markers and popups
- **Event Summaries**: AI-generated context for what happened at each location
- **Responsive Design**: Works on desktop and mobile devices

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

3. **Install backend dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

6. **Run the development server**
   ```bash
   python run.py
   ```
   The application will be available at http://localhost:8000

### Testing

```bash
# Run backend tests
pytest

# Run backend tests with coverage
pytest --cov=app

# Run frontend tests
cd frontend && npm test

# Run all tests (backend + frontend)
./test-all.sh

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

- `GET /` - Serve the frontend application
- `POST /api/extract` - Extract locations from article URL or text
- `GET /api/progress/<session_id>` - Server-Sent Events stream for real-time progress updates
- `GET /api/health` - Health check endpoint

## Project Structure

```
waldo/
├── app/
│   ├── api/              # API routes and blueprints
│   ├── services/         # Core business logic (AI, geocoding, processing)
│   ├── models/           # Pydantic data models
│   └── utils/            # Helper utilities
├── frontend/
│   ├── js/               # JavaScript modules (map, API, UI)
│   ├── css/              # Stylesheets
│   ├── templates/        # HTML templates
│   └── tests/            # Frontend Jest tests
├── tests/                # Backend pytest tests
├── prompts/              # AI prompt templates
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── docs/                # Documentation
├── Dockerfile           # Container configuration
└── railway.toml         # Railway deployment config
```

## Deployment

This application is configured for easy deployment on Railway. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed setup instructions.

**Quick Deploy**: Connect your GitHub repo to Railway - it will auto-detect the configuration and deploy!

## Documentation

- 📚 [Deployment Guide](docs/DEPLOYMENT.md) - Railway deployment instructions
- 🧪 [Testing Guide](docs/TESTING.md) - Test setup and execution
- 📋 [Requirements](docs/REQUIREMENTS.md) - Technical specifications of assignment
- 📝 [TODO](docs/TODO.md) - Planned improvements and roadmap