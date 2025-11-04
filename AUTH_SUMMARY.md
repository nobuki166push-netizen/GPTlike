# 認証機能サマリー

## ✅ 実装完了した機能

### フロントエンド
- ✅ **MSAL.js 統合** - @azure/msal-browser, @azure/msal-react
- ✅ **ログイン/ログアウトUI** - ヘッダーにPersonaとボタンを表示
- ✅ **トークン自動取得** - acquireTokenSilent でトークンを取得
- ✅ **API呼び出し時にトークン送信** - Authorization: Bearer ヘッダー
- ✅ **環境変数対応** - `.env` ファイルで設定可能

### バックエンド
- ✅ **JWT トークン検証** - PyJWT + JWKS
- ✅ **認証デコレータ** - `@require_auth` で簡単に保護
- ✅ **オン/オフ切り替え** - `ENABLE_ENTRA_AUTH` 環境変数
- ✅ **ユーザー情報取得** - req.user_info でアクセス可能

## 🎯 使い方

### 開発環境（認証なし）

```bash
# local.settings.json
"ENABLE_ENTRA_AUTH": "false"
```

→ 認証なしで開発できます

### 本番環境（認証あり）

1. **App Registration を2つ作成:**
   - API用
   - フロントエンド用

2. **環境変数を設定:**
   - バックエンド: `ENABLE_ENTRA_AUTH=true`, `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`
   - フロントエンド: `VITE_ENTRA_CLIENT_ID`, `VITE_API_SCOPE`

3. **起動:**
   - ユーザーはログインボタンでサインイン
   - トークンが自動的に API に送信される

詳細は [ENTRA_AUTH_SETUP.md](ENTRA_AUTH_SETUP.md) を参照！

## 🔧 カスタマイズ例

### 特定の関数のみ保護

```python
from auth import require_auth

@app.route(route="chat", methods=["POST"])
@require_auth  # この関数のみ認証必須
def chat_function(req: func.HttpRequest):
    user_id = req.user_info.get('oid')
    user_name = req.user_info.get('preferred_username')
    # ...
```

### ユーザー情報を利用

```python
from auth import get_user_id, get_user_name

@require_auth
def my_function(req: func.HttpRequest):
    user_id = get_user_id(req)  # Azure AD object ID
    user_name = get_user_name(req)  # email or name
    
    # ユーザーごとのデータ管理など
    logger.info(f"Request from {user_name} ({user_id})")
```

## 📋 チェックリスト

- [ ] Azure Portal で App Registration を2つ作成
- [ ] スコープを公開（API側）
- [ ] API permissions を設定（フロントエンド側）
- [ ] 環境変数を設定（バックエンド & フロントエンド）
- [ ] ローカルでテスト
- [ ] Azure にデプロイ
- [ ] Redirect URI を本番URLに追加
- [ ] 本番環境でテスト
