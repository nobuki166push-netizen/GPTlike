import type { ChatMessage } from "../types";

interface ChatMessageProps {
  message: ChatMessage;
}

export function ChatMessageItem({ message }: ChatMessageProps) {
  const isAssistant = message.role === "assistant";
  const initials = isAssistant ? "AI" : "You";

  return (
    <div className={`message ${isAssistant ? "message--assistant" : "message--user"}`}>
      <span className="message__avatar" aria-hidden>
        {initials}
      </span>
      <div className="message__content">
        {message.content}
        {message.status === "pending" && "_"}
      </div>
    </div>
  );
}
