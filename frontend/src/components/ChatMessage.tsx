import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { Message } from './ChatContainer'
import './ChatMessage.css'

interface ChatMessageProps {
  message: Message
}

function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  // マークダウンをHTMLに変換してサニタイズ
  const getFormattedContent = () => {
    if (isUser) {
      // ユーザーメッセージはそのまま表示
      return message.content
    } else {
      // アシスタントのメッセージはマークダウンとして処理
      const rawHtml = marked(message.content) as string
      return DOMPurify.sanitize(rawHtml)
    }
  }

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-role">
          {isUser ? 'あなた' : 'AI アシスタント'}
        </div>
        <div className="message-text">
          {isUser ? (
            <p>{getFormattedContent()}</p>
          ) : (
            <div 
              className="markdown-content"
              dangerouslySetInnerHTML={{ __html: getFormattedContent() }}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
