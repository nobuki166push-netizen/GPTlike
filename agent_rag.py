"""
Microsoft Agent Framework を使用したエージェンティックRAG実装
https://github.com/microsoft/agent-framework
"""

import os
import logging
from typing import List, Dict, Any, Optional
import json

from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
import faiss
import numpy as np


class DocumentStore:
    """ドキュメントのベクトルストア管理"""
    
    def __init__(self, openai_client: AzureOpenAI, embedding_deployment: str):
        self.client = openai_client
        self.embedding_deployment = embedding_deployment
        self.documents: List[Dict[str, Any]] = []
        self.index: Optional[faiss.IndexFlatL2] = None
        self.dimension = 1536  # text-embedding-ada-002の次元数
        
    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None):
        """ドキュメントを追加してインデックスを構築"""
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
        
        # FAISSインデックスを構築
        embeddings_array = np.array([doc["embedding"] for doc in self.documents]).astype('float32')
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.index.add(embeddings_array)
        
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """クエリに対して類似ドキュメントを検索"""
        if not self.documents or self.index is None:
            return []
        
        # クエリのembeddingを生成
        response = self.client.embeddings.create(
            input=query,
            model=self.embedding_deployment
        )
        query_embedding = np.array([response.data[0].embedding]).astype('float32')
        
        # 類似検索
        distances, indices = self.index.search(query_embedding, min(k, len(self.documents)))
        
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        
        return results


class AgentTool:
    """エージェントが使用するツールの基底クラス"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, *args, **kwargs) -> str:
        """ツールを実行"""
        raise NotImplementedError
    
    def to_function_definition(self) -> Dict[str, Any]:
        """OpenAI Function Calling用の定義を返す"""
        raise NotImplementedError


class DocumentSearchTool(AgentTool):
    """ドキュメント検索ツール"""
    
    def __init__(self, document_store: DocumentStore):
        super().__init__(
            name="search_documents",
            description="ドキュメントデータベースから関連情報を検索します。"
        )
        self.document_store = document_store
    
    def execute(self, query: str) -> str:
        """ドキュメント検索を実行"""
        results = self.document_store.search(query, k=3)
        
        if not results:
            return "関連するドキュメントが見つかりませんでした。"
        
        output = []
        for i, doc in enumerate(results, 1):
            output.append(f"[ドキュメント {i}]\n{doc['content']}")
        
        return "\n\n".join(output)
    
    def to_function_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "検索クエリ"
                        }
                    },
                    "required": ["query"]
                }
            }
        }


class AzureSearchTool(AgentTool):
    """Azure AI Search検索ツール"""
    
    def __init__(self, search_client: Optional[SearchClient]):
        super().__init__(
            name="azure_search",
            description="Azure AI Searchでクラウド上のドキュメントを検索します。"
        )
        self.search_client = search_client
    
    def execute(self, query: str) -> str:
        """Azure AI Searchで検索"""
        if not self.search_client:
            return "Azure AI Searchが設定されていません。"
        
        try:
            results = self.search_client.search(
                search_text=query,
                top=3,
                include_total_count=True
            )
            
            search_results = []
            for result in results:
                content = result.get('content', str(result))
                search_results.append(content)
            
            if not search_results:
                return "Azure AI Searchで関連する結果が見つかりませんでした。"
            
            return "\n\n".join(search_results)
        except Exception as e:
            return f"Azure Search検索中にエラーが発生: {str(e)}"
    
    def to_function_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "検索クエリ"
                        }
                    },
                    "required": ["query"]
                }
            }
        }


class MicrosoftAgent:
    """Microsoft Agent Framework を使用したエージェント"""
    
    def __init__(
        self,
        openai_client: AzureOpenAI,
        deployment_name: str,
        tools: List[AgentTool],
        system_prompt: str
    ):
        self.client = openai_client
        self.deployment_name = deployment_name
        self.tools = tools
        self.system_prompt = system_prompt
        self.logger = logging.getLogger(__name__)
        
        # ツールマップを作成
        self.tool_map = {tool.name: tool for tool in tools}
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """ツールを実行"""
        if tool_name not in self.tool_map:
            return f"ツール '{tool_name}' が見つかりません。"
        
        tool = self.tool_map[tool_name]
        try:
            return tool.execute(**arguments)
        except Exception as e:
            self.logger.error(f"ツール実行エラー ({tool_name}): {str(e)}")
            return f"ツール実行中にエラーが発生しました: {str(e)}"
    
    def run(self, user_message: str, max_iterations: int = 5) -> Dict[str, Any]:
        """エージェントを実行"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Function Calling用のツール定義
        tool_definitions = [tool.to_function_definition() for tool in self.tools]
        
        iteration = 0
        
        try:
            while iteration < max_iterations:
                iteration += 1
                
                # OpenAI APIを呼び出し
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    tools=tool_definitions if tool_definitions else None,
                    tool_choice="auto" if tool_definitions else None,
                    temperature=0.7
                )
                
                assistant_message = response.choices[0].message
                
                # ツール呼び出しがない場合は終了
                if not assistant_message.tool_calls:
                    return {
                        "success": True,
                        "answer": assistant_message.content,
                        "iterations": iteration
                    }
                
                # アシスタントメッセージを履歴に追加
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                
                # 各ツール呼び出しを実行
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    self.logger.info(f"ツール呼び出し: {function_name}({function_args})")
                    
                    # ツールを実行
                    function_response = self._execute_tool(function_name, function_args)
                    
                    # ツール実行結果を履歴に追加
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_response
                    })
            
            # 最大イテレーション到達
            return {
                "success": False,
                "error": "最大イテレーション数に到達しました",
                "iterations": iteration
            }
            
        except Exception as e:
            self.logger.error(f"エージェント実行エラー: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "iterations": iteration
            }


class AzureAgentRAG:
    """Microsoft Agent Framework を使用したエージェンティックRAGシステム"""
    
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
        
        # Azure Blob Storage クライアント（オプション）
        self.blob_service_client = None
        if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
                )
            except Exception as e:
                self.logger.warning(f"Azure Blob Storage初期化失敗: {str(e)}")
        
        # エージェントを初期化
        self.agent = self._create_agent()
    
    def _create_agent(self) -> MicrosoftAgent:
        """エージェントを作成"""
        # ツールを定義
        tools = [
            DocumentSearchTool(self.document_store)
        ]
        
        # Azure AI Searchが利用可能な場合は追加
        if self.search_client:
            tools.append(AzureSearchTool(self.search_client))
        
        # システムプロンプト
        system_prompt = """あなたは親切で知的なAIアシスタントです。
利用可能なツールを使って、ユーザーの質問に正確かつ詳細に答えてください。

ガイドライン:
1. ユーザーの質問を理解し、必要に応じてドキュメント検索ツールを使用する
2. 検索結果を基に、正確で分かりやすい回答を生成する
3. 情報源が不明確な場合は、その旨を明示する
4. 複数のツールを組み合わせて使用することも検討する
5. 日本語で丁寧に回答する
"""
        
        return MicrosoftAgent(
            openai_client=self.openai_client,
            deployment_name=self.deployment_name,
            tools=tools,
            system_prompt=system_prompt
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
    
    def load_documents_from_blob(self, container_name: Optional[str] = None) -> bool:
        """Azure Blob Storageからドキュメントをロード"""
        try:
            if not self.blob_service_client:
                raise ValueError("Azure Blob Storage が設定されていません")
            
            container_name = container_name or os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
            container_client = self.blob_service_client.get_container_client(container_name)
            
            texts = []
            metadata = []
            
            # Blobからテキストを取得
            for blob in container_client.list_blobs():
                blob_client = container_client.get_blob_client(blob.name)
                content = blob_client.download_blob().readall().decode('utf-8')
                texts.append(content)
                metadata.append({"source": blob.name})
            
            return self.load_documents_from_texts(texts, metadata)
        except Exception as e:
            self.logger.error(f"Blob Storage読み込みエラー: {str(e)}")
            return False
    
    def query(self, question: str) -> Dict[str, Any]:
        """エージェントに質問を投げる"""
        try:
            result = self.agent.run(question)
            return result
        except Exception as e:
            self.logger.error(f"クエリ実行エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# シングルトンインスタンス（Azure Functionsで再利用）
_agent_instance: Optional[AzureAgentRAG] = None


def get_agent() -> AzureAgentRAG:
    """エージェントインスタンスを取得（シングルトン）"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AzureAgentRAG()
    return _agent_instance
