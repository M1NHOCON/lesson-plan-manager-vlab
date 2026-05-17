from datetime import date

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.schemas.lesson_plan_schema import (
    LessonPlanCreateSchema,
    LessonPlanUpdateSchema,
)
from app.services.lesson_plan_service import LessonPlanNotFoundError
from app.services import lesson_plan_service


lesson_plans_bp = Blueprint("lesson_plans", __name__)


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


def _parse_positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    return parsed if parsed > 0 else default


def _parse_filters(args):
    planned_date = args.get("planned_date")
    parsed_planned_date = None
    if planned_date:
        try:
            parsed_planned_date = date.fromisoformat(planned_date)
        except ValueError as exc:
            raise ValueError("planned_date must be in YYYY-MM-DD format") from exc

    sort_by = args.get("sort_by", "created_at")
    if sort_by not in {"title", "created_at", "planned_date"}:
        sort_by = "created_at"

    order = args.get("order", "desc").lower()
    if order not in {"asc", "desc"}:
        order = "desc"

    return {
        "page": _parse_positive_int(args.get("page"), 1),
        "per_page": _parse_positive_int(args.get("per_page"), 10),
        "search": args.get("search"),
        "discipline": args.get("discipline"),
        "tag": args.get("tag"),
        "planned_date": parsed_planned_date,
        "sort_by": sort_by,
        "order": order,
    }


@lesson_plans_bp.post("/lesson-plans")
def create_lesson_plan():
    """
    Create a lesson plan.
    ---
    tags:
      - Lesson Plans
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/LessonPlanCreate'
    responses:
      201:
        description: Lesson plan created successfully.
        schema:
          $ref: '#/definitions/LessonPlan'
      400:
        description: Invalid request body.
        schema:
          $ref: '#/definitions/ValidationError'
      500:
        description: Unexpected server error.
    """
    try:
        schema = LessonPlanCreateSchema(**(request.get_json(silent=True) or {}))
        lesson_plan = lesson_plan_service.create(schema.model_dump())
        return jsonify(lesson_plan), 201
    except ValidationError as error:
        return _validation_error_response(error)


@lesson_plans_bp.get("/lesson-plans")
def list_lesson_plans():
    """
    List lesson plans with pagination, filters and sorting.
    ---
    tags:
      - Lesson Plans
    parameters:
      - in: query
        name: page
        type: integer
        required: false
        default: 1
      - in: query
        name: per_page
        type: integer
        required: false
        default: 10
      - in: query
        name: search
        type: string
        required: false
        description: Search by title.
      - in: query
        name: discipline
        type: string
        required: false
      - in: query
        name: tag
        type: string
        required: false
      - in: query
        name: planned_date
        type: string
        format: date
        required: false
        description: Date in YYYY-MM-DD format.
      - in: query
        name: sort_by
        type: string
        enum: [title, created_at, planned_date]
        required: false
        default: created_at
      - in: query
        name: order
        type: string
        enum: [asc, desc]
        required: false
        default: desc
    responses:
      200:
        description: Paginated lesson plan list.
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                $ref: '#/definitions/LessonPlan'
            pagination:
              $ref: '#/definitions/Pagination'
      400:
        description: Invalid query parameter.
        schema:
          $ref: '#/definitions/ValidationError'
      500:
        description: Unexpected server error.
    """
    try:
        filters = _parse_filters(request.args)
    except ValueError as error:
        return jsonify({"error": "Validation error", "details": [str(error)]}), 400

    return jsonify(lesson_plan_service.list_all(filters))


@lesson_plans_bp.get("/lesson-plans/<int:lesson_plan_id>")
def get_lesson_plan(lesson_plan_id):
    """
    Get a lesson plan by ID.
    ---
    tags:
      - Lesson Plans
    parameters:
      - in: path
        name: lesson_plan_id
        type: integer
        required: true
    responses:
      200:
        description: Lesson plan found.
        schema:
          $ref: '#/definitions/LessonPlan'
      404:
        description: Lesson plan not found.
        schema:
          $ref: '#/definitions/NotFoundError'
      500:
        description: Unexpected server error.
    """
    try:
        return jsonify(lesson_plan_service.get_by_id(lesson_plan_id))
    except LessonPlanNotFoundError:
        return jsonify({"error": "Lesson plan not found"}), 404


@lesson_plans_bp.put("/lesson-plans/<int:lesson_plan_id>")
def update_lesson_plan(lesson_plan_id):
    """
    Update a lesson plan by ID.
    ---
    tags:
      - Lesson Plans
    parameters:
      - in: path
        name: lesson_plan_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/LessonPlanUpdate'
    responses:
      200:
        description: Lesson plan updated successfully.
        schema:
          $ref: '#/definitions/LessonPlan'
      400:
        description: Invalid request body.
        schema:
          $ref: '#/definitions/ValidationError'
      404:
        description: Lesson plan not found.
        schema:
          $ref: '#/definitions/NotFoundError'
      500:
        description: Unexpected server error.
    """
    try:
        schema = LessonPlanUpdateSchema(**(request.get_json(silent=True) or {}))
        payload = schema.model_dump(exclude_unset=True)
        lesson_plan = lesson_plan_service.update(lesson_plan_id, payload)
        return jsonify(lesson_plan)
    except ValidationError as error:
        return _validation_error_response(error)
    except LessonPlanNotFoundError:
        return jsonify({"error": "Lesson plan not found"}), 404


@lesson_plans_bp.delete("/lesson-plans/<int:lesson_plan_id>")
def delete_lesson_plan(lesson_plan_id):
    """
    Delete a lesson plan by ID.
    ---
    tags:
      - Lesson Plans
    parameters:
      - in: path
        name: lesson_plan_id
        type: integer
        required: true
    responses:
      200:
        description: Lesson plan deleted successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Lesson plan deleted successfully
      404:
        description: Lesson plan not found.
        schema:
          $ref: '#/definitions/NotFoundError'
      500:
        description: Unexpected server error.
    """
    try:
        return jsonify(lesson_plan_service.delete(lesson_plan_id))
    except LessonPlanNotFoundError:
        return jsonify({"error": "Lesson plan not found"}), 404
