# App Service（Webアプリ）デプロイセンター設定ガイド

既存Web全文検索システム構成に合わせて、App Service（sample-app-aoai-chatGPT）をデプロイするためのデプロイセンター設定ガイドです。

## 📋 前提条件

- Azure App Serviceリソースが作成済みであること
- GitHubリポジトリにコードがプッシュされていること
- Azure Functions（AIエージェント）がデプロイ済みであること

## ⚠️ 重要な注意事項

**コンテナーレジストリ（ACR）やDockerイメージは不要です。**

既存Web全文検索システムの構成では、App Serviceは**コードベースのデプロイ**を使用します。以下の方法でデプロイできます：

- ✅ **GitHub Actions**（推奨）
- ✅ **Azure DevOps**
- ✅ **ローカルGit**
- ✅ **外部Git**
- ✅ **Azure CLI**（`az webapp up`）

**コンテナーベースのデプロイ（Docker、ACR）は使用しません。**

## 🏗️ Step 1: App Serviceリソースの作成（未作成の場合）

### 1.1 Azure Portalでの作成

1. Azure Portalにログイン
2. 「リソースの作成」をクリック
3. 「Web アプリ」を検索して選択
4. 「作成」をクリック
5. 以下の情報を入力：

   **基本設定：**
   - **サブスクリプション**: 既存のサブスクリプションを選択
   - **リソースグループ**: 既存のリソースグループを選択（または新規作成）
   - **名前**: 例）`sample-app-chat-<一意の文字列>`
   - **公開**: コード
   - **ランタイムスタック**: Python
   - **Version**: 3.11 または 3.10（推奨）
   - **オペレーティングシステム**: Linux（推奨）または Windows
   - **地域**: 既存のリソースと同じリージョンを推奨（例：Japan East）

   **ホスティング：**
   - **プランの種類**: 従量課金プラン（Consumption）または App Service プラン
   - **App Service プラン**: 既存のプランを選択、または新規作成

6. 「確認および作成」→「作成」をクリック
7. デプロイ完了を待つ（1-2分程度）

### 1.2 Azure CLIでの作成（オプション）

```bash
# App Serviceプランを作成（まだない場合）
az appservice plan create \
  --name <PLAN_NAME> \
  --resource-group <RG_NAME> \
  --sku B1 \
  --is-linux

# App Serviceを作成
az webapp create \
  --resource-group <RG_NAME> \
  --plan <PLAN_NAME> \
  --name <APP_SERVICE_NAME> \
  --runtime "PYTHON|3.11"
```

## 🔧 Step 2: デプロイセンターの設定

### 2.1 デプロイセンターへのアクセス

1. Azure PortalでApp Serviceリソースに移動
2. 左メニューから「デプロイ センター」を選択

### 2.2 ソースの選択

デプロイセンターで、以下のいずれかのソースを選択：

#### オプション1: GitHub（推奨）

**設定手順：**

1. **ソース**: 「GitHub」を選択
2. **GitHubアカウントの認証**:
   - 「承認」をクリック
   - GitHubにログインして、Azure App Serviceへのアクセスを許可
   - 必要に応じて、特定のリポジトリのみへのアクセスを許可

3. **組織・リポジトリ・ブランチの選択**:
   - **組織**: GitHubの組織名またはユーザー名を選択
   - **リポジトリ**: `sample-app-aoai-chatGPT` または該当するリポジトリを選択
   - **ブランチ**: `main` または `master` を選択

4. **ビルドプロバイダー**:
   - **GitHub Actions**（推奨）: GitHub Actionsワークフローを自動生成
   - **App Service build service**: Azure側でビルドを実行

5. **「保存」をクリック**

**GitHub Actionsワークフローの自動生成:**

Azureが自動的に `.github/workflows/` ディレクトリにワークフローファイルを作成します。このファイルは以下のような内容になります：

```yaml
name: Build and deploy Python app to Azure Web App - <APP_SERVICE_NAME>

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python version
        uses: actions/setup-python@v1
        with:
          python-version: '3.11'
      
      - name: Create and start virtual environment
        run: |
          python -m venv venv
          source venv/bin/activate
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v2
        with:
          app-name: '<APP_SERVICE_NAME>'
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

#### オプション2: Azure DevOps

1. **ソース**: 「Azure Repos」を選択
2. **組織・プロジェクト・リポジトリ・ブランチ**を選択
3. **ビルドプロバイダー**: 「App Service build service」を選択
4. **「保存」をクリック**

#### オプション3: ローカルGit

1. **ソース**: 「ローカルGit」を選択
2. **「保存」をクリック**
3. 表示されるGit URLを使用してローカルからプッシュ

#### オプション4: 外部Git

1. **ソース**: 「外部Git」を選択
2. **リポジトリURL**: GitリポジトリのURLを入力
3. **ブランチ**: デプロイするブランチを指定
4. **「保存」をクリック**

### 2.3 ビルド設定の確認

デプロイセンターで以下の設定を確認・調整：

1. **「設定」タブ**を選択
2. **ビルド設定**を確認：

   **Pythonアプリの場合：**
   - **スタック**: Python
   - **バージョン**: 3.11 または 3.10
   - **ビルドコマンド**: （空欄、または必要に応じて設定）
   - **開始コマンド**: `gunicorn --bind 0.0.0.0:8000 --timeout 600 backend.app:app` など

   **注意**: `sample-app-aoai-chatGPT` の場合は、`backend/app.py` がエントリーポイントです。

### 2.4 環境変数の設定

デプロイセンターとは別に、App Serviceの環境変数を設定する必要があります。

1. App Serviceリソースに移動
2. 左メニューから「設定」→「構成」を選択
3. 「+ 新しいアプリケーション設定」をクリック
4. 以下の環境変数を追加：

| 環境変数名 | 値の例 | 説明 |
|-----------|--------|------|
| `MCP_SERVER_URL` | `https://<FUNCTION_APP_NAME>.azurewebsites.net/api/mcp` | Azure Functions（AIエージェント）のエンドポイントURL |
| `AZURE_OPENAI_ENDPOINT` | `https://rgp-20251019-04.openai.azure.com/` | Azure OpenAI エンドポイント |
| `AZURE_OPENAI_API_KEY` | `sk-...` | Azure OpenAI APIキー |
| `AZURE_OPENAI_API_VERSION` | `2024-02-15-preview` | APIバージョン |
| `AZURE_OPENAI_MODEL` | `gpt-4o` | モデル名 |

5. **「保存」をクリック**

## 🚀 Step 3: デプロイの実行

### 3.1 自動デプロイ（GitHub Actions）

GitHub Actionsを選択した場合、以下のタイミングで自動デプロイが実行されます：

- **プッシュ時**: `main` ブランチにプッシュすると自動的にデプロイ
- **手動実行**: GitHub Actionsの「Run workflow」ボタンから手動実行

**デプロイの確認：**

1. GitHubリポジトリの「Actions」タブでデプロイの進捗を確認
2. Azure Portalの「デプロイ センター」→「ログ」タブでデプロイログを確認

### 3.2 手動デプロイ（Azure CLI）

```bash
# Azure CLIにログイン
az login

# デプロイ（zipファイルから）
az webapp deployment source config-zip \
  --resource-group <RG_NAME> \
  --name <APP_SERVICE_NAME> \
  --src <zip-file-path>
```

### 3.3 手動デプロイ（VS Code拡張機能）

1. VS Codeでプロジェクトを開く
2. 左サイドバーのAzureアイコンをクリック
3. 「App Service」→「Deploy to Web App」を選択
4. App Service名を選択
5. デプロイを確認

## ✅ Step 4: デプロイ後の確認

### 4.1 デプロイ状態の確認

1. Azure PortalでApp Serviceリソースに移動
2. 「デプロイ センター」→「ログ」タブでデプロイログを確認
3. エラーがないことを確認

### 4.2 アプリケーションの動作確認

1. App ServiceのURLにアクセス：
   ```
   https://<APP_SERVICE_NAME>.azurewebsites.net
   ```

2. チャットインターフェースが表示されることを確認

3. テスト質問を送信して、AIエージェント（Azure Functions）経由で検索が実行されることを確認

### 4.3 ログの確認

1. App Serviceリソース → 「監視」→ 「ログストリーム」でリアルタイムログを確認
2. 「設定」→ 「ログ」で詳細ログを有効化

## 🔧 Step 5: デプロイ設定のカスタマイズ

### 5.1 ビルドコマンドのカスタマイズ

デプロイセンターの「設定」タブで、カスタムビルドコマンドを設定できます：

```bash
# 例: 依存関係のインストールとビルド
cd backend && pip install -r requirements.txt
```

### 5.2 開始コマンドのカスタマイズ

**Gunicornを使用する場合：**

```bash
gunicorn --bind 0.0.0.0:8000 --timeout 600 --workers 4 backend.app:app
```

**Flask開発サーバーを使用する場合（開発環境のみ）：**

```bash
python backend/app.py
```

### 5.3 デプロイスロットの設定（オプション）

本番環境への影響を最小限に抑えるため、ステージングスロットを使用できます：

1. App Serviceリソース → 「デプロイ スロット」→ 「+ スロットの追加」
2. スロット名を入力（例: `staging`）
3. デプロイセンターで、スロットごとに異なるブランチを設定可能

## ⚠️ トラブルシューティング

### デプロイが失敗する場合

1. **ログを確認**:
   - 「デプロイ センター」→「ログ」タブでエラーメッセージを確認
   - GitHub Actionsのログを確認（GitHub Actionsを使用している場合）

2. **ビルドエラーの場合**:
   - `requirements.txt` に問題がないか確認
   - Pythonバージョンが正しいか確認
   - ビルドコマンドが正しいか確認

3. **起動エラーの場合**:
   - 開始コマンドが正しいか確認
   - 環境変数が正しく設定されているか確認
   - アプリケーションログを確認

### アプリケーションが起動しない場合

1. **ログストリームを確認**:
   - App Service → 「監視」→ 「ログストリーム」

2. **環境変数を確認**:
   - `MCP_SERVER_URL` が正しく設定されているか
   - Azure Functionsのエンドポイントが正しいか

3. **ネットワーク接続を確認**:
   - Azure Functionsへの接続が可能か
   - VNet統合が必要な場合、設定されているか

## 📝 関連ドキュメント

- [既存Web全文検索システム-実装ガイド](../SOMPOシステムズ_エージェンティックRAG構築%20-%20ドキュメント/020_Poc検証/既存Web全文検索システム_MVP2環境/mdファイル/既存Web全文検索システム-実装ガイド.md)
- [既存Web全文検索システム-設定値一覧](../SOMPOシステムズ_エージェンティックRAG構築%20-%20ドキュメント/020_Poc検証/既存Web全文検索システム_MVP2環境/mdファイル/既存Web全文検索システム-設定値一覧.md)
- [sample-app-aoai-chatGPT GitHubリポジトリ](https://github.com/microsoft/sample-app-aoai-chatGPT)

