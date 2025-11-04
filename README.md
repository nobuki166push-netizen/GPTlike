# Azure OpenAI チャットアプリケーション

Azure OpenAI を使用したチャットライクなWebアプリケーションです。Microsoft の [sample-app-aoai-chatGPT](https://github.com/microsoft/sample-app-aoai-chatGPT) を参考に実装されています。

## 機能

- 💬 リアルタイムなチャット機能
- 🎨 モダンで美しいUI/UX
- 🔄 会話履歴の管理
- 📱 レスポンシブデザイン
- 🚀 Azure OpenAI との統合
- ⚡ 高速なレスポンス
- 🎯 マークダウン形式のレスポンス表示

## 技術スタック

### フロントエンド
- React 18
- TypeScript
- Vite
- Axios
- Marked (マークダウンパーサー)
- DOMPurify (XSS対策)

### バックエンド
- Python 3.11
- Flask
- Azure OpenAI SDK
- Gunicorn

## プロジェクト構造

```
/workspace/
├── backend/              # Pythonバックエンド
│   ├── app.py           # メインアプリケーション
│   ├── requirements.txt # Python依存関係
│   ├── Dockerfile       # Dockerイメージ定義
│   └── .env.example     # 環境変数サンプル
├── frontend/            # Reactフロントエンド
│   ├── src/
│   │   ├── components/  # Reactコンポーネント
│   │   ├── App.tsx      # メインアプリケーション
│   │   └── main.tsx     # エントリーポイント
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf       # Nginx設定
├── docker-compose.yml   # Docker Compose設定
└── README.md
```

## セットアップ

### 前提条件

- Node.js 18以上
- Python 3.11以上
- **Azure OpenAI リソースとAPIキー**（[Azure設定ガイド](./docs/AZURE_SETUP.md)を参照）

または

- Docker と Docker Compose

### ⚠️ 重要: 最初にAzureポータルで設定が必要です

アプリケーションを起動する前に、Azureポータル側でリソースの作成とモデルのデプロイが必要です。

**👉 [Azure ポータル設定ガイド](./docs/AZURE_SETUP.md) を先に確認してください。**

このガイドでは以下の手順を詳しく説明しています：
1. Azure OpenAI リソースの作成
2. GPTモデルのデプロイ
3. APIキーとエンドポイントの取得
4. コストの見積もりと注意点

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd workspace
```

### 2. 環境変数の設定

バックエンド用の環境変数を設定します：

```bash
# ルートディレクトリに .env ファイルを作成
cp .env.example .env

# または backend/.env でも可
cp backend/.env.example backend/.env
```

`.env` ファイルを編集して、Azure OpenAI の認証情報を設定：

```env
AZURE_OPENAI_API_KEY=your_actual_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 3. ローカル開発環境でのセットアップ

#### バックエンドのセットアップ

```bash
cd backend

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# アプリケーションの起動
python app.py
```

バックエンドは `http://localhost:5000` で起動します。

#### フロントエンドのセットアップ

別のターミナルで：

```bash
cd frontend

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

フロントエンドは `http://localhost:3000` で起動します。

### 4. Dockerを使用したセットアップ

より簡単な方法として、Docker Composeを使用できます：

```bash
# ルートディレクトリで実行
docker-compose up --build
```

これにより、フロントエンドとバックエンドが自動的に起動します：
- フロントエンド: `http://localhost:3000`
- バックエンドAPI: `http://localhost:5000`

## 使い方

1. ブラウザで `http://localhost:3000` にアクセス
2. テキストボックスにメッセージを入力
3. 「送信」ボタンをクリックするか、Enterキーを押す
4. AIからの返答を待つ
5. 会話を続ける
6. 「クリア」ボタンで会話履歴をクリア可能

### キーボードショートカット

- `Enter`: メッセージを送信
- `Shift + Enter`: 改行を挿入

## APIエンドポイント

### POST /api/conversation
チャット会話を処理します。

**リクエストボディ:**
```json
{
  "messages": [
    {"role": "user", "content": "こんにちは"},
    {"role": "assistant", "content": "こんにちは！"}
  ],
  "stream": false
}
```

**レスポンス:**
```json
{
  "message": "AIの返答",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### POST /api/clear
会話履歴をクリアします。

### GET /api/health
ヘルスチェックエンドポイント。

## カスタマイズ

### Azure OpenAI モデルの変更

`backend/.env` ファイルで `AZURE_OPENAI_DEPLOYMENT_NAME` を変更：

```env
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### UIテーマの変更

`frontend/src/App.css` でカラー変数をカスタマイズできます：

```css
.app.dark {
  --bg-primary: #1a1a1a;
  --accent-color: #0078d4;
  /* その他の変数 */
}
```

## トラブルシューティング

### バックエンドが起動しない

- Azure OpenAI の認証情報が正しく設定されているか確認
- `.env` ファイルが正しい場所にあるか確認
- Python の仮想環境が有効化されているか確認

### フロントエンドがバックエンドに接続できない

- バックエンドが起動しているか確認（`http://localhost:5000/api/health` にアクセス）
- `frontend/vite.config.ts` のプロキシ設定を確認

### CORS エラーが発生する

- バックエンドの `app.py` で CORS が正しく設定されているか確認
- 開発中は `flask-cors` が有効になっていることを確認

## デプロイ

### Azure App Service へのデプロイ

1. Azure CLI でログイン
2. リソースグループを作成
3. App Service プランを作成
4. Web アプリを作成
5. 環境変数を設定
6. コードをデプロイ

詳細は [Azure のドキュメント](https://docs.microsoft.com/azure/app-service/) を参照してください。

### Docker を使用したデプロイ

```bash
# イメージのビルド
docker-compose build

# コンテナの起動
docker-compose up -d
```

## ライセンス

MIT

## 参考リンク

- [Azure OpenAI Service](https://azure.microsoft.com/services/cognitive-services/openai-service/)
- [Microsoft Sample App](https://github.com/microsoft/sample-app-aoai-chatGPT)
- [React ドキュメント](https://react.dev/)
- [Flask ドキュメント](https://flask.palletsprojects.com/)

## 貢献

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容について議論してください。
