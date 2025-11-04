"""FastAPI ベースの Azure OpenAI チャットバックエンド。"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .azure_client import get_openai_client
from .models import ChatRequest, ChatResponse, ChatResponseMessage, ErrorResponse
from .settings import get_settings


settings = get_settings()

app = FastAPI(title="Azure Chat Sample", version="0.1.0")


if settings.allow_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.allow_origin],
        allow_methods=["*"],
        allow_headers=["*"],
    )


frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"


@app.get("/api/config")
async def get_ui_config() -> dict:
    """フロントエンド初期化用の設定値を返す。"""

    ui = settings.ui
    return {
        "title": ui.title,
        "subtitle": ui.subtitle,
        "footer": ui.footer,
    }


@app.post("/api/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}})
async def create_completion(payload: ChatRequest) -> JSONResponse:
    """Azure OpenAI に問い合わせて応答メッセージを生成する。"""

    if not payload.messages:
        raise HTTPException(status_code=400, detail="messages は必須です。")

    azure_settings = settings.azure_openai

    messages = _build_messages(payload.messages, system_prompt=azure_settings.system_prompt)

    client = get_openai_client()

    try:
        completion = await asyncio.to_thread(
            client.chat.completions.create,
            model=azure_settings.deployment,
            messages=messages,
            temperature=azure_settings.temperature,
            top_p=azure_settings.top_p,
            max_tokens=azure_settings.max_tokens,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    content = completion.choices[0].message.content if completion.choices else ""
    response = ChatResponse(message=ChatResponseMessage(content=content or ""))
    return JSONResponse(status_code=200, content=response.model_dump())


def _build_messages(messages: Iterable, system_prompt: str | None) -> list[dict]:
    result: list[dict] = []
    if system_prompt:
        result.append({"role": "system", "content": system_prompt})

    for message in messages:
        result.append({"role": message.role, "content": message.content})

    return result


@app.get("/healthz")
async def healthcheck() -> dict:
    """ライブネス / レディネス用エンドポイント。"""

    return {"status": "ok"}


if not frontend_dist.exists():

    @app.get("/", include_in_schema=False)
    async def serve_root() -> dict:
        return {
            "message": "フロントエンドがまだビルドされていません。先に 'npm run build' を実行してください。"
        }
else:
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="app")

