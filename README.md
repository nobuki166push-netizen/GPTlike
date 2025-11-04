# Azure OpenAI チャット Web アプリケーション

Microsoftのサンプルアプリを参考にした、Azure OpenAIサービスを使用したチャットライクなWebアプリケーションです。

## 機能

- Azure OpenAI APIとの統合
- リアルタイムチャットインターフェース
- レスポンシブデザイン
- TypeScript + React フロントエンド
- Node.js + Express バックエンド

## 前提条件

- Node.js (v16以上)
- npm または yarn
- Azure OpenAIリソースとAPIキー

## セットアップ

### 1. 依存関係のインストール

```bash
npm run install-all
```

または、手動でインストール：

```bash
# ルートディレクトリ
npm install

# クライアントディレクトリ
cd client
npm install
cd ..
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成：

```bash
cp .env.example .env
```

`.env`ファイルを編集して、Azure OpenAIの認証情報を設定：

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
PORT=3001
```

### 3. アプリケーションの起動

開発モードで起動（バックエンドとフロントエンドを同時に起動）：

```bash
npm run dev
```

または、個別に起動：

```bash
# バックエンドのみ
npm run server

# 別のターミナルでフロントエンドのみ
npm run client
```

### 4. ブラウザでアクセス

ブラウザで `http://localhost:3000` を開いてアプリケーションにアクセスします。

## プロジェクト構造

```
.
├── server/                 # バックエンドサーバー
│   ├── index.js           # Expressサーバーのエントリーポイント
│   └── routes/
│       └── chat.js        # チャットAPIエンドポイント
├── client/                 # フロントエンド（React）
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatInterface.tsx  # チャットUIコンポーネント
│   │   ├── App.tsx
│   │   └── index.tsx
│   └── package.json
├── package.json            # ルートパッケージ設定
├── .env.example           # 環境変数のテンプレート
└── README.md
```

## API エンドポイント

### POST /api/chat

チャットメッセージを送信し、AIからの応答を取得します。

**リクエストボディ:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "こんにちは"
    }
  ]
}
```

**レスポンス:**
```json
{
  "message": {
    "role": "assistant",
    "content": "こんにちは！何かお手伝いできることはありますか？"
  }
}
```

## ビルド

本番環境用にビルド：

```bash
npm run build
```

ビルドされたファイルは `client/build/` ディレクトリに生成されます。

## トラブルシューティング

### Azure OpenAIの設定エラー

- `.env`ファイルが正しく設定されているか確認してください
- Azure PortalでAPIキーとエンドポイントが正しいか確認してください
- デプロイメント名が正しいか確認してください

### ポートの競合

デフォルトでは、バックエンドは3001番ポート、フロントエンドは3000番ポートを使用します。
ポートが使用中の場合は、環境変数で変更できます。

## ライセンス

MIT
