"""Azure OpenAI クライアントの生成を担当するユーティリティ。"""

from __future__ import annotations

from functools import lru_cache

from openai import AzureOpenAI

from .settings import get_settings


class AzureClientFactory:
    """Azure OpenAI クライアントの生成と設定値の検証を行う。"""

    def __init__(self) -> None:
        self._settings = get_settings().azure_openai

    def create_client(self) -> AzureOpenAI:
        endpoint = self._settings.endpoint
        resource = self._settings.resource

        if not endpoint and not resource:
            raise ValueError("AZURE_OPENAI_ENDPOINT もしくは AZURE_OPENAI_RESOURCE を設定してください。")

        azure_endpoint = endpoint if endpoint else f"https://{resource}.openai.azure.com/"

        if not self._settings.key:
            raise ValueError("AZURE_OPENAI_KEY が設定されていません。現在の実装では API キーが必須です。")

        return AzureOpenAI(
            api_key=self._settings.key,
            api_version=self._settings.api_version,
            azure_endpoint=azure_endpoint,
        )


@lru_cache(maxsize=1)
def get_openai_client() -> AzureOpenAI:
    """アプリ全体で共有する Azure OpenAI クライアントを返す。"""

    factory = AzureClientFactory()
    return factory.create_client()

