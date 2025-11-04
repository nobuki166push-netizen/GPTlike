import { useCallback, useMemo, useState } from "react";

import { sendChat } from "../api/chatApi";
import type { ChatMessage } from "../types";

const createId = () =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const payloadMessages = useMemo(
    () => messages.filter((m) => m.role !== "system").map(({ role, content }) => ({ role, content })),
    [messages]
  );

  const send = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      const userMessage: ChatMessage = {
        id: createId(),
        role: "user",
        content: text.trim(),
        status: "done"
      };

      const assistantMessage: ChatMessage = {
        id: createId(),
        role: "assistant",
        content: "...",
        status: "pending"
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setInput("");
      setIsLoading(true);
      setError(null);

      try {
        const response = await sendChat({
          messages: [...payloadMessages, { role: "user", content: userMessage.content }],
          stream: false
        });

        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantMessage.id
              ? { ...message, content: response.message.content, status: "done" }
              : message
          )
        );
      } catch (err) {
        const message = err instanceof Error ? err.message : "不明なエラーが発生しました。";
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantMessage.id ? { ...m, content: message, status: "error" } : m))
        );
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [payloadMessages]
  );

  const reset = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    input,
    setInput,
    isLoading,
    error,
    send,
    reset
  };
}
