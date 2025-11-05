import { useState, useEffect } from 'react'
import { Stack, Text, Link, PrimaryButton, DefaultButton, Persona, PersonaSize } from '@fluentui/react'
import { useMsal, useIsAuthenticated } from '@azure/msal-react'
import { loginRequest } from './authConfig'
import Chat from './components/Chat'
import { getApiInfo } from './api'
import { ApiInfo } from './types'
import './App.css'

function App() {
  const [apiInfo, setApiInfo] = useState<ApiInfo | null>(null)
  const [showInfo, setShowInfo] = useState(false)
  
  const { instance, accounts } = useMsal()
  const isAuthenticated = useIsAuthenticated()

  useEffect(() => {
    getApiInfo()
      .then(setApiInfo)
      .catch(console.error)
  }, [])

  // アクセストークン取得関数を設定
  useEffect(() => {
    const { setAccessTokenGetter } = require('./api')
    setAccessTokenGetter(async () => {
      if (!isAuthenticated || accounts.length === 0) {
        return null
      }

      try {
        const response = await instance.acquireTokenSilent({
          scopes: [import.meta.env.VITE_API_SCOPE || 'User.Read'],
          account: accounts[0],
        })
        return response.accessToken
      } catch (error) {
        console.error('Token acquisition failed:', error)
        return null
      }
    })
  }, [instance, accounts, isAuthenticated])

  const handleLogin = () => {
    instance.loginPopup(loginRequest).catch((error) => {
      console.error('Login error:', error)
    })
  }

  const handleLogout = () => {
    instance.logoutPopup().catch((error) => {
      console.error('Logout error:', error)
    })
  }

  return (
    <Stack className="app-container" tokens={{ childrenGap: 0 }}>
      <Stack className="header" horizontal horizontalAlign="space-between" verticalAlign="center">
        <Stack horizontal tokens={{ childrenGap: 16 }} verticalAlign="center">
          <Text variant="xLarge" className="app-title">
            🤖 GPTlike - Agentic RAG Chat
          </Text>
          {apiInfo && (
            <Text variant="small" className="version-badge">
              v{apiInfo.version}
            </Text>
          )}
        </Stack>
        <Stack horizontal tokens={{ childrenGap: 12 }} verticalAlign="center">
          {isAuthenticated ? (
            <>
              <Persona
                text={accounts[0]?.name || accounts[0]?.username || 'User'}
                size={PersonaSize.size32}
                styles={{
                  root: { color: 'white' },
                  primaryText: { color: 'white' }
                }}
              />
              <DefaultButton
                text="ログアウト"
                onClick={handleLogout}
                iconProps={{ iconName: 'SignOut' }}
                styles={{
                  root: { backgroundColor: 'rgba(255, 255, 255, 0.2)', color: 'white', border: 'none' },
                  rootHovered: { backgroundColor: 'rgba(255, 255, 255, 0.3)', color: 'white' }
                }}
              />
            </>
          ) : (
            <PrimaryButton
              text="ログイン"
              onClick={handleLogin}
              iconProps={{ iconName: 'Signin' }}
              styles={{
                root: { backgroundColor: 'white', color: '#0078d4' },
                rootHovered: { backgroundColor: '#f3f2f1', color: '#0078d4' }
              }}
            />
          )}
          <PrimaryButton
            text={showInfo ? '情報を閉じる' : 'システム情報'}
            onClick={() => setShowInfo(!showInfo)}
            iconProps={{ iconName: 'Info' }}
            styles={{
              root: { backgroundColor: 'rgba(255, 255, 255, 0.2)', color: 'white', border: 'none' },
              rootHovered: { backgroundColor: 'rgba(255, 255, 255, 0.3)', color: 'white' }
            }}
          />
          <Link
            href="https://github.com/microsoft/agent-framework"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </Link>
        </Stack>
      </Stack>

      {showInfo && apiInfo && (
        <Stack className="info-panel" tokens={{ childrenGap: 12 }}>
          <Text variant="mediumPlus" className="info-title">システム情報</Text>
          <Stack tokens={{ childrenGap: 8 }}>
            <Text>
              <strong>サービス:</strong> {apiInfo.service}
            </Text>
            <Stack tokens={{ childrenGap: 4 }}>
              <Text><strong>機能:</strong></Text>
              <ul className="features-list">
                {apiInfo.features.map((feature, index) => (
                  <li key={index}>{feature}</li>
                ))}
              </ul>
            </Stack>
          </Stack>
        </Stack>
      )}

      <Stack className="chat-container" grow>
        <Chat />
      </Stack>

      <Stack className="footer" horizontal horizontalAlign="center">
        <Text variant="small" className="footer-text">
          Powered by Microsoft Agent Framework + Azure OpenAI
        </Text>
      </Stack>
    </Stack>
  )
}

export default App
