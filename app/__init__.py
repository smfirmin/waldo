from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
import os


def create_app():
    # Configure Flask to serve frontend from parent directory
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    app = Flask(
        __name__,
        static_folder=frontend_dir,
        template_folder=os.path.join(frontend_dir, "templates"),
    )
    app.config.from_object(Config)

    # Enable CORS for frontend integration
    CORS(app)

    # Import and register API blueprint only
    from app.api.routes import bp as api_bp

    app.register_blueprint(api_bp)

    # Serve frontend assets
    @app.route("/")
    def index():
        return send_from_directory(os.path.join(frontend_dir, "templates"), "map.html")

    @app.route("/map")
    def map_page():
        return send_from_directory(os.path.join(frontend_dir, "templates"), "map.html")

    # Serve static files
    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory(frontend_dir, filename)

    return app
