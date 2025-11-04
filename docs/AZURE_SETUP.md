# Azure ポータル設定ガイド

このアプリケーションを動かすために、Azureポータル側で事前に行う必要がある設定手順をまとめています。

## 📋 目次

1. [前提条件](#前提条件)
2. [Azure OpenAI リソースの作成](#azure-openai-リソースの作成)
3. [モデルのデプロイ](#モデルのデプロイ)
4. [APIキーとエンドポイントの取得](#apiキーとエンドポイントの取得)
5. [必要な情報のまとめ](#必要な情報のまとめ)

---

## 前提条件

### 必要なもの

- ✅ **Azure アカウント**
  - まだない場合: https://azure.microsoft.com/ja-jp/free/ で無料アカウントを作成
  
- ✅ **Azure OpenAI サービスへのアクセス権限**
  - Azure OpenAI は申請が必要なサービスです
  - 申請フォーム: https://aka.ms/oai/access
  - 承認まで数日〜数週間かかる場合があります

- ✅ **有効なサブスクリプション**
  - 無料試用版でも可能ですが、リソースの制限に注意

---

## Azure OpenAI リソースの作成

### ステップ 1: Azureポータルにログイン

1. https://portal.azure.com にアクセス
2. Azureアカウントでログイン

### ステップ 2: Azure OpenAI リソースを作成

1. **「リソースの作成」** をクリック
   - または検索バーで「Azure OpenAI」と検索

2. **「Azure OpenAI」** を選択して **「作成」** をクリック

3. **基本情報を入力:**

   | 項目 | 入力例 | 説明 |
   |------|--------|------|
   | **サブスクリプション** | お使いのサブスクリプション | 課金されるサブスクリプション |
   | **リソースグループ** | `rg-openai-chat` | 新規作成または既存を選択 |
   | **リージョン** | `East US` または `Japan East` | 利用可能なリージョンを選択 |
   | **名前** | `openai-chat-app-20241104` | グローバルで一意な名前 |
   | **価格レベル** | `Standard S0` | 通常はこれを選択 |

4. **「確認および作成」** をクリック

5. 検証が完了したら **「作成」** をクリック

6. デプロイが完了するまで待つ（通常1〜2分）

7. **「リソースに移動」** をクリック

---

## モデルのデプロイ

Azure OpenAI リソースを作成しただけでは使えません。使用するAIモデルをデプロイする必要があります。

### ステップ 1: Azure OpenAI Studio にアクセス

1. 作成した Azure OpenAI リソースのページで、**「概要」** タブを表示

2. 上部にある **「Azure OpenAI Studio に移動」** ボタンをクリック
   - または直接 https://oai.azure.com/ にアクセス

### ステップ 2: モデルをデプロイ

1. 左側のメニューから **「デプロイ」** または **「Deployments」** をクリック

2. **「+ 新しいデプロイの作成」** または **「+ Create new deployment」** をクリック

3. **デプロイ設定を入力:**

   | 項目 | 推奨値 | 説明 |
   |------|--------|------|
   | **モデル** | `gpt-35-turbo` または `gpt-4` | チャット用モデル |
   | **モデルバージョン** | 最新版（自動更新） | 通常は最新を選択 |
   | **デプロイ名** | `gpt-35-turbo` | この名前を.envファイルで使用 |
   | **コンテンツフィルター** | デフォルト | 有害コンテンツをフィルタリング |
   | **1分あたりのトークン数制限** | `10K` 〜 `120K` | 予算に応じて設定 |

4. **「作成」** をクリック

5. デプロイが完了するまで待つ（数秒〜1分程度）

### 推奨モデル

| モデル | 用途 | コスト | 推奨度 |
|--------|------|--------|--------|
| **gpt-35-turbo** | チャット、会話 | 💰 低い | ⭐⭐⭐ 初心者向け |
| **gpt-35-turbo-16k** | 長文チャット | 💰💰 中程度 | ⭐⭐ |
| **gpt-4** | 高度な推論 | 💰💰💰 高い | ⭐⭐⭐ 本番向け |
| **gpt-4-32k** | 超長文処理 | 💰💰💰💰 非常に高い | ⭐ 特殊用途 |

**開発・テスト段階では `gpt-35-turbo` を推奨します。**

---

## APIキーとエンドポイントの取得

### ステップ 1: Azure ポータルでキーを確認

1. Azure ポータルに戻る（https://portal.azure.com）

2. 作成した Azure OpenAI リソースを開く
   - 検索バーでリソース名を入力して検索

3. 左側メニューの **「キーとエンドポイント」** または **「Keys and Endpoint」** をクリック

4. 以下の情報をメモ：

   ```
   ✅ キー 1（KEY 1）
      例: 1234567890abcdef1234567890abcdef
   
   ✅ エンドポイント（ENDPOINT）
      例: https://your-resource-name.openai.azure.com/
   
   ✅ リージョン（LOCATION）
      例: eastus
   ```

   **⚠️ 重要: キーは絶対に公開しないでください！**

### ステップ 2: API バージョンを確認

現在の推奨APIバージョン:
- `2024-02-15-preview` (最新)
- `2023-12-01-preview`
- `2023-05-15` (安定版)

通常は `2024-02-15-preview` を使用します。

---

## 必要な情報のまとめ

Azureポータルでの設定が完了したら、以下の情報が揃います：

### 📝 .env ファイルに設定する情報

```bash
# 1. APIキー（キーとエンドポイントページから取得）
AZURE_OPENAI_API_KEY=ここにキー1の値を貼り付け

# 2. エンドポイント（キーとエンドポイントページから取得）
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/

# 3. デプロイ名（Azure OpenAI Studioで設定した名前）
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo

# 4. APIバージョン（通常はこのまま）
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 🔍 情報の確認方法

| 項目 | 確認場所 |
|------|----------|
| `AZURE_OPENAI_API_KEY` | Azure ポータル > リソース > キーとエンドポイント > キー 1 |
| `AZURE_OPENAI_ENDPOINT` | Azure ポータル > リソース > キーとエンドポイント > エンドポイント |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI Studio > デプロイ > デプロイ名 |
| `AZURE_OPENAI_API_VERSION` | 通常は `2024-02-15-preview` を使用 |

---

## 接続テスト

### Azure OpenAI Studio でテスト

1. Azure OpenAI Studio（https://oai.azure.com/）にアクセス

2. 左メニューから **「チャット」** または **「Chat Playground」** を選択

3. デプロイしたモデルを選択

4. チャットボックスに「こんにちは」と入力してテスト

5. 正常に返答があれば、設定は成功です ✅

### コマンドラインでテスト（オプション）

```bash
curl https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME/chat/completions?api-version=2024-02-15-preview \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "こんにちは"}
    ]
  }'
```

---

## よくある問題と解決方法

### ❌ エラー: "Access Denied" または "401 Unauthorized"

**原因:**
- APIキーが間違っている
- APIキーの権限が不足している

**解決方法:**
1. Azure ポータルで正しいキーをコピーしているか確認
2. キーの前後にスペースが入っていないか確認
3. キー2を試してみる

---

### ❌ エラー: "Resource not found" または "404"

**原因:**
- エンドポイントURLが間違っている
- デプロイ名が間違っている

**解決方法:**
1. エンドポイントURLの末尾に `/` があることを確認
2. Azure OpenAI Studio でデプロイ名を確認
3. デプロイが正常に完了しているか確認

---

### ❌ エラー: "Rate limit exceeded" または "429"

**原因:**
- 1分あたりのリクエスト制限を超えている

**解決方法:**
1. Azure OpenAI Studio のデプロイ設定でトークン制限を増やす
2. アプリケーション側でリクエスト頻度を制限する
3. より高いティアにアップグレードする

---

### ❌ エラー: "The API deployment for this resource does not exist"

**原因:**
- モデルがまだデプロイされていない
- デプロイ名が`.env`ファイルと一致していない

**解決方法:**
1. Azure OpenAI Studio でモデルがデプロイされているか確認
2. デプロイ名と`.env`の`AZURE_OPENAI_DEPLOYMENT_NAME`が一致しているか確認

---

## コストの見積もり

### 料金体系（目安）

| モデル | 入力トークン | 出力トークン |
|--------|------------|------------|
| **gpt-35-turbo** | $0.0015 / 1K tokens | $0.002 / 1K tokens |
| **gpt-4** | $0.03 / 1K tokens | $0.06 / 1K tokens |

### 概算例

**gpt-35-turbo を使用した場合:**
- 1回の会話（往復）: 約500トークン = $0.001（約0.15円）
- 1000回の会話: 約$1（約150円）
- 1ヶ月の開発テスト: 約$10〜50（約1,500〜7,500円）

**💡 コスト削減のヒント:**
- 開発・テストは `gpt-35-turbo` を使用
- 不要なリソースは削除する
- トークン制限を適切に設定する
- Azure Cost Management でコストを監視する

---

## リソースの削除

### テストが終わったら

使用しなくなったリソースは削除してコストを節約しましょう：

1. Azure ポータルで Azure OpenAI リソースを開く
2. 上部の **「削除」** をクリック
3. リソース名を入力して確認
4. **「削除」** をクリック

または、リソースグループごと削除：

1. リソースグループを開く
2. **「リソースグループの削除」** をクリック
3. リソースグループ名を入力して確認
4. **「削除」** をクリック

---

## 次のステップ

Azure側の設定が完了したら：

1. ✅ このドキュメントで取得した情報を `/workspace/.env` ファイルに設定
2. ✅ `README.md` の手順に従ってアプリケーションを起動
3. ✅ `http://localhost:3000` にアクセスして動作確認

---

## 参考リンク

- [Azure OpenAI Service ドキュメント](https://learn.microsoft.com/ja-jp/azure/cognitive-services/openai/)
- [Azure OpenAI Studio](https://oai.azure.com/)
- [価格の詳細](https://azure.microsoft.com/ja-jp/pricing/details/cognitive-services/openai-service/)
- [クイックスタート](https://learn.microsoft.com/ja-jp/azure/cognitive-services/openai/quickstart)
- [APIリファレンス](https://learn.microsoft.com/ja-jp/azure/cognitive-services/openai/reference)

---

## サポート

問題が発生した場合：
1. このドキュメントの「よくある問題と解決方法」を確認
2. Azure ポータルの「サポート」からチケットを作成
3. Microsoft Learn Q&A で質問: https://learn.microsoft.com/ja-jp/answers/

---

**最終更新日: 2024-11-04**
