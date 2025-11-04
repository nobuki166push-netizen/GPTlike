import { useState, KeyboardEvent } from 'react'
import './ChatInput.css'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  onClearChat: () => void
  disabled: boolean
  hasMessages: boolean
}

function ChatInput({ onSendMessage, onClearChat, disabled, hasMessages }: ChatInputProps) {
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input)
      setInput('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-input-container">
      <div className="input-wrapper">
        <textarea
          className="chat-textarea"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="メッセージを入力してください..."
          disabled={disabled}
          rows={1}
        />
        <div className="input-actions">
          {hasMessages && (
            <button
              className="clear-button"
              onClick={onClearChat}
              disabled={disabled}
              title="チャットをクリア"
            >
              🗑️ クリア
            </button>
          )}
          <button
            className="send-button"
            onClick={handleSend}
            disabled={disabled || !input.trim()}
            title="送信"
          >
            ➤ 送信
          </button>
        </div>
      </div>
      <div className="input-hint">
        Enterキーで送信 / Shift + Enterで改行
      </div>
    </div>
  )
}

export default ChatInput
