from enum import Enum
from pydantic import BaseModel, Field, field_validator


class TargetModel(str, Enum):
    GPT4 = "gpt-4"
    CLAUDE = "claude-3-5"
    GEMINI = "gemini-1-5"


class PromptCreate(BaseModel):
    # Fixed length constraints for strings
    title: str = Field(min_length=5, max_length=20)
    template: str = Field(
        min_length=2,
        max_length=200,
        description="Prompt template containing variables like {variable_name}",
    )
    # Fixed type annotation
    targetmodel: TargetModel
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return value.strip().title()


class PromptUpdate(BaseModel):
    title: str | None = None
    template: str | None = None
    targetmodel: TargetModel | None = None
    tags: list[str] | None = None


class PromptRenderRequest(BaseModel):
    variables: dict[str, str] = Field(
        default_factory=dict,
        description="Key-value pairs to populate inside the template",
    )