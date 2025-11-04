import { ChatRequest, ChatResponse, DocumentLoadRequest, DocumentLoadResponse, HealthResponse, ApiInfo } from './types'

const API_BASE_URL = '/api'

async function fetchWithError<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
    throw new Error(errorData.error || `HTTP ${response.status}`)
  }
  
  return response.json()
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const request: ChatRequest = { message }
  
  return fetchWithError<ChatResponse>(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
}

export async function loadDocuments(request: DocumentLoadRequest): Promise<DocumentLoadResponse> {
  return fetchWithError<DocumentLoadResponse>(`${API_BASE_URL}/documents/load`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
}

export async function checkHealth(): Promise<HealthResponse> {
  return fetchWithError<HealthResponse>(`${API_BASE_URL}/health`)
}

export async function getApiInfo(): Promise<ApiInfo> {
  return fetchWithError<ApiInfo>(`${API_BASE_URL}/info`)
}
