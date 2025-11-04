FROM node:20-alpine as builder

WORKDIR /app

# 依存関係のインストール
COPY package*.json ./
RUN npm ci

# アプリケーションのビルド
COPY . .
RUN npm run build

# 本番環境用のイメージ
FROM nginx:alpine

# ビルド成果物をnginxにコピー
COPY --from=builder /app/dist /usr/share/nginx/html

# nginxの設定ファイル
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
