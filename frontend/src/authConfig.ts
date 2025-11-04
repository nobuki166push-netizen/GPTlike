import { Configuration, PopupRequest } from '@azure/msal-browser'

// Entra ID (Azure AD) 認証設定
// 環境変数から読み込むか、デフォルト値を使用
export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_ENTRA_CLIENT_ID || 'YOUR_CLIENT_ID',
    authority: import.meta.env.VITE_ENTRA_AUTHORITY || 'https://login.microsoftonline.com/YOUR_TENANT_ID',
    redirectUri: import.meta.env.VITE_REDIRECT_URI || window.location.origin,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
}

// アクセストークンリクエストのスコープ
export const loginRequest: PopupRequest = {
  scopes: [
    'User.Read', // Microsoft Graph API
    // Azure Functionsのスコープ（App Registration後に設定）
    // 例: 'api://YOUR_API_CLIENT_ID/access_as_user'
  ],
}

// APIアクセス用のトークンリクエスト
export const apiRequest: PopupRequest = {
  scopes: [
    import.meta.env.VITE_API_SCOPE || 'api://YOUR_API_CLIENT_ID/access_as_user',
  ],
}
