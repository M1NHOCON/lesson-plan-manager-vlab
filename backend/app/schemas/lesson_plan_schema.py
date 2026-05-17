from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LessonPlanBaseSchema(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    objective: Optional[str] = Field(default=None, min_length=1)
    summary: Optional[str] = Field(default=None, min_length=1)
    planned_date: Optional[date] = None
    discipline: Optional[str] = Field(default=None, min_length=1, max_length=120)
    contents: Optional[list[str]] = None
    support_resources: Optional[list[str]] = None
    tags: Optional[list[str]] = None

    @field_validator("title", "objective", "summary", "discipline")
    @classmethod
    def strip_required_strings(cls, value):
        if value is None:
            return value

        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be blank")
        return stripped

    @field_validator("planned_date", mode="before")
    @classmethod
    def validate_planned_date_format(cls, value):
        if value is None or isinstance(value, date):
            return value

        if not isinstance(value, str):
            raise ValueError("planned_date must be in YYYY-MM-DD format")

        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("planned_date must be in YYYY-MM-DD format") from exc

    @field_validator("contents", "support_resources", "tags")
    @classmethod
    def validate_string_lists(cls, value):
        if value is None:
            return value

        if not all(isinstance(item, str) for item in value):
            raise ValueError("All list items must be strings")

        return [item.strip() for item in value if item.strip()]


class LessonPlanCreateSchema(LessonPlanBaseSchema):
    title: str = Field(min_length=1, max_length=255)
    objective: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    planned_date: date
    discipline: str = Field(min_length=1, max_length=120)
    contents: list[str] = Field(default_factory=list)
    support_resources: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class LessonPlanUpdateSchema(LessonPlanBaseSchema):
    pass
