"""Поиск персонажей в тексте и подсчёт связей между ними."""

import logging
from collections import Counter
from dataclasses import dataclass
from itertools import combinations

from character_graph.text_processing import lemmatize, split_text

logger = logging.getLogger(__name__)


@dataclass
class Graph:
    """Результат анализа: персонажи (вершины) и связи (рёбра)."""

    fragments: int
    mentions: dict[str, int]
    links: dict[tuple[str, str], int]


def parse_characters(text: str) -> dict[str, list[str]]:
    """Разбирает список персонажей из текста."""

    characters = {}
    for line in text.splitlines():
        names = [name.strip() for name in line.split(",") if name.strip()]
        if names:
            if names[0] in characters:
                raise ValueError(f"Персонаж «{names[0]}» указан дважды")
            characters[names[0]] = names[1:]
    return characters


def analyze(
    text: str,
    characters: dict[str, list[str]],
    window: str = "sentence",
    min_mentions: int = 1,
    min_links: int = 1,
    top: int | None = None,
) -> Graph:
    """Считает упоминания персонажей и их совместные появления."""

    variants = {
        name: [lemmatize(alias) for alias in [name, *aliases]]
        for name, aliases in characters.items()
    }
    fragments = split_text(text, window)
    mentions: Counter[str] = Counter()
    links: Counter[tuple[str, str]] = Counter()
    for fragment in fragments:
        lemmas = f" {lemmatize(fragment)} "
        found = sorted(
            name
            for name, forms in variants.items()
            if any(form and f" {form} " in lemmas for form in forms)
        )
        mentions.update(found)
        links.update(combinations(found, 2))

    missing = [name for name in characters if name not in mentions]
    if missing:
        logger.warning("Не найдены в тексте: %s", ", ".join(missing))

    kept = {
        name: count
        for name, count in mentions.most_common(top)
        if count >= min_mentions
    }
    kept_links = {
        pair: count
        for pair, count in links.most_common()
        if count >= min_links and pair[0] in kept and pair[1] in kept
    }
    logger.info(
        "Фрагментов: %d, персонажей: %d, связей: %d",
        len(fragments),
        len(kept),
        len(kept_links),
    )
    return Graph(len(fragments), kept, kept_links)
