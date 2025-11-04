"""アプリ全体の設定管理モジュール。"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI 連携に必要な設定値を保持する。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    endpoint: Optional[HttpUrl] = Field(default=None, alias="AZURE_OPENAI_ENDPOINT")
    resource: Optional[str] = Field(default=None, alias="AZURE_OPENAI_RESOURCE")
    key: Optional[str] = Field(default=None, alias="AZURE_OPENAI_KEY")
    deployment: str = Field(alias="AZURE_OPENAI_DEPLOYMENT", description="Azure OpenAI のデプロイメント名")
    api_version: str = Field(default="2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION")
    temperature: float = Field(default=0.0, alias="AZURE_OPENAI_TEMPERATURE")
    max_tokens: int = Field(default=800, alias="AZURE_OPENAI_MAX_TOKENS")
    top_p: float = Field(default=1.0, alias="AZURE_OPENAI_TOP_P")
    system_prompt: str = Field(
        default="You are an AI assistant that helps people find information.",
        alias="AZURE_OPENAI_SYSTEM_PROMPT",
    )


class UISettings(BaseSettings):
    """フロントエンド表示に関する設定値。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    title: str = Field(default="Contoso Copilot", alias="UI_TITLE")
    subtitle: str = Field(default="Ask anything about your data", alias="UI_SUBTITLE")
    footer: str = Field(default="Powered by Azure OpenAI", alias="UI_FOOTER")


class AppSettings(BaseSettings):
    """アプリ全体の設定をまとめる。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    azure_openai: AzureOpenAISettings = AzureOpenAISettings()
    ui: UISettings = UISettings()
    allow_origin: Optional[str] = Field(default=None, alias="CORS_ALLOW_ORIGIN")


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """設定値を取得（キャッシュ付き）。"""

    return AppSettings()

