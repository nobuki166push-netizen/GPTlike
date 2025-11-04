#!/bin/bash

# GPTlike Agentic RAG デプロイスクリプト

set -e

echo "🚀 GPTlike Agentic RAG デプロイを開始します..."

# フロントエンドのビルド
echo "📦 フロントエンドをビルドしています..."
cd frontend
npm install
npm run build
cd ..

echo "✅ フロントエンドのビルドが完了しました"

# Azure Functionsにデプロイ
echo "☁️  Azure Functionsにデプロイしています..."

if [ -z "$1" ]; then
  echo "❌ エラー: Function App名を指定してください"
  echo "使用方法: ./deploy.sh <function-app-name>"
  exit 1
fi

FUNCTION_APP_NAME=$1

func azure functionapp publish $FUNCTION_APP_NAME

echo "✅ デプロイが完了しました！"
echo "🌐 アプリにアクセス: https://${FUNCTION_APP_NAME}.azurewebsites.net"
