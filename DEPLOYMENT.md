# Deployment Guide for Waldo

This application can be deployed to several platforms. Here are the recommended options:

## Option 1: Railway (Recommended - Easiest)

1. **Sign up**: Go to [Railway](https://railway.app) and sign up with GitHub
2. **Deploy**: 
   - Connect your GitHub repository
   - Railway will automatically detect the `railway.toml` and `Dockerfile`
   - Set environment variables in Railway dashboard:
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `SECRET_KEY`: A secure random string

3. **Domain**: Railway provides a free domain like `your-app-name.railway.app`

## Option 2: Render

1. **Sign up**: Go to [Render](https://render.com) and sign up with GitHub
2. **Deploy**:
   - Connect your GitHub repository 
   - Render will detect the `render.yaml` configuration
   - Set environment variables in Render dashboard:
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `SECRET_KEY`: A secure random string

3. **Domain**: Render provides a free domain like `your-app-name.onrender.com`

## Option 3: Google Cloud Run

1. **Setup**: Install Google Cloud CLI and authenticate
2. **Build and Deploy**:
   ```bash
   gcloud run deploy waldo \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your_key,SECRET_KEY=your_secret
   ```

## Environment Variables Required

- `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `SECRET_KEY`: Generate a secure random string
- `FLASK_ENV`: Set to "production"
- `FLASK_DEBUG`: Set to "false"

## Health Check

All platforms can use `/api/health` endpoint for health checks.

## Notes

- The app runs on port 8000 by default
- Frontend assets are served from the `/` route
- API endpoints are under `/api/`
- Requires a valid Gemini API key to function