# 🚀 クイックスタートガイド

GPTlike エージェンティックRAGを5分で始める！

## 📋 前提条件

- Python 3.9以上
- Node.js 18以上
- Azure Functions Core Tools v4
- Azureアカウント

## ⚡ 最速セットアップ

### 1. Azure OpenAI Serviceを作成

```bash
# リソースグループを作成
az group create --name gptlike-rg --location eastus

# Azure OpenAI を作成
az cognitiveservices account create \
  --name your-openai-resource \
  --resource-group gptlike-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# エンドポイントとキーを取得
az cognitiveservices account show \
  --name your-openai-resource \
  --resource-group gptlike-rg \
  --query "properties.endpoint" -o tsv

az cognitiveservices account keys list \
  --name your-openai-resource \
  --resource-group gptlike-rg \
  --query "key1" -o tsv
```

### 2. モデルをデプロイ

Azure Portal で以下のモデルをデプロイ：
- **GPT-4** (デプロイ名: `gpt-4`)
- **text-embedding-ada-002** (デプロイ名: `text-embedding-ada-002`)

### 3. プロジェクトをセットアップ

```bash
# 仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt

# フロントエンドをセットアップ
cd frontend
npm install
cd ..
```

### 4. 環境変数を設定

`local.settings.json` を編集：

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    
    "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "your-api-key-here",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
    "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-ada-002"
  }
}
```

### 5. 起動！

**ターミナル1 - バックエンド:**
```bash
func start
```

**ターミナル2 - フロントエンド:**
```bash
cd frontend
npm run dev
```

### 6. ブラウザで開く

`http://localhost:5173` を開いてチャット開始！🎉

## 🎯 最初の使い方

1. **ドキュメントをロード**
   - 右上の「📤」アイコンをクリック
   - 以下のテキストを入力：
   ```
   Azure OpenAIは、OpenAIのGPT-4やGPT-3.5などの強力な言語モデルをAzureクラウド上で利用できるサービスです。
   ---
   Microsoft Agent Frameworkは、AIエージェントを構築するための公式フレームワークです。
   ```
   - 「ロード」をクリック

2. **質問してみる**
   ```
   Azure OpenAIについて教えてください
   ```

3. **エージェントの動作を観察** 🤖
   - 自動的にドキュメント検索ツールを使用
   - 関連情報を取得して回答を生成

## 🐛 トラブルシューティング

### エラー: "Azure OpenAI endpoint not configured"
→ `local.settings.json` の設定を確認

### フロントエンドがAPIに接続できない
→ バックエンド（Functions）が起動しているか確認（`http://localhost:7071`）

### ドキュメント検索が動作しない
→ まずドキュメントをロードしてください

## 📚 次のステップ

- [完全なREADME](README.md) を読む
- [Azure AI Search統合](README.md#2-azure-ai-search-のセットアップ) を設定
- [Azure Blob Storage](README.md#3-azure-blob-storage-のセットアップ) を追加
- [Azureにデプロイ](README.md#☁️-azure-へのデプロイ)

## 💡 ヒント

- **Shift + Enter** で改行
- **Enter** で送信
- チャットをクリアするには右上の「🗑️」アイコン
- システム情報を見るには「システム情報」ボタン

楽しいチャットを！🚀
