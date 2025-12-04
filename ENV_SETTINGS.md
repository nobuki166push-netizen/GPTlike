# 環境変数設定ガイド

このドキュメントでは、既存Web全文検索システム構成に必要な環境変数の設定方法を説明します。

## 📋 設定方法

### 1. ローカル開発環境

`local.settings.json.example` をコピーして `local.settings.json` を作成し、実際の値を設定してください。

```bash
cp local.settings.json.example local.settings.json
```

**注意**: `local.settings.json` は `.gitignore` に含まれているため、gitにはコミットされません。

### 2. Azure Functions（本番環境）

Azure Portalで以下の環境変数を設定してください。

## 🔑 必須設定

### Azure OpenAI

| 環境変数名 | 説明 | 現在の設定値からのマッピング |
|-----------|------|---------------------------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI エンドポイント | 既存: `AZURE_OPENAI_ENDPOINT` ✅ |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI APIキー | 既存: `AZURE_OPENAI_KEY` → **変更必要** |
| `AZURE_OPENAI_API_VERSION` | APIバージョン | 新規追加（例: `2024-02-15-preview`） |

### Cosmos DB（ログ保存用）

| 環境変数名 | 説明 | 現在の設定値からのマッピング |
|-----------|------|---------------------------|
| `AZURE_COSMOSDB_ENDPOINT` | Cosmos DBエンドポイント | 新規追加 |
| `AZURE_COSMOSDB_KEY` | Cosmos DBキー | 新規追加 |

### 外部検索（FESS/OpenSearch）

| 環境変数名 | 説明 | 現在の設定値からのマッピング |
|-----------|------|---------------------------|
| `SEARCH_BASE_URL` | FESS/OpenSearchのベースURL | 新規追加（例: `http://10.x.x.x:8080`） |

## 🔧 オプション設定

### Azure AI Search（Mem0用・セマンティック検索用）

| 環境変数名 | 説明 | 現在の設定値からのマッピング |
|-----------|------|---------------------------|
| `AZURE_SEARCH_ENDPOINT` | Azure AI Searchエンドポイント | 既存: `AZURE_AISEARCH_ENDPOINT` → **変更必要** |
| `AZURE_SEARCH_KEY` | Azure AI Searchキー | 既存: `AZURE_AISEARCH_KEY` → **変更必要** |
| `AZURE_SEARCH_INDEX_NAME` | インデックス名 | 新規追加（既定: `default-index`） |

### グラフ検索（知識グラフ用）

| 環境変数名 | 説明 |
|-----------|------|
| `GRAPH_SEARCH_ENDPOINT` | グラフ検索エンドポイント |
| `GRAPH_SEARCH_KEY` | グラフ検索キー |

### Cosmos DB（オプション設定）

| 環境変数名 | 説明 | 既定値 |
|-----------|------|--------|
| `COSMOS_DATABASE_NAME` | ログDB名 | `SearchLogs` |
| `COSMOS_CONTAINER_NAME` | ログコンテナ名 | `ProcessLogs` |

### チューニング用パラメータ

| 環境変数名 | 説明 | 既定値 |
|-----------|------|--------|
| `CHUNK_SIZE` | 1チャンクあたりの文書数 | `10` |
| `RELEVANCE_THRESHOLD` | 関連性フィルタリングの閾値 | `0.3` |
| `FESS_SEARCH_LIMIT` | FESS検索の結果上限数 | `20` |
| `SEMANTIC_SEARCH_TOP` | セマンティック検索の結果上限数 | `20` |
| `GRAPH_SEARCH_LIMIT` | グラフ検索の結果上限数 | `20` |
| `GRAPH_SEARCH_DEPTH` | グラフ検索の探索深度 | `2` |
| `FESS_PARALLEL_WORKERS` | FESS検索の並列実行数 | `3` |
| `MAX_EXPANDED_KEYWORDS` | クエリ拡張の最大キーワード数 | `3` |
| `SEARCH_TIMEOUT_SECONDS` | 検索API呼び出しのタイムアウト（秒） | `10` |
| `LIST_DISPLAY_LIMIT` | 資料一覧型の表示件数上限 | `50` |
| `SEMANTIC_CONFIGURATION_NAME` | セマンティック検索の設定名 | `default` |
| `SEMANTIC_QUERY_LANGUAGE` | セマンティック検索のクエリ言語 | `ja-JP` |
| `LLM_MODEL` | 使用するLLMモデル名 | `gpt-4o` |

### その他

| 環境変数名 | 説明 |
|-----------|------|
| `LANGCHAIN_TRACING_V2` | LangSmithトレース有効化（`true`/`false`） |
| `LANGCHAIN_API_KEY` | LangSmith APIキー |

## 🔄 既存設定からの移行

現在のAzure Functionsに設定されている環境変数から、新しい構成への移行が必要です：

### 変更が必要な環境変数

1. **`AZURE_OPENAI_KEY` → `AZURE_OPENAI_API_KEY`**
   - 既存の値を新しい名前で設定

2. **`AZURE_AISEARCH_ENDPOINT` → `AZURE_SEARCH_ENDPOINT`**
   - 既存の値を新しい名前で設定

3. **`AZURE_AISEARCH_KEY` → `AZURE_SEARCH_KEY`**
   - 既存の値を新しい名前で設定

### 追加が必要な環境変数

- `AZURE_OPENAI_API_VERSION` (必須)
- `AZURE_COSMOSDB_ENDPOINT` (必須)
- `AZURE_COSMOSDB_KEY` (必須)
- `SEARCH_BASE_URL` (FESS/OpenSearchを使用する場合)
- `AZURE_SEARCH_INDEX_NAME` (オプション)
- その他のチューニング用パラメータ（オプション）

## 📝 Azure Portalでの設定手順

1. Azure Portalにログイン
2. Function Appリソースに移動
3. 左メニューから「設定」→「構成」を選択
4. 「+ 新しいアプリケーション設定」をクリック
5. 上記の環境変数を追加
6. 既存の環境変数名を変更する場合は、古い設定を削除して新しい名前で追加
7. 「保存」をクリック

## ⚠️ 注意事項

- 機密情報（APIキー、接続文字列など）はgitにコミットしないでください
- `local.settings.json` は `.gitignore` に含まれています
- Azure Portalでの設定変更後、Function Appの再起動が必要な場合があります
- VNet統合が必要な場合（FESS/OpenSearchがプライベートIPの場合）、従量課金プランからPremiumプランまたはApp Serviceプランへの変更が必要です

## 🔗 関連ドキュメント

- [既存Web全文検索システム-実装ガイド](../SOMPOシステムズ_エージェンティックRAG構築%20-%20ドキュメント/020_Poc検証/既存Web全文検索システム_MVP2環境/mdファイル/既存Web全文検索システム-実装ガイド.md)
- [既存Web全文検索システム-設定値一覧](../SOMPOシステムズ_エージェンティックRAG構築%20-%20ドキュメント/020_Poc検証/既存Web全文検索システム_MVP2環境/mdファイル/既存Web全文検索システム-設定値一覧.md)

