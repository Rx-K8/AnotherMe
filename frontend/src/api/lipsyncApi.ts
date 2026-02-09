interface LipsyncRequest {
  audio: Blob
  video: File
  bbox_shift?: number
  extra_margin?: number
  parsing_mode?: "jaw" | "face"
}

interface LipsyncResponse {
  video_data: string
  duration_seconds: number
  processing_time_ms: number
}

interface LipsyncErrorResponse {
  error: string
  detail?: string | null
}

export const generateLipsync = async (
  request: LipsyncRequest,
): Promise<LipsyncResponse> => {
  const API_BASE_URL = import.meta.env.VITE_LIPSYNC_API_BASE_URL
  const formData = new FormData()
  formData.append("audio_file", request.audio)
  formData.append("video_file", request.video)
  formData.append("bbox_shift", (request.bbox_shift ?? 0).toString())
  formData.append("extra_margin", (request.extra_margin ?? 10).toString())
  formData.append("parsing_mode", request.parsing_mode ?? "jaw")

  const response = await fetch(`${API_BASE_URL}/api/lipsync/generate`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const error: LipsyncErrorResponse = await response.json()
    throw new Error(error.error + (error.detail ? `: ${error.detail}` : ""))
  }

  return await response.json()
}
