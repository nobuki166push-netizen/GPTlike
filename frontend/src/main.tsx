import React from 'react'
import ReactDOM from 'react-dom/client'
import { initializeIcons } from '@fluentui/react'
import { PublicClientApplication } from '@azure/msal-browser'
import { MsalProvider } from '@azure/msal-react'
import { msalConfig } from './authConfig'
import App from './App'
import './index.css'

initializeIcons()

// MSAL インスタンスを作成
const msalInstance = new PublicClientApplication(msalConfig)

// MSALの初期化を待つ
msalInstance.initialize().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <App />
      </MsalProvider>
    </React.StrictMode>,
  )
})
