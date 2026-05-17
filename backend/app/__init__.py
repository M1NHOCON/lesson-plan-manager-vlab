from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes.health_routes import health_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)

    app.register_blueprint(health_bp)

    return app
