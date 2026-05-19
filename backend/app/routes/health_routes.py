from flask import Blueprint, jsonify

from app.utils.logger import get_logger


health_bp = Blueprint("health", __name__)
logger = get_logger(__name__)


@health_bp.get("/health")
def health_check():
    """
    Check API health.
    ---
    tags:
      - Health
    responses:
      200:
        description: API is running.
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            message:
              type: string
              example: Lesson Plan Manager API is running
    """
    logger.info('Health Check: status="ok"')
    return jsonify(
        {
            "status": "ok",
            "message": "Lesson Plan Manager API is running",
        }
    )
