export type Role = "user" | "assistant" | "system";

export type MessageStatus = "pending" | "done" | "error";

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  status?: MessageStatus;
}

export interface ChatConfig {
  title: string;
  subtitle: string;
  footer: string;
}

export interface ChatPayload {
  messages: Array<{ role: Role; content: string }>;
  stream?: boolean;
}

export interface ChatResponseBody {
  message: {
    role: "assistant";
    content: string;
  };
}
