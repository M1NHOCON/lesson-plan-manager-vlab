import json

from app.repositories.lesson_plan_repository import (
    create_lesson_plan,
    delete_lesson_plan,
    get_lesson_plan_by_id,
    list_lesson_plans,
    update_lesson_plan,
)
from app.utils.logger import get_logger


logger = get_logger(__name__)


class LessonPlanNotFoundError(Exception):
    pass


def _serialize_lists(data):
    serialized = dict(data)

    for field in ("contents", "support_resources", "tags"):
        if field in serialized:
            serialized[field] = json.dumps(serialized.get(field) or [])

    return serialized


def create(data):
    logger.info("Creating lesson plan")
    lesson_plan = create_lesson_plan(_serialize_lists(data))
    return lesson_plan.to_dict()


def list_all(filters):
    logger.info("Listing lesson plans")
    result = list_lesson_plans(filters)

    return {
        "items": [lesson_plan.to_dict() for lesson_plan in result.items],
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total_items": result.total,
            "total_pages": result.pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev,
        },
    }


def get_by_id(lesson_plan_id):
    lesson_plan = get_lesson_plan_by_id(lesson_plan_id)
    if lesson_plan is None:
        raise LessonPlanNotFoundError("Lesson plan not found")

    return lesson_plan.to_dict()


def update(lesson_plan_id, data):
    lesson_plan = get_lesson_plan_by_id(lesson_plan_id)
    if lesson_plan is None:
        raise LessonPlanNotFoundError("Lesson plan not found")

    logger.info("Updating lesson plan id=%s", lesson_plan_id)
    updated = update_lesson_plan(lesson_plan, _serialize_lists(data))
    return updated.to_dict()


def delete(lesson_plan_id):
    lesson_plan = get_lesson_plan_by_id(lesson_plan_id)
    if lesson_plan is None:
        raise LessonPlanNotFoundError("Lesson plan not found")

    logger.info("Deleting lesson plan id=%s", lesson_plan_id)
    delete_lesson_plan(lesson_plan)
    return {"message": "Lesson plan deleted successfully"}
