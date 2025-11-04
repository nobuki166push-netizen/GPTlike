# アーキテクチャドキュメント

このドキュメントでは、アプリケーションの技術的なアーキテクチャと設計について説明します。

## 📐 システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                        ユーザー                              │
│                      (ブラウザ)                              │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/HTTPS
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  フロントエンド                              │
│              (React + TypeScript)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  UI Components                                      │   │
│  │  - ChatContainer: メインコンテナ                    │   │
│  │  - ChatMessage: メッセージ表示                      │   │
│  │  - ChatInput: 入力フォーム                          │   │
│  └─────────────────────────────────────────────────────┘   │
│              Port: 3000 (Vite/Nginx)                        │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
                     │ /api/conversation
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   バックエンド                               │
│                (Python + Flask)                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API Endpoints                                      │   │
│  │  - POST /api/conversation: チャット処理             │   │
│  │  - POST /api/clear: 履歴クリア                      │   │
│  │  - GET /api/health: ヘルスチェック                  │   │
│  └─────────────────────────────────────────────────────┘   │
│              Port: 5000 (Flask/Gunicorn)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ Azure OpenAI SDK
                     │ HTTPS + API Key
                     │
┌────────────────────▼────────────────────────────────────────┐
│                Azure OpenAI Service                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  GPT Models                                         │   │
│  │  - gpt-35-turbo                                     │   │
│  │  - gpt-4                                            │   │
│  │  - その他のデプロイ済みモデル                       │   │
│  └─────────────────────────────────────────────────────┘   │
│              Endpoint: *.openai.azure.com                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ フロントエンドアーキテクチャ

### 技術スタック

- **React 18**: UIライブラリ
- **TypeScript**: 型安全な開発
- **Vite**: 高速なビルドツール
- **Axios**: HTTP クライアント
- **Marked**: マークダウンパーサー
- **DOMPurify**: XSS対策

### コンポーネント構造

```
src/
├── App.tsx                    # ルートコンポーネント
├── App.css                    # グローバルスタイル
├── main.tsx                   # エントリーポイント
├── index.css                  # ベーススタイル
└── components/
    ├── ChatContainer.tsx      # メインコンテナ
    ├── ChatContainer.css      # コンテナスタイル
    ├── ChatMessage.tsx        # メッセージコンポーネント
    ├── ChatMessage.css        # メッセージスタイル
    ├── ChatInput.tsx          # 入力コンポーネント
    └── ChatInput.css          # 入力スタイル
```

### データフロー

```
User Input
    ↓
ChatInput (入力受付)
    ↓
ChatContainer (状態管理)
    ↓
Axios (HTTP リクエスト)
    ↓
Backend API
    ↓
Azure OpenAI
    ↓
Backend API (レスポンス)
    ↓
ChatContainer (状態更新)
    ↓
ChatMessage (表示)
    ↓
User (返答表示)
```

### 状態管理

**useState を使用したシンプルな状態管理:**

```typescript
// ChatContainer.tsx
const [messages, setMessages] = useState<Message[]>([])
const [isLoading, setIsLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
```

**Message 型定義:**

```typescript
interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}
```

---

## 🔧 バックエンドアーキテクチャ

### 技術スタック

- **Python 3.11**: プログラミング言語
- **Flask**: 軽量Webフレームワーク
- **Azure OpenAI SDK**: OpenAI API クライアント
- **Flask-CORS**: CORS対応
- **Gunicorn**: プロダクション用WSGIサーバー

### API エンドポイント

#### POST /api/conversation

チャット会話を処理します。

**リクエスト:**
```json
{
  "messages": [
    {"role": "user", "content": "こんにちは"},
    {"role": "assistant", "content": "こんにちは！"},
    {"role": "user", "content": "天気は？"}
  ],
  "stream": false
}
```

**レスポンス:**
```json
{
  "message": "AIの返答内容",
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 50,
    "total_tokens": 75
  }
}
```

#### POST /api/clear

会話履歴をクリアします（フロントエンド側で管理）。

**レスポンス:**
```json
{
  "status": "cleared"
}
```

#### GET /api/health

ヘルスチェックエンドポイント。

**レスポンス:**
```json
{
  "status": "healthy"
}
```

### Azure OpenAI 統合

```python
from openai import AzureOpenAI

# クライアントの初期化
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# チャット補完リクエスト
response = client.chat.completions.create(
    model=DEPLOYMENT_NAME,
    messages=messages,
    temperature=0.7,
    max_tokens=800
)
```

---

## 🔐 セキュリティ

### 実装済みのセキュリティ対策

1. **API キーの保護**
   - 環境変数での管理
   - `.env` ファイルを `.gitignore` に追加
   - サーバーサイドでのみ使用

2. **CORS 設定**
   - Flask-CORS による適切なオリジン制御
   - 開発環境では柔軟に、本番環境では厳密に

3. **XSS 対策**
   - DOMPurify によるHTMLサニタイゼーション
   - マークダウンコンテンツの安全な表示

4. **入力検証**
   - 空のメッセージの拒否
   - トークン数の制限
   - エラーハンドリング

### 推奨する追加対策

1. **認証・認可**
   - Azure AD B2C
   - JWT トークン
   - ロールベースアクセス制御

2. **レート制限**
   - Flask-Limiter の導入
   - ユーザーごとのリクエスト制限

3. **HTTPS 強制**
   - 本番環境では必須
   - Let's Encrypt などの証明書

4. **ログ管理**
   - Azure Application Insights
   - センシティブ情報のマスキング

---

## 📊 データフロー詳細

### 1. ユーザーメッセージ送信

```
ユーザー入力
    ↓
ChatInput.handleSend()
    ↓
ChatContainer.handleSendMessage(content)
    ↓
messages 配列に追加
    ↓
axios.post('/api/conversation', { messages })
    ↓
Flask: /api/conversation エンドポイント
    ↓
Azure OpenAI API 呼び出し
    ↓
GPT モデルが応答生成
    ↓
Flask: レスポンス返却
    ↓
ChatContainer: messages 配列に追加
    ↓
ChatMessage で表示
```

### 2. エラーハンドリング

```
エラー発生
    ↓
try-catch でキャッチ
    ↓
エラーメッセージを設定
    ↓
エラーバナー表示
    ↓
ユーザーメッセージを削除（ロールバック）
    ↓
ローディング状態解除
```

---

## 🚀 パフォーマンス最適化

### フロントエンド

1. **React の最適化**
   - メモ化（useMemo, useCallback）の活用
   - 仮想スクロールの検討（長い会話履歴）

2. **バンドルサイズ削減**
   - Code Splitting
   - Tree Shaking
   - 動的インポート

3. **キャッシング**
   - Service Worker
   - ブラウザキャッシュ

### バックエンド

1. **接続プーリング**
   - Azure OpenAI クライアントの再利用
   - セッション管理

2. **レスポンスキャッシング**
   - Redis などのキャッシュ層
   - 同じ質問への素早い応答

3. **非同期処理**
   - ストリーミングレスポンス
   - WebSocket の活用

---

## 🐳 Docker 構成

### docker-compose.yml

```yaml
services:
  backend:
    - Python 環境
    - Flask アプリケーション
    - ポート: 5000
    
  frontend:
    - Node.js ビルド環境
    - Nginx サーバー
    - ポート: 3000
    - バックエンドへのプロキシ
```

### ネットワーク

```
app-network (bridge)
    ├── backend:5000
    └── frontend:3000
```

---

## 📈 スケーラビリティ

### 水平スケーリング

1. **フロントエンド**
   - CDN 配信（Azure CDN）
   - 静的ファイルのグローバル配信

2. **バックエンド**
   - 複数インスタンスの起動
   - ロードバランサー（Azure Load Balancer）
   - Azure Container Apps でのオートスケール

### 垂直スケーリング

1. **Azure OpenAI**
   - トークン制限の引き上げ
   - 複数のデプロイメントの利用
   - より強力なモデルへの移行

---

## 🔄 CI/CD パイプライン（推奨）

```
Git Push
    ↓
GitHub Actions / Azure DevOps
    ↓
┌─────────────────┬─────────────────┐
│   Frontend      │    Backend      │
│   - npm test    │    - pytest     │
│   - npm build   │    - flake8     │
│   - docker build│    - docker build│
└────────┬────────┴────────┬────────┘
         │                 │
         ↓                 ↓
   Azure Static Web Apps   Azure Container Apps
   or Azure App Service    or Azure App Service
         │                 │
         └────────┬────────┘
                  ↓
            本番環境デプロイ
```

---

## 📝 ログとモニタリング

### 推奨ツール

1. **Azure Application Insights**
   - アプリケーションログ
   - パフォーマンスメトリクス
   - エラートラッキング

2. **Azure Monitor**
   - インフラストラクチャ監視
   - アラート設定

3. **ログレベル**
   ```python
   logging.INFO   # 通常の操作
   logging.WARNING  # 警告
   logging.ERROR  # エラー
   logging.DEBUG  # デバッグ情報
   ```

---

## 🧪 テスト戦略

### フロントエンド

- **単体テスト**: Jest + React Testing Library
- **E2Eテスト**: Playwright / Cypress
- **コンポーネントテスト**: Storybook

### バックエンド

- **単体テスト**: pytest
- **統合テスト**: pytest + Flask test client
- **API テスト**: pytest + requests

---

## 📚 参考アーキテクチャ

このプロジェクトは以下のパターンを採用しています：

- **3-Tier Architecture**: フロントエンド / バックエンド / 外部サービス
- **RESTful API**: 標準的なHTTP メソッドとステータスコード
- **Stateless Design**: サーバー側で会話状態を保持しない
- **Microservices Ready**: 各サービスが独立してスケール可能

---

**最終更新日: 2024-11-04**
