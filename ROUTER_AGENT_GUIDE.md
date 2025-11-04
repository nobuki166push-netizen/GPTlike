# Router Agent パターン - 真のエージェンティックRAG 🤖

## 🎯 これが真のエージェンティックRAG

### 従来のシンプルRAG vs Router Agent

#### ❌ シンプルRAG（以前の実装）
```
ユーザー質問 → ベクトル検索 → LLM生成 → 回答
```
**問題点:**
- すべての質問に同じアプローチ
- 質問の種類を考慮しない
- ツールの選択肢がない
- **エージェント的ではない**

#### ✅ Router Agent（新実装）
```
ユーザー質問
    ↓
意図分類（LLM）
    ↓
┌─────────┬──────────┬──────────┬──────────┐
│事実検索  │意味検索   │要約      │比較      │
│→キーワード│→ベクトル  │→検索+要約│→検索+分析│
└─────────┴──────────┴──────────┴──────────┘
    ↓
最終回答生成（コンテキスト統合）
```
**利点:**
- ✅ **質問の意図を理解**
- ✅ **最適なツールを自動選択**
- ✅ **複数ツールの組み合わせ**
- ✅ **真のエージェント動作**

## 🧠 Router Agent の仕組み

### 1. 意図分類（Intent Classification）

質問を7つのカテゴリに自動分類:

| 意図 | 説明 | 例 |
|------|------|-----|
| `factual_search` | 特定の事実を探す | 「Azure OpenAIの価格は？」 |
| `semantic_search` | 概念・意味検索 | 「クラウドセキュリティについて教えて」 |
| `summarization` | 要約を求める | 「この文書をまとめて」 |
| `comparison` | 比較分析 | 「AとBの違いは？」 |
| `analysis` | 分析・考察 | 「なぜこうなった？」 |
| `multi_hop` | 複数ステップ | 「Aを調べて、それに基づいてBを分析」 |
| `unknown` | その他 | - |

### 2. ツール選択（Tool Selection）

意図に応じて最適なツールを自動選択:

```python
intent_to_tools = {
    factual_search: ["keyword_search", "semantic_search"],
    semantic_search: ["semantic_search"],
    summarization: ["semantic_search", "summarization"],
    comparison: ["comparison"],
    # ...
}
```

### 3. ツール実行（Tool Execution）

#### 利用可能なツール

1. **SemanticSearchTool**
   - FAISS ベクトル検索
   - 意味的類似度で検索
   - スコアリング付き

2. **KeywordSearchTool**
   - Azure AI Search使用
   - 正確な用語検索
   - フルテキスト検索

3. **SummarizationTool**
   - GPT-4で要約
   - 箇条書き形式
   - 重要ポイント抽出

4. **ComparisonTool**
   - 複数情報を収集
   - 比較分析
   - 違い・共通点を明確化

### 4. 回答生成（Answer Generation）

ツール実行結果を統合して最終回答:

```python
def _generate_final_answer(query, intent, tool_results):
    # 1. ツール結果を整形
    # 2. 意図に応じたプロンプト選択
    # 3. LLMで統合回答生成
    return final_answer
```

## 💡 実際の動作例

### 例1: 事実検索

**質問:** 「Azure OpenAIとは何ですか？」

```
Step 1: 意図分類 → factual_search
Step 2: ツール選択 → keyword_search + semantic_search
Step 3: ツール実行
  - keyword_search: "Azure OpenAI" で検索
  - semantic_search: 意味的に関連する文書を検索
Step 4: 回答生成
  → 両方の結果を統合して正確な定義を回答
```

### 例2: 比較質問

**質問:** 「Azure OpenAIとOpenAI APIの違いは？」

```
Step 1: 意図分類 → comparison
Step 2: ツール選択 → comparison
Step 3: ツール実行
  - 両方に関する情報を検索
  - GPT-4で比較分析
Step 4: 回答生成
  → 違いを明確に説明
```

### 例3: 要約リクエスト

**質問:** 「この製品の機能をまとめて」

```
Step 1: 意図分類 → summarization
Step 2: ツール選択 → semantic_search + summarization
Step 3: ツール実行
  - 関連文書を検索
  - 要約ツールで箇条書き化
Step 4: 回答生成
  → 簡潔な要約を提示
```

## 🔧 カスタマイズ

### 新しいツールを追加

```python
class CustomTool(KnowledgeTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="カスタムツールの説明"
        )
    
    def execute(self, query: str, context: Dict = None):
        # カスタムロジック
        return {
            "success": True,
            "result": "..."
        }

# Router Agentに追加
router_agent.tools["custom_tool"] = CustomTool()
router_agent.intent_to_tools[QueryIntent.CUSTOM] = ["custom_tool"]
```

### 新しい意図タイプを追加

```python
class QueryIntent(Enum):
    # 既存の意図...
    CALCULATION = "calculation"  # 計算タスク
    TRANSLATION = "translation"   # 翻訳タスク
```

## 📊 ナレッジ検索の推奨設定

### 社内文書検索向け

```python
# 意図の重み付け調整
intent_to_tools = {
    factual_search: ["keyword_search"],  # 正確性重視
    semantic_search: ["semantic_search", "keyword_search"],
}
```

### 製品マニュアル向け

```python
# 要約機能を強化
intent_to_tools = {
    summarization: ["semantic_search", "summarization"],
    comparison: ["comparison", "summarization"],
}
```

### FAQ向け

```python
# 事実検索を優先
intent_to_tools = {
    factual_search: ["keyword_search"],
    unknown: ["keyword_search", "semantic_search"],
}
```

## 🎯 なぜこれがエージェンティックなのか？

1. **自律的な意思決定**
   - 質問を分析して意図を理解
   - 最適なツールを自動選択

2. **複数ツールの協調**
   - 単一ツールではなく、複数ツールを組み合わせ
   - 状況に応じた柔軟な対応

3. **フィードバックループ**
   - ツール実行結果を評価
   - 必要に応じて追加アクション

4. **コンテキスト理解**
   - 質問の種類を理解
   - 適切な回答スタイルを選択

## 🚀 使い方

### ローカルで試す

```bash
# function_app_router.py を使用
cp function_app_router.py function_app.py

# 起動
func start
```

### チャットで試す

```bash
# 事実検索
curl -X POST http://localhost:7071/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Azure OpenAIとは何ですか？"}'

# 比較
curl -X POST http://localhost:7071/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "GPT-4とGPT-3.5の違いは？"}'

# 要約
curl -X POST http://localhost:7071/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Azure サービスについてまとめて"}'
```

### レスポンスの確認

```json
{
  "status": "success",
  "message": "質問内容",
  "answer": "回答...",
  "intent": "factual_search",
  "tools_used": ["keyword_search", "semantic_search"],
  "timestamp": "..."
}
```

## 📈 パフォーマンス

- **意図分類**: ~500ms
- **ツール実行**: ~1-2秒（ツールによる）
- **回答生成**: ~1-2秒
- **合計**: ~2-4秒

### 最適化のヒント

1. **キャッシング**: 頻出質問をキャッシュ
2. **並列実行**: 複数ツールを並列実行
3. **ストリーミング**: 回答をストリーミング配信

## 🎓 次のステップ

- [ ] ReAct Agent パターンの実装
- [ ] Multi-Agent システムの構築
- [ ] カスタムツールの追加
- [ ] パフォーマンス最適化
- [ ] 評価指標の追加

これが**真のエージェンティックRAG**です！🚀
