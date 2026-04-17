import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from .routes import routes


def create_app():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    frontend_build_dir = os.path.join(project_root, "carbon-frontend", "build")
    frontend_static_dir = os.path.join(frontend_build_dir, "static")

    app = Flask(
        __name__,
        static_folder=frontend_static_dir if os.path.isdir(frontend_static_dir) else None,
        template_folder=frontend_build_dir if os.path.isdir(frontend_build_dir) else None,
    )

    cors_origins = os.getenv("CORS_ORIGINS", "*")
    origins = cors_origins.split(",") if cors_origins != "*" else "*"
    CORS(app, resources={r"/api/*": {"origins": origins}})

    app.register_blueprint(routes)

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def serve_frontend(path):
        if not app.template_folder or not os.path.isdir(app.template_folder):
            return jsonify(
                {
                    "message": "CarbonQuest API is running.",
                    "frontend_build_found": False,
                }
            )

        requested_path = os.path.join(app.template_folder, path)
        if path and os.path.exists(requested_path):
            return send_from_directory(app.template_folder, path)

        return send_from_directory(app.template_folder, "index.html")

    return app
