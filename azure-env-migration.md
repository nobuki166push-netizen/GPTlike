# Azure環境変数移行ガイド

現在のGPTlikeプロジェクトの環境変数を、既存Web全文検索システム構成に移行するためのガイドです。

## 📊 現在の設定状況

現在のAzure Functionsに設定されている環境変数：

```json
[
  {
    "name": "APPLICATIONINSIGHTS_CONNECTION_STRING",
    "value": "InstrumentationKey=690da65e-01a4-442e-9944-6d1d034db345;..."
  },
  {
    "name": "AZURE_AISEARCH_ENDPOINT",
    "value": "https://amap-search-001.search.windows.net/"
  },
  {
    "name": "AZURE_AISEARCH_KEY",
    "value": "YOUR_AZURE_SEARCH_KEY_HERE"
  },
  {
    "name": "AZURE_OPENAI_ENDPOINT",
    "value": "https://rgp-20251019-04.openai.azure.com/"
  },
  {
    "name": "AZURE_OPENAI_KEY",
    "value": "YOUR_AZURE_OPENAI_KEY_HERE"
  },
  {
    "name": "AzureWebJobsStorage",
    "value": "DefaultEndpointsProtocol=https;AccountName=amapstorage001;..."
  },
  {
    "name": "DEPLOYMENT_STORAGE_CONNECTION_STRING",
    "value": "DefaultEndpointsProtocol=https;AccountName=amapstorage001;..."
  }
]
```

## 🔄 移行マッピング

### 既存設定の保持

以下の設定はそのまま保持します：

- ✅ `APPLICATIONINSIGHTS_CONNECTION_STRING` → そのまま保持
- ✅ `AzureWebJobsStorage` → そのまま保持
- ✅ `DEPLOYMENT_STORAGE_CONNECTION_STRING` → そのまま保持
- ✅ `AZURE_OPENAI_ENDPOINT` → そのまま保持

### 名前変更が必要な設定

以下の設定は名前を変更する必要があります：

| 現在の名前 | 新しい名前 | アクション |
|-----------|----------|----------|
| `AZURE_OPENAI_KEY` | `AZURE_OPENAI_API_KEY` | 値をコピーして新しい名前で設定後、古い設定を削除 |
| `AZURE_AISEARCH_ENDPOINT` | `AZURE_SEARCH_ENDPOINT` | 値をコピーして新しい名前で設定後、古い設定を削除 |
| `AZURE_AISEARCH_KEY` | `AZURE_SEARCH_KEY` | 値をコピーして新しい名前で設定後、古い設定を削除 |

### 新規追加が必要な設定

#### 必須設定

| 環境変数名 | 値の例 | 説明 |
|-----------|--------|------|
| `AZURE_OPENAI_API_VERSION` | `2024-02-15-preview` | Azure OpenAI APIバージョン |
| `AZURE_COSMOSDB_ENDPOINT` | `https://your-cosmos-account.documents.azure.com:443/` | Cosmos DBエンドポイント（ログ保存用） |
| `AZURE_COSMOSDB_KEY` | `your-cosmos-key` | Cosmos DBキー（ログ保存用） |

#### オプション設定（推奨）

| 環境変数名 | 値の例 | 説明 |
|-----------|--------|------|
| `SEARCH_BASE_URL` | `http://10.x.x.x:8080` | FESS/OpenSearchのベースURL（全文検索用） |
| `AZURE_SEARCH_INDEX_NAME` | `default-index` | Azure AI Searchインデックス名 |
| `COSMOS_DATABASE_NAME` | `SearchLogs` | ログDB名（既定: SearchLogs） |
| `COSMOS_CONTAINER_NAME` | `ProcessLogs` | ログコンテナ名（既定: ProcessLogs） |
| `LLM_MODEL` | `gpt-4o` | 使用するLLMモデル名 |
| `CHUNK_SIZE` | `10` | 1チャンクあたりの文書数 |
| `RELEVANCE_THRESHOLD` | `0.3` | 関連性フィルタリングの閾値 |

## 📋 Azure Portalでの設定手順

### Step 1: 既存設定の確認

1. Azure Portal → Function Appリソースに移動
2. 「設定」→「構成」を選択
3. 現在の設定を確認

### Step 2: 新しい環境変数の追加

1. 「+ 新しいアプリケーション設定」をクリック
2. 以下の順序で追加：

#### 必須設定の追加

```
名前: AZURE_OPENAI_API_KEY
値: （既存のAZURE_OPENAI_KEYの値をコピー）

名前: AZURE_OPENAI_API_VERSION
値: 2024-02-15-preview

名前: AZURE_SEARCH_ENDPOINT
値: https://amap-search-001.search.windows.net/
（既存のAZURE_AISEARCH_ENDPOINTの値をコピー）

名前: AZURE_SEARCH_KEY
値: （既存のAZURE_AISEARCH_KEYの値をコピー）

名前: AZURE_COSMOSDB_ENDPOINT
値: （Cosmos DBアカウントのエンドポイント）

名前: AZURE_COSMOSDB_KEY
値: （Cosmos DBアカウントのキー）
```

#### オプション設定の追加（推奨）

```
名前: AZURE_SEARCH_INDEX_NAME
値: default-index

名前: SEARCH_BASE_URL
値: （FESS/OpenSearchのURL、例: http://10.x.x.x:8080）

名前: COSMOS_DATABASE_NAME
値: SearchLogs

名前: COSMOS_CONTAINER_NAME
値: ProcessLogs

名前: LLM_MODEL
値: gpt-4o

名前: CHUNK_SIZE
値: 10

名前: RELEVANCE_THRESHOLD
値: 0.3
```

### Step 3: 古い設定の削除

新しい設定が正しく追加されたことを確認後、以下の古い設定を削除：

- `AZURE_OPENAI_KEY` → `AZURE_OPENAI_API_KEY` に移行済み
- `AZURE_AISEARCH_ENDPOINT` → `AZURE_SEARCH_ENDPOINT` に移行済み
- `AZURE_AISEARCH_KEY` → `AZURE_SEARCH_KEY` に移行済み

### Step 4: 設定の保存

1. 「保存」をクリック
2. 確認ダイアログで「続行」をクリック
3. Function Appが再起動されるのを待つ

## ✅ 設定確認チェックリスト

移行完了後、以下の設定が正しく行われているか確認してください：

- [ ] `AZURE_OPENAI_API_KEY` が設定されている（`AZURE_OPENAI_KEY` から移行）
- [ ] `AZURE_OPENAI_ENDPOINT` が設定されている（既存）
- [ ] `AZURE_OPENAI_API_VERSION` が設定されている（新規）
- [ ] `AZURE_SEARCH_ENDPOINT` が設定されている（`AZURE_AISEARCH_ENDPOINT` から移行）
- [ ] `AZURE_SEARCH_KEY` が設定されている（`AZURE_AISEARCH_KEY` から移行）
- [ ] `AZURE_COSMOSDB_ENDPOINT` が設定されている（新規）
- [ ] `AZURE_COSMOSDB_KEY` が設定されている（新規）
- [ ] `APPLICATIONINSIGHTS_CONNECTION_STRING` が設定されている（既存）
- [ ] `AzureWebJobsStorage` が設定されている（既存）

## 🔗 関連リソースの作成

### Cosmos DBアカウントの作成（未作成の場合）

1. Azure Portal → 「リソースの作成」→ 「Azure Cosmos DB」
2. API: **Core (SQL)** を選択
3. サブスクリプション、リソースグループを選択
4. アカウント名を入力（例: `gptlike-cosmos-001`）
5. 場所を選択（既存リソースと同じリージョンを推奨）
6. 「確認および作成」→「作成」
7. デプロイ完了後、エンドポイントとキーを取得

### Azure AI Searchインデックスの確認・作成

既存のAzure AI Searchリソース（`amap-search-001`）にインデックスが存在するか確認：

1. Azure Portal → Azure AI Searchリソースに移動
2. 「インデックス」を確認
3. インデックスが存在しない場合は作成が必要（Mem0が自動的に作成する場合もあります）

## ⚠️ 注意事項

1. **機密情報の取り扱い**
   - APIキーや接続文字列は機密情報です
   - gitリポジトリにはコミットしないでください
   - `local.settings.json` は `.gitignore` に含まれています

2. **設定変更のタイミング**
   - コードのデプロイ前に環境変数を設定してください
   - 環境変数変更後、Function Appが自動的に再起動されます

3. **VNet統合**
   - FESS/OpenSearchがプライベートIPの場合は、VNet統合が必要です
   - 従量課金プランではVNet統合が利用できません
   - PremiumプランまたはApp Serviceプランへの変更が必要です

4. **設定値の確認**
   - 移行後、Function Appのログを確認してエラーがないか確認してください
   - テストリクエストを送信して動作確認を行ってください

