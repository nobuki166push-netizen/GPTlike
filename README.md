# GPTlike - エージェンティックRAG on Azure Functions 🤖

Azure Functions上で動作する高度なエージェンティックRAGシステムです。**Microsoft Agent Framework**、Azure OpenAI、Azure AI Searchを活用した、インテリジェントなドキュメント検索と質問応答を提供します。

> 🚀 **すぐに始めたい？** → [クイックスタートガイド](QUICKSTART.md) をご覧ください！

## ✨ 主な機能

### 🎯 エージェンティックRAG
- **Microsoft Agent Framework**: Microsoftの公式エージェントフレームワーク（[GitHub](https://github.com/microsoft/agent-framework)）
- **OpenAI Function Calling**: ツールを自動選択して最適な回答を生成
- **複数の検索ツール**: ベクトル検索（FAISS）、Azure AI Search統合
- **インテリジェントな推論**: コンテキストを理解し、適切な情報を組み合わせて回答

### 🔌 Azure統合
- **Azure OpenAI Service**: GPT-4による高度な自然言語処理
- **Azure AI Search**: 大規模ドキュメントコレクションのハイブリッド検索
- **Azure Blob Storage**: ドキュメントの永続化と自動ロード
- **FAISS ベクトルストア**: 高速な類似度検索

### 🔐 セキュリティ
- **Entra ID（Azure AD）認証**: エンタープライズグレードの認証（[セットアップガイド](ENTRA_AUTH_SETUP.md)）
- **MSAL.js統合**: フロントエンドでのシームレスな認証体験
- **JWT トークン検証**: バックエンドでの安全なAPI保護
- **オン/オフ切り替え**: 開発環境では認証を無効化可能

### 🌐 API エンドポイント

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/api/chat` | POST | エージェンティックRAGで質問応答 |
| `/api/documents/load` | POST | ドキュメントをロード |
| `/api/health` | GET | ヘルスチェック |
| `/api/info` | GET | API情報 |

## 🚀 クイックスタート

### 前提条件

- Python 3.9以上
- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- Azureサブスクリプション
- 以下のAzureリソース（作成手順は後述）:
  - Azure OpenAI Service
  - Azure AI Search（オプション）
  - Azure Blob Storage（オプション）

### 1. Azure OpenAI Serviceのセットアップ

#### リソースを作成
```bash
# Azure OpenAI リソースを作成
az cognitiveservices account create \
  --name your-openai-resource \
  --resource-group your-resource-group \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# モデルをデプロイ（GPT-4）
az cognitiveservices account deployment create \
  --name your-openai-resource \
  --resource-group your-resource-group \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"

# Embeddingsモデルをデプロイ
az cognitiveservices account deployment create \
  --name your-openai-resource \
  --resource-group your-resource-group \
  --deployment-name text-embedding-ada-002 \
  --model-name text-embedding-ada-002 \
  --model-version "2" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

#### エンドポイントとAPIキーを取得
```bash
# エンドポイント
az cognitiveservices account show \
  --name your-openai-resource \
  --resource-group your-resource-group \
  --query "properties.endpoint" -o tsv

# APIキー
az cognitiveservices account keys list \
  --name your-openai-resource \
  --resource-group your-resource-group \
  --query "key1" -o tsv
```

### 2. Azure AI Search のセットアップ（オプション）

```bash
# Azure AI Search サービスを作成
az search service create \
  --name your-search-service \
  --resource-group your-resource-group \
  --sku basic \
  --location japaneast

# APIキーを取得
az search admin-key show \
  --service-name your-search-service \
  --resource-group your-resource-group
```

### 3. Azure Blob Storage のセットアップ（オプション）

```bash
# ストレージアカウントを作成
az storage account create \
  --name yourstorageaccount \
  --resource-group your-resource-group \
  --location japaneast \
  --sku Standard_LRS

# コンテナーを作成
az storage container create \
  --name documents \
  --account-name yourstorageaccount

# 接続文字列を取得
az storage account show-connection-string \
  --name yourstorageaccount \
  --resource-group your-resource-group
```

### 4. ローカル環境のセットアップ

#### 環境変数を設定

`.env.template`をコピーして`local.settings.json`を編集:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    
    "AZURE_OPENAI_ENDPOINT": "https://your-resource-name.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "your-api-key",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
    "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "text-embedding-ada-002",
    
    "AZURE_SEARCH_ENDPOINT": "https://your-search-service.search.windows.net",
    "AZURE_SEARCH_API_KEY": "your-search-api-key",
    "AZURE_SEARCH_INDEX_NAME": "gptlike-index",
    
    "AZURE_STORAGE_CONNECTION_STRING": "your-storage-connection-string",
    "AZURE_STORAGE_CONTAINER_NAME": "documents"
  }
}
```

#### 依存関係をインストール

```bash
# 仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt
```

#### ローカルで起動

**バックエンド（Azure Functions）:**
```bash
func start
```

**フロントエンド（別ターミナル）:**
```bash
cd frontend
npm install
npm run dev
```

- バックエンド: `http://localhost:7071`
- フロントエンド: `http://localhost:5173`

フロントエンドは自動的にバックエンドのAPIにプロキシします。

## 🎨 UIの使い方

### チャットUI

ブラウザで `http://localhost:5173` を開くと、Microsoft公式サンプルスタイルのチャットUIが表示されます。

#### 基本的な使い方

1. **ドキュメントをロード**: 
   - 右上の「📤」アイコンをクリック
   - ドキュメントのテキストを入力（複数の場合は`---`で区切る）
   - 「ロード」ボタンをクリック

2. **質問する**:
   - 下部のテキストボックスに質問を入力
   - 「送信」ボタンをクリック（またはEnterキー）

3. **エージェントの動作を確認**:
   - エージェントが自動的にツールを選択
   - 検索結果を基に回答を生成

### システム情報の確認

右上の「システム情報」ボタンをクリックすると：
- サービス名とバージョン
- 利用可能な機能一覧
が表示されます。

## 📖 API使用方法（プログラマティック）

### チャット（エージェンティックRAG）

```bash
curl -X POST http://localhost:7071/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ドキュメントの内容について教えてください"
  }'
```

レスポンス例:
```json
{
  "status": "success",
  "message": "ドキュメントの内容について教えてください",
  "answer": "検索結果に基づいた詳細な回答...",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### ドキュメントをロード

#### テキストから直接ロード

```bash
curl -X POST http://localhost:7071/api/documents/load \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "これは最初のドキュメントです。",
      "これは二番目のドキュメントです。"
    ],
    "metadata": [
      {"source": "doc1.txt"},
      {"source": "doc2.txt"}
    ]
  }'
```

#### Azure Blob Storageからロード

```bash
curl -X POST http://localhost:7071/api/documents/load \
  -H "Content-Type: application/json" \
  -d '{
    "from_blob": true,
    "container_name": "documents"
  }'
```

## ☁️ Azure へのデプロイ

### 1. Function App用のリソースを作成

```bash
# Azureにログイン
az login

# リソースグループを作成
az group create --name gptlike-rg --location japaneast

# ストレージアカウントを作成（Function App用）
az storage account create \
  --name gptlikefuncstorage \
  --resource-group gptlike-rg \
  --location japaneast \
  --sku Standard_LRS

# Function Appを作成
az functionapp create \
  --resource-group gptlike-rg \
  --consumption-plan-location japaneast \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name gptlike-func-app \
  --storage-account gptlikefuncstorage \
  --os-type Linux
```

### 2. 環境変数を設定

Azure Portal または Azure CLI で環境変数を設定:

```bash
# Azure OpenAI 設定
az functionapp config appsettings set \
  --name gptlike-func-app \
  --resource-group gptlike-rg \
  --settings \
  AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
  AZURE_OPENAI_API_KEY="your-api-key" \
  AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4" \
  AZURE_OPENAI_API_VERSION="2024-02-15-preview" \
  AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002"

# Azure AI Search 設定（オプション）
az functionapp config appsettings set \
  --name gptlike-func-app \
  --resource-group gptlike-rg \
  --settings \
  AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net" \
  AZURE_SEARCH_API_KEY="your-search-api-key" \
  AZURE_SEARCH_INDEX_NAME="gptlike-index"

# Azure Storage 設定（オプション）
az functionapp config appsettings set \
  --name gptlike-func-app \
  --resource-group gptlike-rg \
  --settings \
  AZURE_STORAGE_CONNECTION_STRING="your-storage-connection-string" \
  AZURE_STORAGE_CONTAINER_NAME="documents"
```

### 3. フロントエンドをビルドしてデプロイ

**簡単な方法（デプロイスクリプト使用）:**
```bash
./deploy.sh gptlike-func-app
```

**手動デプロイ:**
```bash
# フロントエンドをビルド
cd frontend
npm install
npm run build
cd ..

# Azure Functionsにデプロイ
func azure functionapp publish gptlike-func-app
```

### 4. デプロイ後の確認

```bash
# ヘルスチェック
curl https://gptlike-func-app.azurewebsites.net/api/health

# API情報
curl https://gptlike-func-app.azurewebsites.net/api/info
```

## 🎨 高度な使用例

### シナリオ1: 社内ドキュメント検索システム

```bash
# 1. ドキュメントをロード
curl -X POST https://your-app.azurewebsites.net/api/documents/load \
  -H "Content-Type: application/json" \
  -H "x-functions-key: YOUR_FUNCTION_KEY" \
  -d '{
    "texts": [
      "社内規定: 有給休暇は年間20日付与されます。",
      "社内規定: リモートワークは週3日まで可能です。"
    ]
  }'

# 2. 質問する
curl -X POST https://your-app.azurewebsites.net/api/chat \
  -H "Content-Type: application/json" \
  -H "x-functions-key: YOUR_FUNCTION_KEY" \
  -d '{
    "message": "リモートワークのルールについて教えてください"
  }'
```

### シナリオ2: Azure Blob Storageから自動ロード

```bash
# 1. ドキュメントをBlobにアップロード
az storage blob upload-batch \
  --destination documents \
  --source ./my-documents \
  --account-name yourstorageaccount

# 2. Function Appに自動ロードさせる
curl -X POST https://your-app.azurewebsites.net/api/documents/load \
  -H "Content-Type: application/json" \
  -H "x-functions-key: YOUR_FUNCTION_KEY" \
  -d '{
    "from_blob": true
  }'
```

## 🔧 カスタマイズとモデル切り替え

### LLMモデルの変更

環境変数でモデルを簡単に変更できます:

```bash
# local.settings.json または Azure Portal で設定
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
```

### カスタムツールの追加

`agent_rag.py`に新しいツールを追加する例:

```python
class CustomTool(AgentTool):
    """カスタムツール"""
    
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="カスタムツールの説明"
        )
    
    def execute(self, query: str) -> str:
        # カスタムロジック
        return "結果"
    
    def to_function_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "クエリ"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
```

### システムプロンプトのカスタマイズ

`agent_rag.py`の`_create_agent`メソッド内でプロンプトを編集:

```python
system_prompt = """あなたのカスタムシステムプロンプト...
"""
```

## 📚 プロジェクト構造

```
/workspace/
├── function_app.py                # Azure Function エンドポイント定義
├── agent_rag.py                   # Microsoft Agent FrameworkベースのエージェンティックRAG実装
├── auth.py                        # Entra ID認証とトークン検証
├── host.json                      # Azure Functions ランタイム設定
├── local.settings.json            # ローカル開発環境設定
├── requirements.txt               # Python依存関係
├── .env.template                  # 環境変数テンプレート
├── deploy.sh                      # デプロイスクリプト
├── staticwebapp.config.json       # 静的Webアプリ設定
├── README.md                      # このファイル
├── QUICKSTART.md                  # クイックスタートガイド
├── ENTRA_AUTH_SETUP.md            # Entra ID認証セットアップガイド
└── frontend/                      # Reactフロントエンド
    ├── src/
    │   ├── App.tsx                # メインアプリケーション（認証UI含む）
    │   ├── main.tsx               # エントリーポイント（MSAL統合）
    │   ├── authConfig.ts          # MSAL設定
    │   ├── components/
    │   │   └── Chat.tsx           # チャットUI
    │   ├── api.ts                 # APIクライアント（トークン送信）
    │   └── types.ts               # TypeScript型定義
    ├── .env.example               # 環境変数の例
    ├── package.json               # MSAL依存関係含む
    └── vite.config.ts
```

## 🏗️ アーキテクチャ

```
┌─────────────┐
│   クライアント   │
└──────┬──────┘
       │ HTTP Request
       ▼
┌──────────────────────┐
│  Azure Functions     │
│  (function_app.py)   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Microsoft Agent Framework    │
│  (agent_rag.py)              │
└──────┬───────────────────────┘
       │
       ├─► Azure OpenAI (GPT-4)
       │
       ├─► FAISS Vector Store
       │
       ├─► Azure AI Search
       │
       └─► Azure Blob Storage
```

## 🔐 セキュリティ・ベストプラクティス

### Entra ID 認証（推奨）
- **完全なセットアップガイド**: [ENTRA_AUTH_SETUP.md](ENTRA_AUTH_SETUP.md) を参照
- 本番環境では Entra ID 認証を有効化してください
- シングルサインオン（SSO）と統合可能
- ロールベースアクセス制御（RBAC）をサポート

### 認証の有効化

```bash
# local.settings.json（ローカル）
"ENABLE_ENTRA_AUTH": "true"
"ENTRA_TENANT_ID": "your-tenant-id"
"ENTRA_CLIENT_ID": "your-api-client-id"

# Azure Functions（本番）
az functionapp config appsettings set \
  --name gptlike-func-app \
  --resource-group gptlike-rg \
  --settings \
  ENABLE_ENTRA_AUTH="true" \
  ENTRA_TENANT_ID="your-tenant-id" \
  ENTRA_CLIENT_ID="your-api-client-id"
```

### APIキー管理
- Azure Key Vault を使用してシークレットを管理
```bash
az keyvault create --name gptlike-vault --resource-group gptlike-rg
az keyvault secret set --vault-name gptlike-vault \
  --name "AzureOpenAIKey" --value "your-key"
```

### ネットワーク
- Private Endpoint を使用して VNet 内に配置
- API Management でレート制限を実装

## 🐛 トラブルシューティング

### エージェントが初期化できない
```bash
# ログを確認
az functionapp log tail --name gptlike-func-app --resource-group gptlike-rg

# 環境変数を確認
az functionapp config appsettings list \
  --name gptlike-func-app \
  --resource-group gptlike-rg
```

### ドキュメントロードが失敗する
- Azure Blob Storage の接続文字列を確認
- コンテナー名が正しいか確認
- アクセス権限を確認

### Azure OpenAI でエラー
- デプロイ名が正しいか確認
- API バージョンの互換性を確認
- レート制限に達していないか確認

## 📊 パフォーマンス最適化

### コールドスタート対策
- Always On を有効化（Premium プラン）
- エージェントのシングルトンパターンを使用（実装済み）

### コスト最適化
- Consumption プランでコスト削減
- Azure AI Search の SKU を適切に選択
- ベクトルストアのサイズを管理

## 📖 参考資料

- [Microsoft Agent Framework (GitHub)](https://github.com/microsoft/agent-framework)
- [Azure Functions Python ガイド](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure AI Search](https://learn.microsoft.com/azure/search/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

## 🤝 コントリビューション

改善提案やバグ報告は Issue または Pull Request でお願いします。

## 📝 ライセンス

このプロジェクトはオープンソースです。
