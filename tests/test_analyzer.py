"""Тесты обработки текста и анализа персонажей."""

from pathlib import Path

from character_graph.analyzer import analyze, parse_characters
from character_graph.text_processing import lemmatize, split_text

EXAMPLES = Path(__file__).parent.parent / "src/character_graph/examples"
TALE = (EXAMPLES / "tale.txt").read_text(encoding="utf-8")
CHARACTERS = parse_characters(
    (EXAMPLES / "characters.txt").read_text(encoding="utf-8")
)


def test_lemmatize_reduces_cases_to_base_form() -> None:
    assert lemmatize("Ивану Василисы Кощея") == "иван василиса кощей"


def test_split_into_sentences_and_paragraphs() -> None:
    text = "Иван пришёл. Василиса ушла!\n\nКощей остался."
    assert split_text(text, "sentence") == [
        "Иван пришёл.",
        "Василиса ушла!",
        "Кощей остался.",
    ]
    assert len(split_text(text, "paragraph")) == 2


def test_parse_characters_with_aliases() -> None:
    text = "Иван, Иван-царевич, Ванюша\n\n  Кощей  \n"
    assert parse_characters(text) == {
        "Иван": ["Иван-царевич", "Ванюша"],
        "Кощей": [],
    }


def test_main_scenario_on_tale() -> None:
    result = analyze(TALE, CHARACTERS)

    assert result.fragments == 14
    assert result.mentions["Иван"] == 10
    assert result.mentions["Кощей"] == 6
    assert result.links[("Василиса", "Кощей")] == 4
    assert result.links[("Иван", "Серый Волк")] == 4


def test_paragraph_window() -> None:
    result = analyze(TALE, CHARACTERS, window="paragraph")

    assert result.fragments == 4
    assert result.mentions["Кощей"] == 4


def test_filters_and_top() -> None:
    result = analyze(TALE, CHARACTERS, min_links=3, top=2)

    assert list(result.mentions) == ["Иван", "Кощей"]
    assert result.links == {("Иван", "Кощей"): 3}


def test_single_character_has_no_links() -> None:
    result = analyze("Иван шёл. Иван пришёл.", {"Иван": []})

    assert result.mentions == {"Иван": 2}
    assert result.links == {}


def test_characters_not_in_text() -> None:
    result = analyze("Шёл дождь.", {"Кощей": []})

    assert result.mentions == {}
    assert result.links == {}
