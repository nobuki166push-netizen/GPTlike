import { useState, useEffect, useRef } from 'react'
import { Stack, TextField, PrimaryButton, Spinner, SpinnerSize, Text, IconButton } from '@fluentui/react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import { sendChatMessage, loadDocuments } from '../api'
import { ChatMessage } from '../types'
import './Chat.css'

function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showDocLoader, setShowDocLoader] = useState(false)
  const [docTexts, setDocTexts] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await sendChatMessage(inputValue)
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer || response.message,
        timestamp: new Date(response.timestamp),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'error',
        content: `エラーが発生しました: ${error instanceof Error ? error.message : '不明なエラー'}`,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleLoadDocuments = async () => {
    if (!docTexts.trim()) return

    setIsLoading(true)
    try {
      const texts = docTexts.split('\n---\n').filter(t => t.trim())
      await loadDocuments({ texts })
      
      const successMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `✅ ${texts.length}個のドキュメントをロードしました。これで質問に答えることができます。`,
        timestamp: new Date(),
      }
      
      setMessages((prev) => [...prev, successMessage])
      setDocTexts('')
      setShowDocLoader(false)
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'error',
        content: `ドキュメントのロードに失敗: ${error instanceof Error ? error.message : '不明なエラー'}`,
        timestamp: new Date(),
      }
      
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <Stack className="chat-wrapper" tokens={{ childrenGap: 0 }}>
      <Stack horizontal horizontalAlign="space-between" className="chat-header">
        <Text variant="medium" className="chat-header-title">
          💬 チャット
        </Text>
        <Stack horizontal tokens={{ childrenGap: 8 }}>
          <IconButton
            iconProps={{ iconName: 'CloudUpload' }}
            title="ドキュメントをロード"
            onClick={() => setShowDocLoader(!showDocLoader)}
          />
          <IconButton
            iconProps={{ iconName: 'Delete' }}
            title="チャットをクリア"
            onClick={clearChat}
          />
        </Stack>
      </Stack>

      {showDocLoader && (
        <Stack className="doc-loader-panel" tokens={{ childrenGap: 12 }}>
          <Text variant="mediumPlus" className="doc-loader-title">
            📄 ドキュメントをロード
          </Text>
          <Text variant="small" className="doc-loader-help">
            複数のドキュメントを入力する場合は「---」で区切ってください
          </Text>
          <TextField
            multiline
            rows={6}
            value={docTexts}
            onChange={(_, value) => setDocTexts(value || '')}
            placeholder="ドキュメントの内容を入力してください...&#10;&#10;---&#10;&#10;次のドキュメント..."
          />
          <Stack horizontal tokens={{ childrenGap: 8 }}>
            <PrimaryButton
              text="ロード"
              onClick={handleLoadDocuments}
              disabled={!docTexts.trim() || isLoading}
            />
            <PrimaryButton
              text="キャンセル"
              onClick={() => {
                setShowDocLoader(false)
                setDocTexts('')
              }}
            />
          </Stack>
        </Stack>
      )}

      <Stack className="messages-container" tokens={{ childrenGap: 16 }}>
        {messages.length === 0 && (
          <Stack className="welcome-message" horizontalAlign="center" verticalAlign="center">
            <Text variant="xxLarge" className="welcome-icon">🤖</Text>
            <Text variant="xLarge" className="welcome-title">
              GPTlike エージェンティックRAGへようこそ
            </Text>
            <Text variant="medium" className="welcome-subtitle">
              質問を入力してください。エージェントが最適なツールを使って回答します。
            </Text>
            <Stack tokens={{ childrenGap: 8 }} className="welcome-tips">
              <Text variant="small"><strong>ヒント:</strong></Text>
              <Text variant="small">• まずドキュメントをロードしてください</Text>
              <Text variant="small">• エージェントは自動的に検索ツールを使用します</Text>
              <Text variant="small">• Azure AI Searchとも統合されています</Text>
            </Stack>
          </Stack>
        )}

        {messages.map((message) => (
          <Stack
            key={message.id}
            className={`message message-${message.role}`}
            tokens={{ childrenGap: 8 }}
          >
            <Stack horizontal tokens={{ childrenGap: 8 }} verticalAlign="center">
              <Text className="message-role-icon">
                {message.role === 'user' ? '👤' : message.role === 'error' ? '⚠️' : '🤖'}
              </Text>
              <Text variant="small" className="message-role">
                {message.role === 'user' ? 'あなた' : message.role === 'error' ? 'エラー' : 'アシスタント'}
              </Text>
              <Text variant="small" className="message-timestamp">
                {message.timestamp.toLocaleTimeString('ja-JP')}
              </Text>
            </Stack>
            <Stack className="message-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
              >
                {message.content}
              </ReactMarkdown>
            </Stack>
          </Stack>
        ))}

        {isLoading && (
          <Stack horizontal tokens={{ childrenGap: 12 }} verticalAlign="center" className="loading-indicator">
            <Spinner size={SpinnerSize.small} />
            <Text variant="small">エージェントが考えています...</Text>
          </Stack>
        )}

        <div ref={messagesEndRef} />
      </Stack>

      <Stack className="input-container" tokens={{ childrenGap: 12 }}>
        <TextField
          multiline
          rows={3}
          value={inputValue}
          onChange={(_, value) => setInputValue(value || '')}
          onKeyPress={handleKeyPress}
          placeholder="メッセージを入力してください... (Enterで送信、Shift+Enterで改行)"
          disabled={isLoading}
        />
        <Stack horizontal horizontalAlign="end">
          <PrimaryButton
            text={isLoading ? '送信中...' : '送信'}
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            iconProps={{ iconName: 'Send' }}
          />
        </Stack>
      </Stack>
    </Stack>
  )
}

export default Chat
