from flask import Blueprint, jsonify


health_bp = Blueprint("health", __name__)


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
    return jsonify(
        {
            "status": "ok",
            "message": "Lesson Plan Manager API is running",
        }
    )
