interface VoiceCloneRequest {
  audio_file: File
  input: string
  ref_text: string
  speed?: number
}

interface VoiceCloneResponse {
  audio_data: string
}

interface TTSErrorResponse {
  error: string
  detail?: string | null
}

const API_BASE_URL = import.meta.env.VITE_TTS_API_BASE_URL

export const voiceClone = async (
  request: VoiceCloneRequest,
): Promise<VoiceCloneResponse> => {
  const formData = new FormData()
  formData.append("audio_file", request.audio_file)
  formData.append("input", request.input)
  formData.append("ref_text", request.ref_text)
  formData.append("speed", (request.speed || 1.0).toString())

  const response = await fetch(`${API_BASE_URL}/api/tts/voice-clone`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const error: TTSErrorResponse = await response.json()
    throw new Error(error.error + (error.detail ? `: ${error.detail}` : ""))
  }

  return await response.json()
}
