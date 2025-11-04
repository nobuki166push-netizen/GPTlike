"""
エージェンティックRAG実装
LangChainとAzure OpenAI、Azure AI Searchを使用したエージェントシステム
"""

import os
import logging
from typing import List, Dict, Any, Optional

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient


class AzureRAGAgent:
    """Azure上で動作するエージェンティックRAGシステム"""
    
    def __init__(self):
        """環境変数からAzureサービスを初期化"""
        self.logger = logging.getLogger(__name__)
        
        # Azure OpenAI の初期化
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.7,
        )
        
        # Embeddings の初期化
        self.embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        )
        
        # Azure AI Search クライアント
        self.search_client = None
        if os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_SEARCH_API_KEY"):
            self.search_client = SearchClient(
                endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
                index_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "gptlike-index"),
                credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
            )
        
        # Azure Blob Storage クライアント
        self.blob_service_client = None
        if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
            self.blob_service_client = BlobServiceClient.from_connection_string(
                os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            )
        
        # ベクトルストア（ローカルキャッシュ用）
        self.vector_store: Optional[FAISS] = None
        
        # エージェントの初期化
        self.agent_executor = self._create_agent()
    
    def _create_rag_tool(self) -> Tool:
        """RAG検索ツールを作成"""
        def search_documents(query: str) -> str:
            """ドキュメントを検索して関連情報を取得"""
            try:
                if self.vector_store is None:
                    return "ベクトルストアが初期化されていません。先にドキュメントをロードしてください。"
                
                # 類似ドキュメント検索
                docs = self.vector_store.similarity_search(query, k=3)
                
                if not docs:
                    return "関連するドキュメントが見つかりませんでした。"
                
                # 結果をフォーマット
                results = []
                for i, doc in enumerate(docs, 1):
                    results.append(f"[ドキュメント {i}]\n{doc.page_content}\n")
                
                return "\n".join(results)
            except Exception as e:
                self.logger.error(f"RAG検索エラー: {str(e)}")
                return f"検索中にエラーが発生しました: {str(e)}"
        
        return Tool(
            name="document_search",
            description="ドキュメントデータベースから関連情報を検索します。ユーザーの質問に答えるために必要な情報を探す際に使用してください。",
            func=search_documents,
        )
    
    def _create_azure_search_tool(self) -> Tool:
        """Azure AI Search検索ツールを作成"""
        def azure_search(query: str) -> str:
            """Azure AI Searchでドキュメントを検索"""
            try:
                if self.search_client is None:
                    return "Azure AI Searchが設定されていません。"
                
                results = self.search_client.search(
                    search_text=query,
                    top=3,
                    include_total_count=True
                )
                
                search_results = []
                for result in results:
                    content = result.get('content', '')
                    search_results.append(content)
                
                if not search_results:
                    return "Azure AI Searchで関連する結果が見つかりませんでした。"
                
                return "\n\n".join(search_results)
            except Exception as e:
                self.logger.error(f"Azure Search エラー: {str(e)}")
                return f"Azure Search検索中にエラーが発生しました: {str(e)}"
        
        return Tool(
            name="azure_search",
            description="Azure AI Searchを使用してクラウド上のドキュメントを検索します。大規模なドキュメントコレクションから情報を探す際に使用してください。",
            func=azure_search,
        )
    
    def _create_summarization_tool(self) -> Tool:
        """要約ツールを作成"""
        def summarize_text(text: str) -> str:
            """テキストを要約"""
            try:
                prompt = f"以下のテキストを簡潔に要約してください:\n\n{text}"
                response = self.llm.invoke(prompt)
                return response.content
            except Exception as e:
                self.logger.error(f"要約エラー: {str(e)}")
                return f"要約中にエラーが発生しました: {str(e)}"
        
        return Tool(
            name="summarize",
            description="長いテキストを簡潔に要約します。大量の情報を整理する際に使用してください。",
            func=summarize_text,
        )
    
    def _create_agent(self) -> AgentExecutor:
        """エージェントを作成"""
        # ツールの定義
        tools = [
            self._create_rag_tool(),
            self._create_summarization_tool(),
        ]
        
        # Azure AI Searchが利用可能な場合は追加
        if self.search_client:
            tools.append(self._create_azure_search_tool())
        
        # プロンプトテンプレート
        prompt = ChatPromptTemplate.from_messages([
            ("system", """あなたは親切で知的なAIアシスタントです。
利用可能なツールを使って、ユーザーの質問に正確かつ詳細に答えてください。

以下のガイドラインに従ってください：
1. ユーザーの質問を理解し、必要に応じてドキュメント検索ツールを使用する
2. 検索結果を基に、正確で分かりやすい回答を生成する
3. 情報源が不明確な場合は、その旨を明示する
4. 複数のツールを組み合わせて使用することも検討する
5. 日本語で丁寧に回答する
"""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # エージェントの作成
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        
        # エージェント実行環境
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
        )
        
        return agent_executor
    
    def load_documents_from_texts(self, texts: List[str], metadata: Optional[List[Dict]] = None):
        """テキストからドキュメントをロードしてベクトルストアを構築"""
        try:
            # テキスト分割
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
            
            # ドキュメント作成
            documents = []
            for i, text in enumerate(texts):
                meta = metadata[i] if metadata and i < len(metadata) else {}
                chunks = text_splitter.split_text(text)
                for chunk in chunks:
                    documents.append(Document(page_content=chunk, metadata=meta))
            
            # ベクトルストア作成
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            self.logger.info(f"{len(documents)}個のドキュメントチャンクをロードしました")
            
            return True
        except Exception as e:
            self.logger.error(f"ドキュメントロードエラー: {str(e)}")
            return False
    
    def load_documents_from_blob(self, container_name: Optional[str] = None):
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
            result = self.agent_executor.invoke({"input": question})
            return {
                "success": True,
                "answer": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            self.logger.error(f"クエリ実行エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# シングルトンインスタンス（Azure Functionsで再利用）
_agent_instance: Optional[AzureRAGAgent] = None


def get_agent() -> AzureRAGAgent:
    """エージェントインスタンスを取得（シングルトン）"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AzureRAGAgent()
    return _agent_instance
