import os

from app import create_app


application = create_app()


if __name__ == "__main__":
    application.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "").lower() == "true",
    )
