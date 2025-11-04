import { useState, useEffect } from 'react'
import { Stack, Text, Link, PrimaryButton } from '@fluentui/react'
import Chat from './components/Chat'
import { getApiInfo } from './api'
import { ApiInfo } from './types'
import './App.css'

function App() {
  const [apiInfo, setApiInfo] = useState<ApiInfo | null>(null)
  const [showInfo, setShowInfo] = useState(false)

  useEffect(() => {
    getApiInfo()
      .then(setApiInfo)
      .catch(console.error)
  }, [])

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
        <Stack horizontal tokens={{ childrenGap: 8 }}>
          <PrimaryButton
            text={showInfo ? '情報を閉じる' : 'システム情報'}
            onClick={() => setShowInfo(!showInfo)}
            iconProps={{ iconName: 'Info' }}
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
