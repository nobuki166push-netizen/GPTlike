# Entra ID（Azure AD）認証セットアップガイド

GPTlike に Entra ID（旧Azure AD）認証を統合する完全ガイドです。

## 📋 前提条件

- Azure サブスクリプション
- Azure Portal へのアクセス権限
- App Registration を作成する権限

## 🚀 セットアップ手順

### 1. App Registration を作成（API用）

#### Azure Portal で設定

1. **Azure Portal** → **Entra ID** → **App registrations** → **New registration**

2. アプリを登録:
   ```
   Name: GPTlike API
   Supported account types: Single tenant
   Redirect URI: (空白のまま)
   ```

3. **登録後、以下をメモ:**
   - `Application (client) ID` → これが **API の Client ID**
   - `Directory (tenant) ID` → これが **Tenant ID**

#### スコープを公開

1. **Expose an API** に移動
2. **Add a scope** をクリック
3. スコープを追加:
   ```
   Scope name: access_as_user
   Who can consent: Admins and users
   Admin consent display name: Access GPTlike API
   Admin consent description: Allows the app to access GPTlike API as the signed-in user
   State: Enabled
   ```
4. **Application ID URI** をメモ（例: `api://12345678-1234-1234-1234-123456789012`）

### 2. App Registration を作成（フロントエンド用）

#### Azure Portal で設定

1. **Azure Portal** → **Entra ID** → **App registrations** → **New registration**

2. アプリを登録:
   ```
   Name: GPTlike Frontend
   Supported account types: Single tenant
   Redirect URI:
     - Type: Single-page application (SPA)
     - URI: http://localhost:5173 (開発用)
           https://your-app.azurewebsites.net (本番用)
   ```

3. **登録後、以下をメモ:**
   - `Application (client) ID` → これが **フロントエンドの Client ID**

#### API アクセス許可を追加

1. **API permissions** に移動
2. **Add a permission** をクリック
3. **My APIs** タブを選択
4. 先ほど作成した **GPTlike API** を選択
5. **access_as_user** スコープを選択
6. **Add permissions** をクリック
7. （オプション）**Grant admin consent** をクリック

### 3. 環境変数を設定

#### バックエンド（local.settings.json）

```json
{
  "Values": {
    ...
    "ENABLE_ENTRA_AUTH": "true",
    "ENTRA_TENANT_ID": "your-tenant-id-here",
    "ENTRA_CLIENT_ID": "your-api-client-id-here"
  }
}
```

#### フロントエンド（frontend/.env）

```bash
VITE_ENTRA_CLIENT_ID=your-frontend-client-id-here
VITE_ENTRA_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
VITE_REDIRECT_URI=http://localhost:5173
VITE_API_SCOPE=api://your-api-client-id/access_as_user
```

### 4. Azure Functions にデプロイ時の設定

```bash
# Entra ID 認証を有効化
az functionapp config appsettings set \
  --name gptlike-func-app \
  --resource-group gptlike-rg \
  --settings \
  ENABLE_ENTRA_AUTH="true" \
  ENTRA_TENANT_ID="your-tenant-id" \
  ENTRA_CLIENT_ID="your-api-client-id"
```

## 🧪 テスト

### ローカルでテスト

1. **バックエンドを起動:**
   ```bash
   func start
   ```

2. **フロントエンドを起動:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **ブラウザで確認:**
   - `http://localhost:5173` を開く
   - 「ログイン」ボタンをクリック
   - Entra ID でサインイン
   - チャットを試す

### トークンを確認

ブラウザの開発者ツール → Network タブで:
- リクエストヘッダーに `Authorization: Bearer eyJ...` が含まれていることを確認

## 🔧 カスタマイズ

### 特定のAPIエンドポイントのみ認証を要求

`function_app.py` で個別に認証を適用:

```python
from auth import require_auth

@app.route(route="chat", methods=["POST"])
@require_auth  # この関数のみ認証が必要
def chat_function(req: func.HttpRequest) -> func.HttpResponse:
    # req.user_info にユーザー情報が含まれる
    user_id = req.user_info.get('oid')  # ユーザーID
    user_name = req.user_info.get('preferred_username')  # ユーザー名
    ...
```

### 認証なしで一部のエンドポイントを許可

```python
# healthエンドポイントは認証不要
@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    # 認証なしでアクセス可能
    ...
```

## 🐛 トラブルシューティング

### エラー: "AADSTS50011: The reply URL specified in the request does not match"

→ App Registration の Redirect URI に現在のURLを追加してください

### エラー: "Invalid token audience"

→ `ENTRA_CLIENT_ID`（バックエンド）が API の Client ID と一致しているか確認

### エラー: "AADSTS65001: The user or administrator has not consented"

→ Azure Portal で **API permissions** → **Grant admin consent** をクリック

### トークンが取得できない

→ フロントエンドの `.env` ファイルの設定を確認
→ `VITE_API_SCOPE` が正しい形式か確認（`api://...`）

### 認証を一時的に無効化

開発中に認証を無効化したい場合:

```bash
# local.settings.json
"ENABLE_ENTRA_AUTH": "false"
```

## 📚 参考資料

- [Microsoft identity platform documentation](https://learn.microsoft.com/entra/identity-platform/)
- [MSAL.js documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [Azure Functions authentication](https://learn.microsoft.com/azure/azure-functions/functions-bindings-http-webhook-trigger#authorization-keys)

## 🎯 次のステップ

- [ ] マルチテナント対応
- [ ] ロールベースアクセス制御（RBAC）
- [ ] カスタムクレームの追加
- [ ] Conditional Access の設定
