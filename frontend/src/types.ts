export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'error'
  content: string
  timestamp: Date
}

export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  status: string
  message: string
  answer: string
  timestamp: string
}

export interface DocumentLoadRequest {
  texts?: string[]
  metadata?: Record<string, any>[]
  from_blob?: boolean
  container_name?: string
}

export interface DocumentLoadResponse {
  status: string
  message: string
}

export interface HealthResponse {
  status: string
  service: string
  version: string
  timestamp: string
}

export interface ApiInfo {
  service: string
  version: string
  endpoints: Record<string, {
    path: string
    method: string
    description: string
  }>
  features: string[]
}
