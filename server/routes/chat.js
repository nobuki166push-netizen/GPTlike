const { OpenAIClient, AzureKeyCredential } = require('@azure/openai');

// Azure OpenAI クライアントの初期化
const endpoint = process.env.AZURE_OPENAI_ENDPOINT;
const apiKey = process.env.AZURE_OPENAI_API_KEY;
const deploymentName = process.env.AZURE_OPENAI_DEPLOYMENT_NAME;
const apiVersion = process.env.AZURE_OPENAI_API_VERSION || '2024-02-15-preview';

if (!endpoint || !apiKey || !deploymentName) {
  console.error('Azure OpenAI の設定が不完全です。環境変数を確認してください。');
}

const client = endpoint && apiKey && deploymentName
  ? new OpenAIClient(endpoint, new AzureKeyCredential(apiKey))
  : null;

/**
 * チャットリクエストを処理
 */
async function chatHandler(req, res) {
  try {
    const { messages } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ 
        error: 'messages 配列が必要です' 
      });
    }

    if (!client) {
      return res.status(500).json({ 
        error: 'Azure OpenAI クライアントが初期化されていません' 
      });
    }

    // Azure OpenAI API を呼び出し
    const events = await client.streamChatCompletions(
      deploymentName,
      messages,
      {
        maxTokens: 800,
        temperature: 0.7,
        topP: 0.95,
        frequencyPenalty: 0,
        presencePenalty: 0,
        stop: null,
      }
    );

    let fullResponse = '';
    
    // ストリーミングレスポンスを処理
    for await (const event of events) {
      for (const choice of event.choices) {
        const delta = choice.delta?.content;
        if (delta) {
          fullResponse += delta;
        }
      }
    }

    // 完全なレスポンスを返す
    res.json({
      message: {
        role: 'assistant',
        content: fullResponse
      }
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ 
      error: 'チャット処理中にエラーが発生しました',
      message: error.message 
    });
  }
}

module.exports = { chatHandler };
