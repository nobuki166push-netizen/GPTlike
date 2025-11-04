# ナレッジ検索パターン比較 📚

## 🎯 どのパターンを選ぶべきか？

### パターン比較表

| パターン | 複雑度 | レイテンシ | コスト | 推論能力 | 推奨用途 |
|---------|--------|----------|--------|---------|---------|
| **シンプルRAG** | ⭐ | 最速 | 低 | ⭐ | 単純なFAQ |
| **Router Agent** | ⭐⭐⭐ | 速い | 中 | ⭐⭐⭐⭐ | **ナレッジ検索（推奨）** |
| **ReAct Agent** | ⭐⭐⭐⭐ | 遅い | 高 | ⭐⭐⭐⭐⭐ | 複雑な調査 |
| **Multi-Agent** | ⭐⭐⭐⭐⭐ | 速い | 高 | ⭐⭐⭐⭐⭐ | 大規模システム |

## 📊 ユースケース別推奨

### 1. 社内文書検索システム

**推奨: Router Agent** ✅

```
特徴:
- 多様な質問タイプ（事実、比較、要約）
- 複数の文書ソース
- レスポンス速度が重要

実装例:
- 意図分類でキーワード検索 or 意味検索を選択
- 比較質問は専用ツールで処理
- 要約機能で長文を簡潔化
```

**設定:**
```python
intent_to_tools = {
    factual_search: ["keyword_search"],  # 正確性重視
    semantic_search: ["semantic_search"],
    comparison: ["comparison"],
    summarization: ["semantic_search", "summarization"],
}
```

### 2. 製品マニュアル・ヘルプデスク

**推奨: Router Agent with FAQ特化** ✅

```
特徴:
- 定型的な質問が多い
- 手順説明が必要
- マルチステップガイダンス

実装例:
- FAQパターンマッチング
- 手順抽出ツール
- トラブルシューティングフロー
```

**設定:**
```python
# FAQ用カスタムツールを追加
class FAQTool(KnowledgeTool):
    def execute(self, query: str):
        # FAQ特化の検索ロジック
        pass

router_agent.tools["faq_search"] = FAQTool()
```

### 3. 技術ドキュメント・API リファレンス

**推奨: Router Agent + Code Search** ✅

```
特徴:
- コード例が重要
- 正確な技術用語
- バージョン管理

実装例:
- コード検索ツール
- APIドキュメント専用検索
- バージョンフィルタリング
```

**設定:**
```python
class CodeSearchTool(KnowledgeTool):
    def execute(self, query: str):
        # コードスニペット検索
        pass

class APIReferenceTool(KnowledgeTool):
    def execute(self, query: str):
        # API仕様検索
        pass
```

### 4. 研究論文・レポート検索

**推奨: Router Agent + Citation** ✅

```
特徴:
- 引用が重要
- 複雑な分析
- メタデータ管理

実装例:
- 論文メタデータ検索
- 引用追跡
- 関連論文推薦
```

### 5. リアルタイムサポート

**推奨: シンプルRAG** ⚡

```
特徴:
- 速度最優先
- 単純な質問
- 高頻度アクセス

実装:
- 単一ベクトル検索
- キャッシング活用
- ストリーミング回答
```

### 6. 複雑な調査タスク

**推奨: ReAct Agent** 🧠

```
特徴:
- 複数ステップの推論
- 情報の組み合わせ
- 「なぜ？」に答える

実装:
- 思考-行動-観察ループ
- 複数回の検索・分析
- 推論過程の記録
```

## 🏗️ 実装の選択フローチャート

```
質問の複雑度は？
    │
    ├─ 単純（FAQ） → シンプルRAG
    │
    ├─ 中程度（多様な質問） → Router Agent ★推奨
    │
    └─ 複雑（調査・分析） → ReAct Agent
```

## 📈 ナレッジベースの規模による選択

### 小規模（< 1,000 文書）
- **推奨**: Router Agent
- **理由**: オーバーヘッドが少ない、十分な性能

### 中規模（1,000 - 100,000 文書）
- **推奨**: Router Agent + Azure AI Search
- **理由**: スケーラブル、コスト効率的

### 大規模（> 100,000 文書）
- **推奨**: Multi-Agent System
- **理由**: 並列処理、専門化

## 💡 Router Agent のカスタマイズ例

### 社内文書検索向け設定

```python
# agentic_router.py をカスタマイズ

class InternalDocSearchTool(KnowledgeTool):
    """社内文書検索に特化したツール"""
    
    def execute(self, query: str, context: Dict = None):
        # 部署フィルタリング
        department = context.get("department")
        
        # アクセス権限チェック
        user_id = context.get("user_id")
        
        # 検索実行
        results = self.search_with_permissions(
            query, 
            department, 
            user_id
        )
        
        return {"success": True, "documents": results}

# Router Agentに追加
router.tools["internal_doc_search"] = InternalDocSearchTool()
```

### 製品マニュアル向け設定

```python
class TroubleshootingTool(KnowledgeTool):
    """トラブルシューティング専用ツール"""
    
    def execute(self, query: str, context: Dict = None):
        # 問題の症状を分析
        symptoms = self.extract_symptoms(query)
        
        # 解決策を検索
        solutions = self.search_solutions(symptoms)
        
        # ステップバイステップガイド生成
        guide = self.generate_guide(solutions)
        
        return {
            "success": True,
            "symptoms": symptoms,
            "solutions": solutions,
            "guide": guide
        }
```

## 🎯 推奨: ナレッジ検索には Router Agent

### 理由

1. **柔軟性**: 多様な質問タイプに対応
2. **効率性**: 必要なツールだけ実行
3. **拡張性**: 新しいツールを簡単に追加
4. **コスト効率**: 不要な処理を削減
5. **ユーザー体験**: 適切な回答スタイル

### 実装済み機能

✅ 意図分類（7種類）  
✅ 意味検索（FAISS）  
✅ キーワード検索（Azure AI Search）  
✅ 要約機能  
✅ 比較分析  
✅ 自動ツール選択  
✅ 統合回答生成  

### 今すぐ始める

```bash
# Router Agent版を使用
cp function_app_router.py function_app.py

# 起動
func start

# フロントエンドも起動
cd frontend && npm run dev
```

## 📚 参考資料

- [Router Agent 完全ガイド](ROUTER_AGENT_GUIDE.md)
- [クイックスタート](QUICKSTART.md)
- [README](README.md)

**ナレッジ検索なら Router Agent が最適解です！** 🎯
