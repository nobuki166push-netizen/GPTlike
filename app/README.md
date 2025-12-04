# App Service (sample-app-aoai-chatGPT)

このディレクトリには、[Microsoft sample-app-aoai-chatGPT](https://github.com/microsoft/sample-app-aoai-chatGPT) をベースに、既存Web全文検索システム（LangGraph統合）の修正を適用したApp Serviceアプリケーションが含まれています。

## 📋 概要

このアプリケーションは、Azure App Service上でホスティングされるWebチャットアプリケーションです。Azure Functions（AIエージェント）と連携して、LangGraphベースのエージェンティックRAG機能を提供します。

## 🔧 主な変更点

### LangGraph統合

- `app.py` の `conversation_internal` 関数にLangGraph統合ロジックを追加
- `MCP_SERVER_URL` 環境変数が設定されている場合、Azure Functions（LangGraph API）にリクエストを転送
- ストリーミング対応（Server-Sent Events）

### 追加エンドポイント

- `/api/logs/session/<session_id>`: セッションIDでログを取得
- `/api/logs/user/<user_id>`: ユーザーIDでログを取得
- `/api/logs/user/<user_id>/sessions`: ユーザーのセッション一覧を取得

## 🚀 デプロイ方法

詳細は [APP_SERVICE_DEPLOYMENT.md](../APP_SERVICE_DEPLOYMENT.md) を参照してください。

### 前提条件

- Azure App Serviceリソースが作成済み
- Azure Functions（AIエージェント）がデプロイ済み
- 環境変数が設定済み（`MCP_SERVER_URL` など）

### 環境変数

App Serviceの「設定」→「構成」で以下の環境変数を設定：

| 環境変数名 | 説明 |
|-----------|------|
| `MCP_SERVER_URL` | Azure Functions（LangGraph API）のエンドポイントURL |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI エンドポイント |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI APIキー |
| `AZURE_OPENAI_API_VERSION` | APIバージョン |
| `AZURE_OPENAI_MODEL` | モデル名 |

## 📁 ディレクトリ構造

```
app/
├── app.py                    # メインアプリケーション（LangGraph統合済み）
├── backend/                  # バックエンドモジュール
│   ├── auth/                 # 認証関連
│   ├── history/              # 会話履歴管理
│   ├── security/             # セキュリティ関連
│   └── settings.py           # 設定管理
├── frontend/                 # Reactフロントエンド
├── requirements.txt          # Python依存関係
└── README.md                 # このファイル
```

## 🔗 関連ドキュメント

- [APP_SERVICE_DEPLOYMENT.md](../APP_SERVICE_DEPLOYMENT.md): デプロイセンター設定ガイド
- [ENV_SETTINGS.md](../ENV_SETTINGS.md): 環境変数設定ガイド
- [既存Web全文検索システム-実装ガイド](../../SOMPOシステムズ_エージェンティックRAG構築%20-%20ドキュメント/020_Poc検証/既存Web全文検索システム_MVP2環境/mdファイル/既存Web全文検索システム-実装ガイド.md)
