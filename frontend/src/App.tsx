import { useState } from 'react'
import ChatContainer from './components/ChatContainer'
import './App.css'

function App() {
  const [darkMode] = useState(true)

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      <header className="app-header">
        <div className="header-content">
          <h1>Azure OpenAI Chat</h1>
          <p className="subtitle">GPTを使った対話型チャットアプリケーション</p>
        </div>
      </header>
      <main className="app-main">
        <ChatContainer />
      </main>
    </div>
  )
}

export default App
