import azure.functions as func
import logging
import json
from datetime import datetime
from agent_rag import get_agent

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# グローバルでエージェントを初期化（コールドスタート対策）
_agent = None


def get_initialized_agent():
    """エージェントを取得（遅延初期化）"""
    global _agent
    if _agent is None:
        logging.info("エージェントを初期化しています...")
        _agent = get_agent()
        logging.info("エージェントの初期化が完了しました")
    return _agent


@app.route(route="chat", methods=["POST"])
def chat_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    エージェンティックRAGチャットエンドポイント
    
    リクエスト:
    {
        "message": "質問内容",
        "stream": false  // オプション: ストリーミング対応（将来実装）
    }
    """
    logging.info('Chat function が呼び出されました。')
    
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
        
        # エージェントを取得してクエリ実行
        agent = get_initialized_agent()
        result = agent.query(message)
        
        if result.get("success"):
            response = {
                "status": "success",
                "message": message,
                "answer": result.get("answer", ""),
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
    """
    ドキュメントをロードしてRAGシステムに追加
    
    リクエスト:
    {
        "texts": ["ドキュメント1", "ドキュメント2"],
        "metadata": [{"source": "doc1.txt"}, {"source": "doc2.txt"}]  // オプション
    }
    または
    {
        "from_blob": true,
        "container_name": "documents"  // オプション
    }
    """
    logging.info('Document load function が呼び出されました。')
    
    try:
        req_body = req.get_json()
        agent = get_initialized_agent()
        
        # Blob Storageからロード
        if req_body.get('from_blob'):
            container_name = req_body.get('container_name')
            success = agent.load_documents_from_blob(container_name)
            
            if success:
                return func.HttpResponse(
                    json.dumps({
                        "status": "success",
                        "message": "Blob Storageからドキュメントをロードしました"
                    }, ensure_ascii=False),
                    mimetype="application/json",
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        "status": "error",
                        "error": "Blob Storageからのロードに失敗しました"
                    }, ensure_ascii=False),
                    mimetype="application/json",
                    status_code=500
                )
        
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
    """
    ヘルスチェックエンドポイント
    """
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "GPTlike Agentic RAG",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )


@app.route(route="info", methods=["GET"])
def info_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    APIの情報を返すエンドポイント
    """
    return func.HttpResponse(
        json.dumps({
            "service": "GPTlike Agentic RAG on Azure Functions",
            "version": "2.0.0",
            "endpoints": {
                "chat": {
                    "path": "/api/chat",
                    "method": "POST",
                    "description": "エージェンティックRAGでチャット"
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
                "Microsoft Agent Frameworkベースのエージェント",
                "OpenAI Function Calling",
                "Azure OpenAI統合",
                "Azure AI Search対応",
                "Azure Blob Storage統合",
                "ベクトル検索（FAISS）"
            ]
        }, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )
