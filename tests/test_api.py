"""Тесты API и веб-страницы."""

import pytest
from fastapi.testclient import TestClient

from character_graph import main

client = TestClient(main.app)

REQUEST = {
    "text": "Иван встретил Василису. Василиса помогла Ивану. Кощей злился.",
    "characters": {"Иван": [], "Василиса": [], "Кощей": []},
}
REQUEST_FORM = {"text": REQUEST["text"], "characters": "Иван\nВасилиса"}


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_api_analyze() -> None:
    response = client.post("/api/analyze", json=REQUEST)

    assert response.status_code == 200
    assert response.json() == {
        "fragments": 3,
        "characters": {"Василиса": 2, "Иван": 2, "Кощей": 1},
        "links": [{"source": "Василиса", "target": "Иван", "weight": 2}],
    }


def test_api_rejects_invalid_input() -> None:
    bad_requests = [
        {**REQUEST, "text": "   "},
        {**REQUEST, "window": "chapter"},
        {**REQUEST, "min_mentions": 0},
        {**REQUEST, "characters": {}},
        {"characters": {}},
    ]
    for request in bad_requests:
        assert client.post("/api/analyze", json=request).status_code == 422


def test_page_shows_form_with_example() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Построить граф" in response.text
    assert "Иван-царевич" in response.text


def test_page_builds_graph_from_text() -> None:
    response = client.post("/", data=REQUEST_FORM)

    assert response.status_code == 200
    assert "data:image/png;base64" in response.text
    assert "Василиса — Иван" in response.text


def test_page_reads_cp1251_file() -> None:
    file = ("tale.txt", REQUEST["text"].encode("cp1251"), "text/plain")

    response = client.post(
        "/", data={"characters": "Иван"}, files={"file": file}
    )

    assert response.status_code == 200
    assert "data:image/png;base64" in response.text


def test_page_shows_error_for_empty_text() -> None:
    response = client.post("/", data={"text": "  ", "top": ""})

    assert response.status_code == 400
    assert "Введите текст" in response.text


def test_page_shows_error_without_characters() -> None:
    response = client.post("/", data={"text": REQUEST["text"]})

    assert response.status_code == 400
    assert "Укажите хотя бы одного персонажа" in response.text


def test_page_shows_error_for_too_long_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(main, "MAX_TEXT_LENGTH", 10)

    response = client.post("/", data=REQUEST_FORM)

    assert response.status_code == 400
    assert "Текст слишком длинный" in response.text
