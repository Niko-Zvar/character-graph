"""Модели запроса и ответа API (проверка входных данных)."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_TEXT_LENGTH = 3_000_000


class AnalyzeRequest(BaseModel):
    """Запрос на анализ текста."""

    text: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)
    characters: dict[str, list[str]] = Field(
        min_length=1,
        examples=[{"Иван": ["Иван-царевич", "Ванюша"], "Кощей": []}],
    )
    window: Literal["sentence", "paragraph"] = "sentence"
    min_mentions: int = Field(default=1, ge=1)
    min_links: int = Field(default=1, ge=1)
    top: int | None = Field(default=None, ge=1)

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        """Запрещает текст из одних пробелов."""
        
        if not value.strip():
            raise ValueError("текст не может быть пустым")
        return value


class Link(BaseModel):
    """Связь между двумя персонажами."""

    source: str
    target: str
    weight: int


class AnalyzeResponse(BaseModel):
    """Результат анализа: персонажи с числом упоминаний и связи."""

    fragments: int
    characters: dict[str, int]
    links: list[Link]
