from flask import Flask
from flask_cors import CORS
from .routes import routes
import os

def create_app():
    # 👇 specify static_folder pointing to root/static
    static_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, static_folder=static_folder_path)
    
    CORS(app)
    app.register_blueprint(routes)
    return app
