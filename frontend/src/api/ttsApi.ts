interface TTSRequest {
  input: string
  response_format?: "wav" | "mp3"
  speed?: number
}

interface TTSResponse {
  audio_data: string
  format: string
  sample_rate: number
}

interface TTSErrorResponse {
  error: string
  detail?: string | null
}

const API_BASE_URL = "http://localhost:8001"

export const textToSpeech = async (request: TTSRequest): Promise<TTSResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/tts/synthesize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error: TTSErrorResponse = await response.json()
    throw new Error(error.error + (error.detail ? `: ${error.detail}` : ""))
  }

  return await response.json()
}
