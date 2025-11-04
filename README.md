# GPTlike - Azure Functions版

Azure Functions上で動作するGPTライクなAIサービスのエンドポイント実装です。

## 📋 機能

- **GPTlike エンドポイント** (`/api/gptlike`)
  - GET: ヘルスチェック
  - POST: メッセージ処理（AI処理ロジックを実装可能）

- **ヘルスチェックエンドポイント** (`/api/health`)
  - サービスの稼働状態を確認

## 🚀 ローカル開発

### 前提条件

- Python 3.9以上
- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- Azure サブスクリプション（デプロイ時）

### セットアップ

1. 仮想環境を作成・有効化:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows
```

2. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

3. ローカルで実行:
```bash
func start
```

サーバーが起動したら、以下のURLでアクセスできます:
- GPTlike: `http://localhost:7071/api/gptlike`
- Health: `http://localhost:7071/api/health`

### テスト方法

**GETリクエスト（ヘルスチェック）:**
```bash
curl http://localhost:7071/api/gptlike
```

**POSTリクエスト（メッセージ処理）:**
```bash
curl -X POST http://localhost:7071/api/gptlike \
  -H "Content-Type: application/json" \
  -d '{"message": "こんにちは、Azure Functions！"}'
```

## ☁️ Azure へのデプロイ

### 1. Azure にログイン
```bash
az login
```

### 2. リソースグループを作成
```bash
az group create --name gptlike-rg --location japaneast
```

### 3. ストレージアカウントを作成
```bash
az storage account create \
  --name gptlikestorage \
  --resource-group gptlike-rg \
  --location japaneast \
  --sku Standard_LRS
```

### 4. Function Appを作成
```bash
az functionapp create \
  --resource-group gptlike-rg \
  --consumption-plan-location japaneast \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name gptlike-func-app \
  --storage-account gptlikestorage \
  --os-type Linux
```

### 5. デプロイ
```bash
func azure functionapp publish gptlike-func-app
```

デプロイ後、以下のようなURLでアクセスできます:
- `https://gptlike-func-app.azurewebsites.net/api/gptlike`
- `https://gptlike-func-app.azurewebsites.net/api/health`

## 🔧 カスタマイズ

### AI処理の追加

`function_app.py` の `gptlike_function` 内で、実際のAI処理ロジックを実装できます:

```python
# Azure OpenAI や他のAIサービスを統合
# 例:
from openai import AzureOpenAI

client = AzureOpenAI(...)
response = client.chat.completions.create(...)
```

### 環境変数の設定

`local.settings.json`（ローカル）または Azure Portal の「構成」セクション（本番環境）で環境変数を設定できます:

```json
{
  "Values": {
    "OPENAI_API_KEY": "your-api-key",
    "OPENAI_ENDPOINT": "your-endpoint"
  }
}
```

## 📚 プロジェクト構造

```
/workspace/
├── function_app.py          # メインのFunction定義
├── host.json               # Azure Functions ランタイム設定
├── local.settings.json     # ローカル開発設定
├── requirements.txt        # Python依存関係
├── .funcignore            # デプロイ時に除外するファイル
├── .gitignore             # Git除外設定
└── README.md              # このファイル
```

## 🔐 セキュリティ

- デフォルトでは関数レベルの認証が有効です（`http_auth_level=func.AuthLevel.FUNCTION`）
- Function キーは Azure Portal の「関数」→「関数キー」で確認できます
- 本番環境では、API Management や Application Gateway の使用を検討してください

## 📖 参考資料

- [Azure Functions Python 開発者ガイド](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- [Azure CLI リファレンス](https://learn.microsoft.com/cli/azure/)

## 📝 ライセンス

このプロジェクトはオープンソースです。
