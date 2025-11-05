# エージェント機能分解 - Router Agent の内部構造 🔍

## 🏗️ アーキテクチャ全体図

```
┌─────────────────────────────────────────────────────────────┐
│                    RouterAgent (指揮官)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  route(query) - メインのエージェントループ            │   │
│  │                                                       │   │
│  │  Step 1: 意図を分類 → IntentClassifier              │   │
│  │  Step 2: ツールを選択 → intent_to_tools             │   │
│  │  Step 3: ツールを実行 → ツール群                    │   │
│  │  Step 4: 結果を統合 → _generate_final_answer        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
              ↓              ↓              ↓
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  認知層      │  │  実行層      │  │  知識層      │
    │ (Cognition) │  │ (Execution)  │  │ (Knowledge)  │
    └─────────────┘  └─────────────┘  └─────────────┘
```

## 🧠 レイヤー1: 認知層（Cognitive Layer）

### IntentClassifier - 意図理解エンジン

```python
class IntentClassifier:
    """質問の意図を分類"""
    
    def classify(self, query: str) -> QueryIntent:
        # LLMを使って質問を7種類に分類
        # - factual_search: 「〜とは？」
        # - semantic_search: 「〜について教えて」
        # - summarization: 「まとめて」
        # - comparison: 「違いは？」
        # - analysis: 「なぜ？」
        # - multi_hop: 複数ステップ
        # - unknown: その他
```

**エージェンティックな点:**
- ✅ **自律的判断**: LLMで質問の意図を推論
- ✅ **コンテキスト理解**: 単なるキーワードマッチではなく意味理解
- ✅ **動的分類**: 質問タイプを動的に判定

**実際のコード:**
```python
# agentic_router.py:105-156
def classify(self, query: str) -> QueryIntent:
    system_prompt = """あなたは質問の意図を分類するエキスパートです。
    以下の質問を分析し、最も適切なカテゴリを1つ選んでください：
    1. factual_search: 特定の事実...
    2. semantic_search: 概念や意味的...
    ...
    """
    
    response = self.client.chat.completions.create(
        model=self.deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"質問: {query}"}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return QueryIntent(result.get("intent"))
```

## ⚙️ レイヤー2: 実行層（Execution Layer）

### RouterAgent.route() - 意思決定エンジン

```python
class RouterAgent:
    def route(self, query: str) -> Dict[str, Any]:
        """
        エージェントのメインループ
        これが真のエージェント動作
        """
        
        # ========== Step 1: 認知 ==========
        intent = self.intent_classifier.classify(query)
        logger.info(f"Classified intent: {intent.value}")
        
        # ========== Step 2: 計画 ==========
        # 意図に基づいてツールを選択
        tool_names = self.intent_to_tools.get(intent, ["semantic_search"])
        logger.info(f"Selected tools: {tool_names}")
        
        # ========== Step 3: 実行 ==========
        tool_results = []
        for tool_name in tool_names:
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                result = tool.execute(query)
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })
        
        # ========== Step 4: 統合 ==========
        final_answer = self._generate_final_answer(query, intent, tool_results)
        
        return {
            "query": query,
            "intent": intent.value,
            "tools_used": tool_names,
            "answer": final_answer
        }
```

**エージェンティックな点:**
- ✅ **計画（Planning）**: 意図に基づいてツールを選択
- ✅ **実行（Execution）**: 選択したツールを実行
- ✅ **観察（Observation）**: ツール実行結果を取得
- ✅ **統合（Synthesis）**: 結果を統合して最終回答

### 意図→ツールマッピング（戦略テーブル）

```python
self.intent_to_tools = {
    QueryIntent.FACTUAL_SEARCH: ["keyword_search", "semantic_search"],
    QueryIntent.SEMANTIC_SEARCH: ["semantic_search"],
    QueryIntent.SUMMARIZATION: ["semantic_search", "summarization"],
    QueryIntent.COMPARISON: ["comparison"],
    QueryIntent.ANALYSIS: ["semantic_search"],
    QueryIntent.MULTI_HOP: ["semantic_search", "comparison"],
    QueryIntent.UNKNOWN: ["semantic_search"],
}
```

**これが「Router」の核心:**
- 意図ごとに最適なツールの組み合わせを定義
- 柔軟に変更・拡張可能

## 🛠️ レイヤー3: ツール層（Tool Layer）

### 各ツールは独立したエージェント

#### 1. SemanticSearchTool - 意味検索エージェント

```python
class SemanticSearchTool(KnowledgeTool):
    def execute(self, query: str, context: Dict = None) -> Dict:
        # 1. ベクトル化
        # 2. FAISS検索
        # 3. スコアリング
        # 4. 結果返却
        
        results = self.document_store.search(query, k=3)
        
        return {
            "success": True,
            "documents": results
        }
```

#### 2. KeywordSearchTool - キーワード検索エージェント

```python
class KeywordSearchTool(KnowledgeTool):
    def execute(self, query: str, context: Dict = None) -> Dict:
        # Azure AI Search でキーワード検索
        results = self.search_client.search(
            search_text=query,
            top=3
        )
        
        return {
            "success": True,
            "documents": list(results)
        }
```

#### 3. SummarizationTool - 要約エージェント

```python
class SummarizationTool(KnowledgeTool):
    def execute(self, query: str, context: Dict = None) -> Dict:
        # 1. テキストを取得
        # 2. LLMで要約
        # 3. 箇条書き化
        
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "簡潔に要約してください"},
                {"role": "user", "content": text}
            ]
        )
        
        return {
            "success": True,
            "summary": response.choices[0].message.content
        }
```

#### 4. ComparisonTool - 比較分析エージェント

```python
class ComparisonTool(KnowledgeTool):
    def execute(self, query: str, context: Dict = None) -> Dict:
        # 1. 関連情報を検索
        search_results = self.document_store.search(query, k=5)
        
        # 2. 検索結果を整形
        context_text = "\n".join([doc["content"] for doc in search_results])
        
        # 3. LLMで比較分析
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": "比較分析してください"},
                {"role": "user", "content": f"情報:\n{context_text}\n\n質問: {query}"}
            ]
        )
        
        return {
            "success": True,
            "comparison": response.choices[0].message.content
        }
```

## 🔄 実行フロー詳細

### 例: 「GPT-4とGPT-3.5の違いは？」

```
┌─────────────────────────────────────────────────────────┐
│ 1. 質問入力                                              │
│    query = "GPT-4とGPT-3.5の違いは？"                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 意図分類（IntentClassifier）                          │
│    LLM推論: "comparison" と判定                          │
│    理由: "違い"というキーワードと文脈から                 │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. ツール選択（RouterAgent）                             │
│    intent_to_tools[comparison] → ["comparison"]         │
│    決定: ComparisonTool を実行                            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. ツール実行（ComparisonTool）                          │
│    4a. 検索: GPT-4とGPT-3.5に関する情報を検索            │
│    4b. 分析: LLMで両者を比較分析                         │
│    4c. 構造化: 違いを明確に整理                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. 結果統合（_generate_final_answer）                    │
│    - ComparisonToolの結果を整形                          │
│    - 比較表形式で出力                                     │
│    - 情報源を明示                                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 6. 最終回答                                              │
│    {                                                    │
│      "intent": "comparison",                            │
│      "tools_used": ["comparison"],                      │
│      "answer": "GPT-4とGPT-3.5の主な違い..."            │
│    }                                                    │
└─────────────────────────────────────────────────────────┘
```

## 🎯 なぜこれが「エージェンティック」なのか？

### 1. **自律性（Autonomy）**
```python
# 人間が指定するのは質問だけ
query = "違いは？"

# エージェントが自律的に：
# - 意図を理解（comparison）
# - ツールを選択（ComparisonTool）
# - 実行戦略を決定
# - 結果を統合
```

### 2. **反応性（Reactivity）**
```python
# 質問の種類によって動作を変える
if intent == FACTUAL_SEARCH:
    tools = ["keyword_search"]  # 正確性重視
elif intent == SEMANTIC_SEARCH:
    tools = ["semantic_search"]  # 意味理解重視
elif intent == COMPARISON:
    tools = ["comparison"]  # 分析重視
```

### 3. **目標志向（Goal-oriented）**
```python
# 最終目標: ユーザーの質問に最適に答える
# そのために:
# 1. 意図を理解
# 2. 戦略を立案
# 3. ツールを実行
# 4. 結果を統合
```

### 4. **学習・適応（Learning/Adaptation）**
```python
# 新しいツールを簡単に追加可能
class NewTool(KnowledgeTool):
    def execute(self, query: str):
        # 新しい検索方法
        pass

router.tools["new_tool"] = NewTool()
router.intent_to_tools[NEW_INTENT] = ["new_tool"]
```

## 📊 従来のRAG vs Router Agent

### シンプルRAG（非エージェント的）
```python
def simple_rag(query):
    # 常に同じ処理
    docs = vector_search(query)
    answer = llm_generate(docs, query)
    return answer
```
- ❌ 意図理解なし
- ❌ ツール選択なし
- ❌ 戦略なし

### Router Agent（エージェント的）
```python
def router_agent(query):
    # 1. 理解
    intent = classify_intent(query)
    
    # 2. 計画
    tools = select_tools(intent)
    
    # 3. 実行
    results = [tool.execute(query) for tool in tools]
    
    # 4. 統合
    answer = synthesize(results, intent)
    
    return answer
```
- ✅ 意図理解
- ✅ 戦略的ツール選択
- ✅ 複数ツール協調
- ✅ 適応的回答生成

## 🔧 拡張性

### 新しい意図タイプを追加

```python
# 1. 意図を定義
class QueryIntent(Enum):
    CALCULATION = "calculation"  # NEW!

# 2. ツールを作成
class CalculatorTool(KnowledgeTool):
    def execute(self, query: str):
        # 数式を抽出して計算
        pass

# 3. マッピングに追加
intent_to_tools[QueryIntent.CALCULATION] = ["calculator"]
```

### 複雑な推論パターン

```python
# Multi-hop推論の例
intent_to_tools[QueryIntent.MULTI_HOP] = [
    "semantic_search",  # Step 1: 情報収集
    "analysis",         # Step 2: 分析
    "comparison"        # Step 3: 比較
]

# ツールを順次実行し、前のツールの結果を次に渡す
```

## 📈 エージェント動作のログ

実際のログ出力:
```
=== Router Agent Started ===
Query: GPT-4とGPT-3.5の違いは？
Classified intent: comparison
Selected tools: ['comparison']
Executing tool: comparison
  → Searching documents...
  → Found 5 relevant documents
  → Analyzing with LLM...
  → Comparison complete
=== Router Agent Completed ===
```

## 🎓 まとめ

**Router Agent の機能分解:**

1. **認知層**: IntentClassifier（意図理解）
2. **実行層**: RouterAgent（計画・実行・統合）
3. **ツール層**: 専門ツール群（検索・要約・比較・分析）
4. **知識層**: DocumentStore, Azure AI Search

**エージェンティックな特徴:**

- ✅ 自律的判断
- ✅ 戦略的計画
- ✅ ツール選択
- ✅ 適応的実行
- ✅ 結果統合
- ✅ 拡張可能

これが**真のエージェンティックRAG**です！🤖
