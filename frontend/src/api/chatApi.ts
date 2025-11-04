import type { ChatConfig, ChatPayload, ChatResponseBody } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

const withBase = (path: string) => `${API_BASE}${path}`;

export async function fetchConfig(): Promise<ChatConfig> {
  const response = await fetch(withBase("/api/config"));
  if (!response.ok) {
    throw new Error("設定情報の取得に失敗しました。");
  }
  return response.json();
}

export async function sendChat(payload: ChatPayload): Promise<ChatResponseBody> {
  const response = await fetch(withBase("/api/chat"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const message = await response.json().catch(() => ({}));
    const detail = (message as { detail?: string }).detail ?? "チャットの呼び出しに失敗しました。";
    throw new Error(detail);
  }

  return response.json();
}
