"""
Azure Functions with Router Agent Pattern
真のエージェンティックRAG実装
"""

import azure.functions as func
import logging
import json
from datetime import datetime
from agentic_router import get_router_agent

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# グローバルでエージェントを初期化（コールドスタート対策）
_agent = None


def get_initialized_agent():
    """Router Agentを取得（遅延初期化）"""
    global _agent
    if _agent is None:
        logging.info("Router Agentを初期化しています...")
        _agent = get_router_agent()
        logging.info("Router Agentの初期化が完了しました")
    return _agent


@app.route(route="chat", methods=["POST"])
def chat_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Router Agent チャットエンドポイント
    
    質問の意図を自動分類し、最適なツールを使って回答
    """
    logging.info('Router Agent Chat function が呼び出されました。')
    
    try:
        req_body = req.get_json()
        message = req_body.get('message')
        
        if not message:
            return func.HttpResponse(
                json.dumps({
                    "error": "メッセージが指定されていません",
                    "usage": {
                        "message": "質問内容を入力してください"
                    }
                }, ensure_ascii=False),
                mimetype="application/json",
                status_code=400
            )
        
        # Router Agentを取得してクエリ実行
        agent = get_initialized_agent()
        result = agent.query(message)
        
        if result.get("success"):
            response = {
                "status": "success",
                "message": message,
                "answer": result.get("answer", ""),
                "intent": result.get("intent", "unknown"),
                "tools_used": result.get("tools_used", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            status_code = 200
        else:
            response = {
                "status": "error",
                "message": message,
                "error": result.get("error", "不明なエラー"),
                "timestamp": datetime.utcnow().isoformat()
            }
            status_code = 500
        
        return func.HttpResponse(
            json.dumps(response, ensure_ascii=False),
            mimetype="application/json",
            status_code=status_code
        )
    
    except ValueError:
        return func.HttpResponse(
            json.dumps({
                "error": "無効なJSONフォーマット"
            }, ensure_ascii=False),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Chat処理エラー: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "サーバーエラーが発生しました",
                "details": str(e)
            }, ensure_ascii=False),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="documents/load", methods=["POST"])
def load_documents_function(req: func.HttpRequest) -> func.HttpResponse:
    """ドキュメントをロード"""
    logging.info('Document load function が呼び出されました。')
    
    try:
        req_body = req.get_json()
        agent = get_initialized_agent()
        
        # テキストから直接ロード
        texts = req_body.get('texts')
        metadata = req_body.get('metadata')
        
        if not texts or not isinstance(texts, list):
            return func.HttpResponse(
                json.dumps({
                    "error": "textsが指定されていないか、配列ではありません",
                    "usage": {
                        "texts": ["ドキュメント1", "ドキュメント2"],
                        "metadata": [{"source": "doc1"}, {"source": "doc2"}]
                    }
                }, ensure_ascii=False),
                mimetype="application/json",
                status_code=400
            )
        
        success = agent.load_documents_from_texts(texts, metadata)
        
        if success:
            return func.HttpResponse(
                json.dumps({
                    "status": "success",
                    "message": f"{len(texts)}個のドキュメントをロードしました"
                }, ensure_ascii=False),
                mimetype="application/json",
                status_code=200
            )
        else:
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "error": "ドキュメントのロードに失敗しました"
                }, ensure_ascii=False),
                mimetype="application/json",
                status_code=500
            )
    
    except ValueError:
        return func.HttpResponse(
            json.dumps({
                "error": "無効なJSONフォーマット"
            }, ensure_ascii=False),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Document load エラー: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "error": "サーバーエラーが発生しました",
                "details": str(e)
            }, ensure_ascii=False),
            mimetype="application/json",
            status_code=500
        )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """ヘルスチェック"""
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "GPTlike Router Agent RAG",
            "version": "3.0.0",
            "agent_type": "Router Agent Pattern",
            "timestamp": datetime.utcnow().isoformat()
        }, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )


@app.route(route="info", methods=["GET"])
def info_function(req: func.HttpRequest) -> func.HttpResponse:
    """API情報"""
    return func.HttpResponse(
        json.dumps({
            "service": "GPTlike Router Agent RAG on Azure Functions",
            "version": "3.0.0",
            "agent_pattern": "Router Agent",
            "description": "質問の意図を自動分類し、最適なツールを選択して回答するエージェンティックRAG",
            "endpoints": {
                "chat": {
                    "path": "/api/chat",
                    "method": "POST",
                    "description": "Router Agentでチャット（意図自動分類）"
                },
                "documents_load": {
                    "path": "/api/documents/load",
                    "method": "POST",
                    "description": "ドキュメントをロード"
                },
                "health": {
                    "path": "/api/health",
                    "method": "GET",
                    "description": "ヘルスチェック"
                },
                "info": {
                    "path": "/api/info",
                    "method": "GET",
                    "description": "API情報"
                }
            },
            "features": [
                "Router Agent Pattern - 真のエージェンティックRAG",
                "質問意図の自動分類（7種類）",
                "複数の専門ツール（意味検索、キーワード検索、要約、比較）",
                "意図に応じた最適なツール選択",
                "Azure OpenAI統合",
                "Azure AI Search対応",
                "ベクトル検索（FAISS）",
                "Entra ID認証対応"
            ],
            "supported_intents": [
                "factual_search - 事実検索",
                "semantic_search - 意味検索",
                "summarization - 要約",
                "comparison - 比較",
                "analysis - 分析",
                "multi_hop - 複数ステップ推論",
                "unknown - その他"
            ]
        }, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )
