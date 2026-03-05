export interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
}

export interface ChatCompletionRequest {
  messages: Message[]
  stream?: boolean
  temperature?: number | null
  max_new_tokens?: number | null
}

export interface Choice {
  index: number
  message: Message
  finish_reason?: string | null
}

export interface ChatCompletionResponse {
  id: string
  object?: string
  created?: number
  choices: Choice[]
}

export interface HealthResponse {
  [key: string]: string
}

const API_BASE_URL = import.meta.env.VITE_CHAT_API_BASE_URL

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/health`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  })

  if (!response.ok) {
    throw new Error("ヘルスチェックエラー")
  }

  return response.json()
}

export const createChatCompletion = async (
  request: ChatCompletionRequest,
): Promise<ChatCompletionResponse> => {
  if (import.meta.env.VITE_USE_MOCK_API === "true") {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    return {
      id: "mock-response-id",
      created: Date.now(),
      choices: [
        {
          index: 0,
          message: {
            id: "mock-message-id",
            role: "assistant",
            content: `これはモックレスポンスです。${request.messages[request.messages.length - 1].content}`,
          },
        },
      ],
    }
  }

  const response = await fetch(`${API_BASE_URL}/api/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || "チャット送信エラー")
  }

  return response.json()
}
