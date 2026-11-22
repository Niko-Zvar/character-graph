"""FastAPI-приложение: веб-страница и API."""

import base64
import logging
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from character_graph.analyzer import Graph, analyze, parse_characters
from character_graph.graph import draw_graph
from character_graph.schemas import (
    MAX_TEXT_LENGTH,
    AnalyzeRequest,
    AnalyzeResponse,
    Link,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
EXAMPLES_DIR = BASE_DIR / "examples"
templates = Jinja2Templates(directory=BASE_DIR / "templates")

DEFAULT_FORM = {
    "text": (EXAMPLES_DIR / "tale.txt").read_text(encoding="utf-8"),
    "characters": (EXAMPLES_DIR / "characters.txt").read_text(
        encoding="utf-8"
    ),
    "window": "sentence",
    "min_mentions": 1,
    "min_links": 1,
    "top": None,
}

app = FastAPI(
    title="Character Graph",
    description="Граф персонажей: кто с кем появляется в одном фрагменте.",
    version="0.2.0",
)


def read_upload(file: UploadFile) -> str:
    """Читает TXT-файл в кодировке UTF-8 или Windows-1251."""
    
    content = file.file.read()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        logger.info("Файл %s не в UTF-8, читаем как cp1251", file.filename)
        return content.decode("cp1251")


def to_response(result: Graph) -> AnalyzeResponse:
    """Переводит результат анализа в формат ответа API."""

    links = [
        Link(source=source, target=target, weight=weight)
        for (source, target), weight in result.links.items()
    ]
    return AnalyzeResponse(
        fragments=result.fragments,
        characters=result.mentions,
        links=links,
    )


@app.get("/")
def index(request: Request) -> HTMLResponse:
    """Главная страница: форма, заполненная примером."""

    return templates.TemplateResponse(
        request, "index.html", {"form": DEFAULT_FORM}
    )


@app.post("/")
def build_graph_page(
    request: Request,
    text: Annotated[str, Form()] = "",
    characters: Annotated[str, Form()] = "",
    window: Annotated[Literal["sentence", "paragraph"], Form()] = "sentence",
    min_mentions: Annotated[int, Form(ge=1)] = 1,
    min_links: Annotated[int, Form(ge=1)] = 1,
    top: Annotated[int | None, Form(ge=1)] = None,
    file: Annotated[UploadFile | None, File()] = None,
) -> HTMLResponse:
    """Обрабатывает форму и показывает граф с таблицами."""

    if file is not None and file.filename:
        text = read_upload(file)
    form = {
        "text": text,
        "characters": characters,
        "window": window,
        "min_mentions": min_mentions,
        "min_links": min_links,
        "top": top,
    }

    parsed = parse_characters(characters)
    error = None
    if not text.strip():
        error = "Введите текст или загрузите TXT-файл"
    elif len(text) > MAX_TEXT_LENGTH:
        error = "Текст слишком длинный"
    elif not parsed:
        error = "Укажите хотя бы одного персонажа"
    if error:
        logger.warning("Некорректный ввод: %s", error)
        return templates.TemplateResponse(
            request,
            "index.html",
            {"form": form, "error": error},
            status_code=400,
        )

    result = analyze(text, parsed, window, min_mentions, min_links, top)
    image = base64.b64encode(draw_graph(result)).decode("ascii")
    return templates.TemplateResponse(
        request,
        "index.html",
        {"form": form, "result": result, "image": image},
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Проверка, что сервис запущен."""

    return {"status": "ok"}


@app.post("/api/analyze")
def api_analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Возвращает граф персонажей в формате JSON."""

    return to_response(analyze(**request.model_dump()))
