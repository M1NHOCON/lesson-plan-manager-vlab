from pydantic import BaseModel, Field, field_validator


class AIRecommendationRequestSchema(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    discipline: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1)

    @field_validator("title", "discipline", "summary")
    @classmethod
    def strip_required_strings(cls, value):
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be blank")
        return stripped
