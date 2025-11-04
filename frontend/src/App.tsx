import { FormEvent, useEffect, useState } from "react";

import { ChatMessageItem } from "./components/ChatMessage";
import { fetchConfig } from "./api/chatApi";
import { useChat } from "./hooks/useChat";
import type { ChatConfig } from "./types";

function App() {
  const { messages, input, setInput, send, isLoading, error, reset } = useChat();
  const [config, setConfig] = useState<ChatConfig | null>(null);
  const [configError, setConfigError] = useState<string | null>(null);

  useEffect(() => {
    fetchConfig()
      .then(setConfig)
      .catch((err) => setConfigError(err instanceof Error ? err.message : "設定の取得に失敗しました。"));
  }, []);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim()) return;
    void send(input);
  };

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">{config?.title ?? "Azure Chat"}</h1>
        <p className="app__subtitle">{config?.subtitle ?? "Azure OpenAI と対話しましょう。"}</p>
        {configError && <small role="alert">{configError}</small>}
      </header>

      <section className="chat-panel" aria-live="polite">
        <div className="message-list">
          {messages.length === 0 && <p>はじめまして！質問を入力してください。</p>}
          {messages.map((message) => (
            <ChatMessageItem key={message.id} message={message} />
          ))}
        </div>

        <form className="chat-form" onSubmit={handleSubmit}>
          <textarea
            placeholder="Azure OpenAI に質問をしてみましょう"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            送信
          </button>
        </form>

        <div>
          <button type="button" onClick={reset} disabled={isLoading || messages.length === 0}>
            履歴をクリア
          </button>
          {error && (
            <small role="alert" style={{ marginLeft: "12px", color: "#f87171" }}>
              {error}
            </small>
          )}
        </div>
      </section>

      <footer className="footer">{config?.footer ?? "Powered by Azure OpenAI"}</footer>
    </div>
  );
}

export default App;

