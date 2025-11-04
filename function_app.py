import azure.functions as func
import logging
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="gptlike", methods=["GET", "POST"])
def gptlike_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    GPTlike Azure Function - GPTのようなAIサービスのエンドポイント
    
    使用方法:
    - GET: ヘルスチェック
    - POST: メッセージを処理
    """
    logging.info('GPTlike function が呼び出されました。')

    if req.method == "GET":
        return func.HttpResponse(
            json.dumps({
                "status": "healthy",
                "message": "GPTlike Azure Function is running",
                "version": "1.0.0"
            }, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    elif req.method == "POST":
        try:
            # リクエストボディからメッセージを取得
            req_body = req.get_json()
            message = req_body.get('message')
            
            if not message:
                return func.HttpResponse(
                    json.dumps({
                        "error": "メッセージが指定されていません",
                        "usage": {
                            "message": "処理したいメッセージテキスト"
                        }
                    }, ensure_ascii=False),
                    mimetype="application/json",
                    status_code=400
                )

            # ここでGPTのような処理を実装
            # 現在は簡単なエコーレスポンスを返します
            response = {
                "status": "success",
                "received_message": message,
                "response": f"受信したメッセージ: {message}",
                "note": "ここにAI処理ロジックを実装できます"
            }

            return func.HttpResponse(
                json.dumps(response, ensure_ascii=False),
                mimetype="application/json",
                status_code=200
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
            logging.error(f"エラーが発生しました: {str(e)}")
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
            "timestamp": func.datetime.datetime.utcnow().isoformat()
        }),
        mimetype="application/json",
        status_code=200
    )
