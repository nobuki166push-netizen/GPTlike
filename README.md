# Azure OpenAI チャット Web アプリ

Microsoft のサンプル [sample-app-aoai-chatGPT](https://github.com/microsoft/sample-app-aoai-chatGPT) を参考に、Azure OpenAI と連携したチャットライクな Web アプリケーションを実装しました。FastAPI ベースのバックエンドと、Vite + React によるフロントエンドで構成されています。

## 構成

- `backend/`: FastAPI アプリケーション。Azure OpenAI へのリクエストを仲介します。
- `frontend/`: Vite + React 製チャット UI。`npm run build` の成果物はバックエンドから配信されます。
- `.env.sample`: 必要な環境変数の雛形。
- `start.sh`: 仮想環境のセットアップ、フロントエンドのビルド、バックエンドの起動を一括で行うスクリプト。

## 事前準備

1. Azure OpenAI リソースを作成し、チャットモデル（例: `gpt-4o` や `gpt-35-turbo`）をデプロイします。
2. `.env.sample` を参考に `.env` を作成し、各種値を設定します。

```bash
cp .env.sample .env
# 必要な値を編集
```

## ローカル開発 / 実行

```bash
chmod +x start.sh
./start.sh
```

- バックエンド: `http://localhost:8000`
- フロントエンド: `http://localhost:8000`（ビルド済み静的ファイルを FastAPI が配信）

開発中にフロントエンドをホットリロードしたい場合は、別ターミナルで次を実行します。

```bash
cd frontend
npm install
npm run dev
```

その際は `.env` に `CORS_ALLOW_ORIGIN=http://localhost:5173` を追加してください。

## デプロイのヒント

- Azure App Service にデプロイする場合は、`start.sh` を参考にデプロイ前にフロントエンドをビルドし、`uvicorn backend.main:app` をスタートアップコマンドに設定します。
- 環境変数は Azure ポータルまたは IaC（Bicep / ARM / Terraform など）で設定してください。

## ライセンス

このリポジトリは MIT ライセンスの下で提供されます。詳しくは `LICENSE` を参照してください。