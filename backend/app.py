import os
import json
import logging
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from openai import AzureOpenAI
from dotenv import load_dotenv

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__)
CORS(app)

# Azure OpenAI クライアントの初期化
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-35-turbo")


@app.route("/api/health", methods=["GET"])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({"status": "healthy"}), 200


@app.route("/api/conversation", methods=["POST"])
def conversation():
    """チャット会話エンドポイント"""
    try:
        # リクエストボディから会話履歴を取得
        request_data = request.get_json()
        messages = request_data.get("messages", [])
        stream = request_data.get("stream", False)
        
        if not messages:
            return jsonify({"error": "メッセージが空です"}), 400

        logger.info(f"Received conversation request with {len(messages)} messages")

        if stream:
            # ストリーミングレスポンス
            def generate():
                try:
                    response = client.chat.completions.create(
                        model=DEPLOYMENT_NAME,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=800,
                        stream=True
                    )
                    
                    for chunk in response:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'content') and delta.content:
                                # SSE形式でデータを送信
                                yield f"data: {json.dumps({'content': delta.content})}\n\n"
                    
                    yield "data: [DONE]\n\n"
                    
                except Exception as e:
                    logger.error(f"Streaming error: {str(e)}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return Response(
                stream_with_context(generate()),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # 通常のレスポンス
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            assistant_message = response.choices[0].message.content
            
            return jsonify({
                "message": assistant_message,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }), 200

    except Exception as e:
        logger.error(f"Error in conversation endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/clear", methods=["POST"])
def clear_conversation():
    """会話履歴のクリア"""
    # この実装では、フロントエンド側で履歴を管理するため、
    # 成功レスポンスを返すだけ
    return jsonify({"status": "cleared"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
