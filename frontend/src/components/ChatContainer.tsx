import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import './ChatContainer.css'

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}

function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return

    const newUserMessage: Message = {
      role: 'user',
      content: content.trim()
    }

    setMessages(prev => [...prev, newUserMessage])
    setIsLoading(true)
    setError(null)

    try {
      const response = await axios.post('/api/conversation', {
        messages: [...messages, newUserMessage],
        stream: false
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.message
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Error sending message:', err)
      setError('メッセージの送信に失敗しました。もう一度お試しください。')
      // エラー時はユーザーメッセージを削除
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearChat = async () => {
    try {
      await axios.post('/api/clear')
      setMessages([])
      setError(null)
    } catch (err) {
      console.error('Error clearing chat:', err)
      // エラーが発生しても履歴をクリアする
      setMessages([])
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-content">
              <h2>👋 こんにちは！</h2>
              <p>何でもお聞きください。AIがお答えします。</p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && (
              <div className="loading-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <ChatInput
        onSendMessage={handleSendMessage}
        onClearChat={handleClearChat}
        disabled={isLoading}
        hasMessages={messages.length > 0}
      />
    </div>
  )
}

export default ChatContainer
