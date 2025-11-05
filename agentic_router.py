"""
Router Agent パターン - 真のエージェンティックRAG実装
質問の意図に応じて最適なツールを自動選択
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json
from enum import Enum

from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
import faiss
import numpy as np


logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """質問の意図タイプ"""
    FACTUAL_SEARCH = "factual_search"  # 事実検索
    SEMANTIC_SEARCH = "semantic_search"  # 意味検索
    SUMMARIZATION = "summarization"  # 要約
    COMPARISON = "comparison"  # 比較
    ANALYSIS = "analysis"  # 分析
    MULTI_HOP = "multi_hop"  # 複数ステップ推論
    UNKNOWN = "unknown"


class DocumentStore:
    """ドキュメントのベクトルストア管理（FAISSベース）"""
    
    def __init__(self, openai_client: AzureOpenAI, embedding_deployment: str):
        self.client = openai_client
        self.embedding_deployment = embedding_deployment
        self.documents: List[Dict[str, Any]] = []
        self.index: Optional[faiss.IndexFlatL2] = None
        self.dimension = 1536
        
    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None):
        """ドキュメントを追加"""
        if not texts:
            return
        
        # Embeddingsを生成
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            embeddings.append(response.data[0].embedding)
        
        # ドキュメント情報を保存
        for i, text in enumerate(texts):
            meta = metadata[i] if metadata and i < len(metadata) else {}
            self.documents.append({
                "id": len(self.documents),
                "content": text,
                "metadata": meta,
                "embedding": embeddings[i]
            })
        
        # FAISSインデックスを再構築
        embeddings_array = np.array([doc["embedding"] for doc in self.documents]).astype('float32')
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        else:
            self.index.reset()
        
        self.index.add(embeddings_array)
        logger.info(f"Indexed {len(self.documents)} documents")
        
    def search(self, query: str, k: int = 5, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """類似ドキュメントを検索"""
        if not self.documents or self.index is None:
            return []
        
        # クエリのembeddingを生成
        response = self.client.embeddings.create(
            input=query,
            model=self.embedding_deployment
        )
        query_embedding = np.array([response.data[0].embedding]).astype('float32')
        
        # 類似検索
        k = min(k, len(self.documents))
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(dist)
                
                # スコアがthresholdを超える場合はスキップ
                if threshold and dist > threshold:
                    continue
                    
                results.append(doc)
        
        return results


class IntentClassifier:
    """質問の意図を分類"""
    
    def __init__(self, openai_client: AzureOpenAI, deployment_name: str):
        self.client = openai_client
        self.deployment_name = deployment_name
    
    def classify(self, query: str) -> QueryIntent:
        """質問の意図を分類"""
        
        system_prompt = """あなたは質問の意図を分類するエキスパートです。
以下の質問を分析し、最も適切なカテゴリを1つ選んでください：

1. factual_search: 特定の事実や情報を探している（「〜とは何ですか」「〜の価格は」）
2. semantic_search: 概念や意味的な検索（「〜に関する情報」「〜について教えて」）
3. summarization: 要約を求めている（「まとめて」「要約して」）
4. comparison: 複数のものを比較（「AとBの違いは」「どちらが良い」）
5. analysis: 分析や考察を求めている（「なぜ」「どう思うか」「評価して」）
6. multi_hop: 複数ステップの推論が必要（「〜を調べてから、その情報を使って〜」）
7. unknown: 上記に当てはまらない

JSON形式で回答してください：{"intent": "カテゴリ名", "reasoning": "理由"}"""

        try:
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
            intent_str = result.get("intent", "unknown")
            reasoning = result.get("reasoning", "")
            
            logger.info(f"Intent classified: {intent_str} - {reasoning}")
            
            try:
                return QueryIntent(intent_str)
            except ValueError:
                return QueryIntent.UNKNOWN
                
        except Exception as e:
            logger.error(f"Intent classification error: {str(e)}")
            return QueryIntent.UNKNOWN


class KnowledgeTool:
    """ナレッジ検索ツールの基底クラス"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """ツールを実行"""
        raise NotImplementedError


class SemanticSearchTool(KnowledgeTool):
    """意味的検索ツール"""
    
    def __init__(self, document_store: DocumentStore):
        super().__init__(
            name="semantic_search",
            description="ドキュメントから意味的に関連する情報を検索します。"
        )
        self.document_store = document_store
    
    def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """意味検索を実行"""
        k = context.get("k", 3) if context else 3
        results = self.document_store.search(query, k=k)
        
        if not results:
            return {
                "success": False,
                "message": "関連するドキュメントが見つかりませんでした。",
                "documents": []
            }
        
        return {
            "success": True,
            "message": f"{len(results)}件のドキュメントを見つけました。",
            "documents": [
                {
                    "content": doc["content"],
                    "metadata": doc.get("metadata", {}),
                    "score": doc.get("score", 0)
                }
                for doc in results
            ]
        }


class KeywordSearchTool(KnowledgeTool):
    """キーワード検索ツール（Azure AI Search使用）"""
    
    def __init__(self, search_client: Optional[SearchClient]):
        super().__init__(
            name="keyword_search",
            description="キーワードベースでドキュメントを検索します（正確な用語検索に最適）。"
        )
        self.search_client = search_client
    
    def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """キーワード検索を実行"""
        if not self.search_client:
            return {
                "success": False,
                "message": "Azure AI Searchが設定されていません。"
            }
        
        try:
            top = context.get("top", 3) if context else 3
            results = self.search_client.search(
                search_text=query,
                top=top,
                include_total_count=True
            )
            
            documents = []
            for result in results:
                documents.append({
                    "content": result.get('content', str(result)),
                    "metadata": {k: v for k, v in result.items() if k != 'content'}
                })
            
            if not documents:
                return {
                    "success": False,
                    "message": "該当するドキュメントが見つかりませんでした。"
                }
            
            return {
                "success": True,
                "message": f"{len(documents)}件のドキュメントを見つけました。",
                "documents": documents
            }
            
        except Exception as e:
            logger.error(f"Keyword search error: {str(e)}")
            return {
                "success": False,
                "message": f"検索エラー: {str(e)}"
            }


class SummarizationTool(KnowledgeTool):
    """要約ツール"""
    
    def __init__(self, openai_client: AzureOpenAI, deployment_name: str):
        super().__init__(
            name="summarization",
            description="長いテキストを簡潔に要約します。"
        )
        self.client = openai_client
        self.deployment_name = deployment_name
    
    def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """要約を実行"""
        text_to_summarize = context.get("text", query) if context else query
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "以下のテキストを簡潔に要約してください。重要なポイントを3-5個の箇条書きにまとめてください。"},
                    {"role": "user", "content": text_to_summarize}
                ],
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return {
                "success": False,
                "message": f"要約エラー: {str(e)}"
            }


class ComparisonTool(KnowledgeTool):
    """比較分析ツール"""
    
    def __init__(self, openai_client: AzureOpenAI, deployment_name: str, document_store: DocumentStore):
        super().__init__(
            name="comparison",
            description="複数の項目を比較分析します。"
        )
        self.client = openai_client
        self.deployment_name = deployment_name
        self.document_store = document_store
    
    def execute(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """比較を実行"""
        # まず関連ドキュメントを検索
        search_results = self.document_store.search(query, k=5)
        
        if not search_results:
            return {
                "success": False,
                "message": "比較するための情報が見つかりませんでした。"
            }
        
        # 検索結果を元に比較分析
        context_text = "\n\n".join([doc["content"] for doc in search_results])
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "以下の情報を基に、ユーザーの質問に答えてください。比較分析を行い、違いや共通点を明確にしてください。"},
                    {"role": "user", "content": f"情報:\n{context_text}\n\n質問: {query}"}
                ],
                temperature=0.5
            )
            
            comparison = response.choices[0].message.content
            
            return {
                "success": True,
                "comparison": comparison,
                "sources": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Comparison error: {str(e)}")
            return {
                "success": False,
                "message": f"比較エラー: {str(e)}"
            }


class RouterAgent:
    """
    Router Agent - 質問の意図に応じて最適なツールを選択・実行
    """
    
    def __init__(
        self,
        openai_client: AzureOpenAI,
        deployment_name: str,
        document_store: DocumentStore,
        search_client: Optional[SearchClient] = None
    ):
        self.client = openai_client
        self.deployment_name = deployment_name
        self.document_store = document_store
        
        # 意図分類器
        self.intent_classifier = IntentClassifier(openai_client, deployment_name)
        
        # ツール群を初期化
        self.tools: Dict[str, KnowledgeTool] = {
            "semantic_search": SemanticSearchTool(document_store),
            "summarization": SummarizationTool(openai_client, deployment_name),
            "comparison": ComparisonTool(openai_client, deployment_name, document_store),
        }
        
        if search_client:
            self.tools["keyword_search"] = KeywordSearchTool(search_client)
        
        # 意図とツールのマッピング
        self.intent_to_tools = {
            QueryIntent.FACTUAL_SEARCH: ["keyword_search", "semantic_search"],
            QueryIntent.SEMANTIC_SEARCH: ["semantic_search"],
            QueryIntent.SUMMARIZATION: ["semantic_search", "summarization"],
            QueryIntent.COMPARISON: ["comparison"],
            QueryIntent.ANALYSIS: ["semantic_search"],
            QueryIntent.MULTI_HOP: ["semantic_search", "comparison"],
            QueryIntent.UNKNOWN: ["semantic_search"],
        }
    
    def route(self, query: str) -> Dict[str, Any]:
        """
        質問を分析し、最適なツールにルーティングして回答を生成
        """
        logger.info(f"=== Router Agent Started ===")
        logger.info(f"Query: {query}")
        
        # Step 1: 意図を分類
        intent = self.intent_classifier.classify(query)
        logger.info(f"Classified intent: {intent.value}")
        
        # Step 2: 適切なツールを選択
        tool_names = self.intent_to_tools.get(intent, ["semantic_search"])
        logger.info(f"Selected tools: {tool_names}")
        
        # Step 3: ツールを実行
        tool_results = []
        for tool_name in tool_names:
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                logger.info(f"Executing tool: {tool_name}")
                
                result = tool.execute(query)
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })
        
        # Step 4: 結果を統合して最終回答を生成
        final_answer = self._generate_final_answer(query, intent, tool_results)
        
        logger.info(f"=== Router Agent Completed ===")
        
        return {
            "success": True,
            "query": query,
            "intent": intent.value,
            "tools_used": tool_names,
            "tool_results": tool_results,
            "answer": final_answer
        }
    
    def _generate_final_answer(
        self,
        query: str,
        intent: QueryIntent,
        tool_results: List[Dict[str, Any]]
    ) -> str:
        """ツール実行結果を統合して最終回答を生成"""
        
        # ツール結果を整形
        context_parts = []
        for tr in tool_results:
            tool_name = tr["tool"]
            result = tr["result"]
            
            if result.get("success"):
                if "documents" in result:
                    docs_text = "\n".join([
                        f"- {doc['content']}" 
                        for doc in result["documents"][:3]
                    ])
                    context_parts.append(f"[{tool_name}の結果]\n{docs_text}")
                elif "summary" in result:
                    context_parts.append(f"[要約]\n{result['summary']}")
                elif "comparison" in result:
                    context_parts.append(f"[比較分析]\n{result['comparison']}")
        
        if not context_parts:
            return "申し訳ございません。関連する情報が見つかりませんでした。"
        
        context_text = "\n\n".join(context_parts)
        
        # 意図に応じたシステムプロンプト
        system_prompts = {
            QueryIntent.FACTUAL_SEARCH: "以下の情報を基に、ユーザーの質問に正確に答えてください。",
            QueryIntent.SEMANTIC_SEARCH: "以下の情報を基に、ユーザーの質問に丁寧に答えてください。",
            QueryIntent.SUMMARIZATION: "以下の情報を基に、要点を簡潔にまとめて説明してください。",
            QueryIntent.COMPARISON: "以下の比較分析を基に、違いや共通点を明確に説明してください。",
            QueryIntent.ANALYSIS: "以下の情報を基に、分析的に回答してください。",
            QueryIntent.MULTI_HOP: "以下の情報を組み合わせて、段階的に推論して答えてください。",
        }
        
        system_prompt = system_prompts.get(
            intent,
            "以下の情報を基に、ユーザーの質問に答えてください。"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"情報:\n{context_text}\n\n質問: {query}"}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Answer generation error: {str(e)}")
            return f"回答生成中にエラーが発生しました: {str(e)}"


class AzureRouterRAG:
    """Azure上のRouter Agent RAGシステム"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Azure OpenAI クライアント
        self.openai_client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )
        
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        
        # ドキュメントストア
        self.document_store = DocumentStore(self.openai_client, self.embedding_deployment)
        
        # Azure AI Search クライアント（オプション）
        self.search_client = None
        if os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_SEARCH_API_KEY"):
            try:
                self.search_client = SearchClient(
                    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
                    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "gptlike-index"),
                    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
                )
            except Exception as e:
                self.logger.warning(f"Azure AI Search初期化失敗: {str(e)}")
        
        # Router Agent を初期化
        self.agent = RouterAgent(
            openai_client=self.openai_client,
            deployment_name=self.deployment_name,
            document_store=self.document_store,
            search_client=self.search_client
        )
    
    def load_documents_from_texts(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> bool:
        """テキストからドキュメントをロード"""
        try:
            self.document_store.add_documents(texts, metadata)
            self.logger.info(f"{len(texts)}個のドキュメントをロードしました")
            return True
        except Exception as e:
            self.logger.error(f"ドキュメントロードエラー: {str(e)}")
            return False
    
    def query(self, question: str) -> Dict[str, Any]:
        """Router Agentに質問を投げる"""
        try:
            result = self.agent.route(question)
            return result
        except Exception as e:
            self.logger.error(f"クエリ実行エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# シングルトンインスタンス
_router_agent_instance: Optional[AzureRouterRAG] = None


def get_router_agent() -> AzureRouterRAG:
    """Router Agentインスタンスを取得（シングルトン）"""
    global _router_agent_instance
    if _router_agent_instance is None:
        _router_agent_instance = AzureRouterRAG()
    return _router_agent_instance
