import json
from datetime import datetime

from app.database import db


def _loads_list(value):
    if not value:
        return []

    try:
        loaded = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []

    if not isinstance(loaded, list):
        return []

    return [item for item in loaded if isinstance(item, str)]


class LessonPlan(db.Model):
    __tablename__ = "lesson_plans"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    objective = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    planned_date = db.Column(db.Date, nullable=False)
    discipline = db.Column(db.String(120), nullable=False)
    contents = db.Column(db.Text, nullable=True)
    support_resources = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "objective": self.objective,
            "summary": self.summary,
            "planned_date": self.planned_date.isoformat(),
            "discipline": self.discipline,
            "contents": _loads_list(self.contents),
            "support_resources": _loads_list(self.support_resources),
            "tags": _loads_list(self.tags),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
