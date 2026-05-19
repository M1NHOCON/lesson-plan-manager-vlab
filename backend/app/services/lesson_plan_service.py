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
    lesson_plan = create_lesson_plan(_serialize_lists(data))
    serialized_lesson_plan = lesson_plan.to_dict()
    logger.info(
        'LessonPlan Created: id=%s, title="%s", discipline="%s"',
        serialized_lesson_plan.get("id"),
        serialized_lesson_plan.get("title"),
        serialized_lesson_plan.get("discipline"),
    )
    return serialized_lesson_plan


def list_all(filters):
    result = list_lesson_plans(filters)
    logger.info(
        "LessonPlan List: page=%s, per_page=%s, total_items=%s",
        result.page,
        result.per_page,
        result.total,
    )

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
        logger.warning("LessonPlan Not Found: id=%s", lesson_plan_id)
        raise LessonPlanNotFoundError("Lesson plan not found")

    logger.info("LessonPlan Retrieved: id=%s", lesson_plan_id)
    return lesson_plan.to_dict()


def update(lesson_plan_id, data):
    lesson_plan = get_lesson_plan_by_id(lesson_plan_id)
    if lesson_plan is None:
        logger.warning("LessonPlan Not Found: id=%s", lesson_plan_id)
        raise LessonPlanNotFoundError("Lesson plan not found")

    updated = update_lesson_plan(lesson_plan, _serialize_lists(data))
    serialized_lesson_plan = updated.to_dict()
    logger.info(
        'LessonPlan Updated: id=%s, title="%s", discipline="%s"',
        serialized_lesson_plan.get("id"),
        serialized_lesson_plan.get("title"),
        serialized_lesson_plan.get("discipline"),
    )
    return serialized_lesson_plan


def delete(lesson_plan_id):
    lesson_plan = get_lesson_plan_by_id(lesson_plan_id)
    if lesson_plan is None:
        logger.warning("LessonPlan Not Found: id=%s", lesson_plan_id)
        raise LessonPlanNotFoundError("Lesson plan not found")

    delete_lesson_plan(lesson_plan)
    logger.info("LessonPlan Deleted: id=%s", lesson_plan_id)
    return {"message": "Lesson plan deleted successfully"}
