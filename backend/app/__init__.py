from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.database import init_db
from app.routes.health_routes import health_bp
from app.routes.lesson_plans_routes import lesson_plans_bp
from app.swagger import init_swagger


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    init_db(app)
    init_swagger(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(lesson_plans_bp)

    @app.errorhandler(404)
    def handle_not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        return {"error": "Internal server error"}, 500

    return app
