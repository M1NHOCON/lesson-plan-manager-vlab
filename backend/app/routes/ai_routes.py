from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from app.schemas.ai_schema import AIRecommendationRequestSchema
from app.services import ai_service


ai_bp = Blueprint("ai", __name__)


def _validation_error_response(error):
    return (
        jsonify(
            {
                "error": "Validation error",
                "details": error.errors(include_context=False, include_input=False),
            }
        ),
        400,
    )


@ai_bp.post("/ai/recommendations")
def create_recommendations():
    """
    Generate Smart Assist recommendations for a lesson plan.
    ---
    tags:
      - Smart Assist
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/AIRecommendationRequest'
    responses:
      200:
        description: Recommendations generated successfully.
        schema:
          $ref: '#/definitions/AIRecommendationResponse'
        examples:
          application/json:
            contents:
              - Conceito de roteamento dinamico
              - Funcionamento basico do OSPF
              - Areas OSPF
            related_topics:
              - Protocolos de roteamento
              - Topologias de rede
              - Convergencia de rede
            tags:
              - OSPF
              - Redes
              - Roteamento
            source: mock
      400:
        description: Invalid request body.
        schema:
          $ref: '#/definitions/ValidationError'
      500:
        description: Unexpected server error.
    """
    try:
        schema = AIRecommendationRequestSchema(**(request.get_json(silent=True) or {}))
        recommendations = ai_service.generate_recommendations(
            schema.model_dump(),
            api_key=current_app.config.get("LLM_API_KEY"),
            provider=current_app.config.get("LLM_PROVIDER"),
        )
        return jsonify(recommendations)
    except ValidationError as error:
        return _validation_error_response(error)
