"""Подготовка текста: деление на фрагменты и лемматизация."""

import re
from functools import lru_cache

import pymorphy3

WORD = re.compile(r"[а-яёa-z]+", re.IGNORECASE)
morph = pymorphy3.MorphAnalyzer()


def split_text(text: str, window: str) -> list[str]:
    """Делит текст на предложения (sentence) или абзацы (paragraph)."""

    if window == "sentence":
        pattern = r"(?<=[.!?…])\s+"
    else:
        pattern = r"\n\s*\n"
    return [part.strip() for part in re.split(pattern, text) if part.strip()]


@lru_cache(maxsize=100_000)
def lemma(word: str) -> str:
    """Возвращает начальную форму слова: «Ивану» -> «иван»."""

    return morph.parse(word.lower())[0].normal_form


def lemmatize(text: str) -> str:
    """Возвращает леммы всех слов текста одной строкой через пробел."""

    return " ".join(lemma(word) for word in WORD.findall(text))
