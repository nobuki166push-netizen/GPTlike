# クイックスタートガイド

このガイドでは、最短でアプリケーションを動かすための手順を説明します。

## 🚀 5ステップで始める

### ステップ 1️⃣: Azureポータルで準備（初回のみ）

**所要時間: 約10分**

1. **Azure OpenAI リソースを作成**
   - [Azure ポータル](https://portal.azure.com) にアクセス
   - 「リソースの作成」→「Azure OpenAI」を検索
   - リソースを作成（詳細は [AZURE_SETUP.md](./AZURE_SETUP.md) 参照）

2. **モデルをデプロイ**
   - [Azure OpenAI Studio](https://oai.azure.com/) にアクセス
   - 「デプロイ」から「gpt-35-turbo」をデプロイ
   - デプロイ名を「`gpt-35-turbo`」にする

3. **APIキーを取得**
   - Azure ポータルのリソース画面
   - 「キーとエンドポイント」をクリック
   - 以下をメモ：
     - ✅ キー 1
     - ✅ エンドポイント

**👉 詳しい手順は [AZURE_SETUP.md](./AZURE_SETUP.md) をご覧ください。**

---

### ステップ 2️⃣: リポジトリをクローン

```bash
git clone <repository-url>
cd workspace
```

---

### ステップ 3️⃣: 環境変数を設定

```bash
# .envファイルを作成
cp .env.example .env
```

`.env` ファイルを編集して、ステップ1で取得した情報を設定：

```bash
# Azure OpenAI の情報を入力
AZURE_OPENAI_API_KEY=ここにキー1を貼り付け
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

### ステップ 4️⃣: アプリケーションを起動

#### 🐳 方法A: Docker を使う（推奨・簡単）

```bash
docker-compose up --build
```

#### 💻 方法B: ローカル環境で起動

**バックエンド:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**フロントエンド（別ターミナル）:**
```bash
cd frontend
npm install
npm run dev
```

---

### ステップ 5️⃣: ブラウザでアクセス

ブラウザで以下にアクセス：

```
http://localhost:3000
```

**🎉 成功！チャットアプリが起動しました！**

---

## 💬 使い方

1. テキストボックスにメッセージを入力
2. 「送信」ボタンをクリック（または Enter キー）
3. AIからの返答を待つ
4. 会話を続ける
5. 「クリア」ボタンで会話をリセット

---

## 🔧 トラブルシューティング

### Q: バックエンドが起動しない

**A: 環境変数を確認してください**

```bash
# バックエンドディレクトリで確認
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('AZURE_OPENAI_API_KEY')[:10] + '...' if os.getenv('AZURE_OPENAI_API_KEY') else 'Not set')"
```

### Q: "401 Unauthorized" エラー

**A: APIキーが間違っている可能性があります**

1. Azure ポータルで正しいキーをコピーしているか確認
2. `.env` ファイルに正しく貼り付けられているか確認
3. キーの前後にスペースがないか確認

### Q: "404 Not Found" エラー

**A: デプロイ名が間違っている可能性があります**

1. Azure OpenAI Studio で実際のデプロイ名を確認
2. `.env` の `AZURE_OPENAI_DEPLOYMENT_NAME` と一致させる

### Q: フロントエンドがバックエンドに接続できない

**A: バックエンドが起動しているか確認してください**

```bash
# 別ターミナルで確認
curl http://localhost:5000/api/health
# {"status":"healthy"} が返ってくればOK
```

### Q: Docker が起動しない

**A: ポートが使用中の可能性があります**

```bash
# 使用中のポートを確認
lsof -i :5000  # バックエンド
lsof -i :3000  # フロントエンド

# プロセスを終了するか、docker-compose.yml でポートを変更
```

---

## 📚 詳細ドキュメント

- **[AZURE_SETUP.md](./AZURE_SETUP.md)** - Azure ポータルでの詳細な設定手順
- **[README.md](../README.md)** - プロジェクト全体の説明
- **[API仕様](../backend/app.py)** - バックエンド API の詳細

---

## 💰 コストについて

### 開発・テスト段階の概算

**gpt-35-turbo を使用した場合:**
- 1回の会話: 約 ¥0.15
- 100回の会話: 約 ¥15
- 1日のテスト: 約 ¥150〜300

**💡 コスト削減のヒント:**
- テストが終わったらリソースを停止または削除
- トークン制限を低めに設定
- Azure Cost Management でコストを監視

---

## 🎯 次のステップ

✅ アプリが動いたら：

1. **UIをカスタマイズ**
   - `frontend/src/App.css` でデザイン変更
   - `frontend/src/components/` でコンポーネント追加

2. **機能を追加**
   - 会話履歴の保存
   - ユーザー認証
   - ファイルアップロード

3. **本番環境にデプロイ**
   - Azure App Service
   - Azure Container Apps
   - Azure Static Web Apps + Functions

---

## 🆘 サポート

問題が解決しない場合：

1. **ドキュメントを確認**
   - [AZURE_SETUP.md](./AZURE_SETUP.md) の「よくある問題」セクション
   - [README.md](../README.md) のトラブルシューティング

2. **ログを確認**
   ```bash
   # バックエンドのログ
   cd backend
   python app.py
   
   # Dockerのログ
   docker-compose logs -f
   ```

3. **GitHub Issues で質問**
   - プロジェクトのリポジトリで Issue を作成

---

**それでは、楽しいチャットアプリ開発を！🚀**
