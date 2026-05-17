from app.database import db
from app.models import LessonPlan


SORTABLE_FIELDS = {
    "title": LessonPlan.title,
    "created_at": LessonPlan.created_at,
    "planned_date": LessonPlan.planned_date,
}


def create_lesson_plan(data):
    lesson_plan = LessonPlan(**data)
    db.session.add(lesson_plan)
    db.session.commit()
    return lesson_plan


def list_lesson_plans(filters):
    query = LessonPlan.query

    search = filters.get("search")
    if search:
        query = query.filter(LessonPlan.title.ilike(f"%{search}%"))

    discipline = filters.get("discipline")
    if discipline:
        query = query.filter(LessonPlan.discipline == discipline)

    tag = filters.get("tag")
    if tag:
        query = query.filter(LessonPlan.tags.ilike(f'%"{tag}"%'))

    planned_date = filters.get("planned_date")
    if planned_date:
        query = query.filter(LessonPlan.planned_date == planned_date)

    sort_column = SORTABLE_FIELDS.get(filters.get("sort_by"), LessonPlan.created_at)
    if filters.get("order") == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.paginate(
        page=filters["page"],
        per_page=filters["per_page"],
        error_out=False,
    )


def get_lesson_plan_by_id(lesson_plan_id):
    return db.session.get(LessonPlan, lesson_plan_id)


def update_lesson_plan(lesson_plan, data):
    for field, value in data.items():
        setattr(lesson_plan, field, value)

    db.session.commit()
    return lesson_plan


def delete_lesson_plan(lesson_plan):
    db.session.delete(lesson_plan)
    db.session.commit()
