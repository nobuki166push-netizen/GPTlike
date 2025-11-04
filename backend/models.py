"""FastAPI 用のリクエスト / レスポンスモデル。"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """チャット履歴における 1 メッセージ。"""

    role: Literal["system", "user", "assistant"] = Field(description="メッセージの役割")
    content: str = Field(description="メッセージ本文")


class ChatRequest(BaseModel):
    """チャット API に送信されるペイロード。"""

    messages: list[Message] = Field(default_factory=list)
    stream: bool = Field(default=False, description="ストリーミング応答を要求するかどうか")


class ChatResponseMessage(BaseModel):
    """チャット API の応答メッセージ。"""

    role: Literal["assistant"] = "assistant"
    content: str


class ChatResponse(BaseModel):
    """チャット API 全体のレスポンス。"""

    message: ChatResponseMessage


class ErrorResponse(BaseModel):
    """エラーレスポンス。"""

    detail: str

