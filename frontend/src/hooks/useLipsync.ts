import { useCallback, useRef, useState } from "react"
import { generateLipsync } from "@/api/lipsyncApi"

interface LipsyncOptions {
  bbox_shift?: number
  extra_margin?: number
  parsing_mode?: "jaw" | "face"
}

function base64ToBlob(base64: string, mimeType: string): Blob {
  const byteCharacters = atob(base64)
  const byteNumbers = new Uint8Array(byteCharacters.length)
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i)
  }
  return new Blob([byteNumbers], { type: mimeType })
}

export function useLipsync() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const videoUrlRef = useRef<string | null>(null)

  const revokeCurrentUrl = useCallback(() => {
    if (videoUrlRef.current) {
      URL.revokeObjectURL(videoUrlRef.current)
      videoUrlRef.current = null
    }
  }, [])

  const generate = useCallback(
    async (
      audioBase64: string,
      videoFile: File,
      options?: LipsyncOptions,
    ): Promise<void> => {
      setIsGenerating(true)
      setError(null)
      revokeCurrentUrl()

      try {
        const audioBlob = base64ToBlob(audioBase64, "audio/wav")
        const result = await generateLipsync({
          audio: audioBlob,
          video: videoFile,
          ...options,
        })

        const videoBlob = base64ToBlob(result.video_data, "video/mp4")
        const url = URL.createObjectURL(videoBlob)
        videoUrlRef.current = url
        setVideoUrl(url)
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "動画生成に失敗しました。"
        setError(errorMessage)
        setVideoUrl(null)
      } finally {
        setIsGenerating(false)
      }
    },
    [revokeCurrentUrl],
  )

  const clearVideo = useCallback(() => {
    revokeCurrentUrl()
    setVideoUrl(null)
  }, [revokeCurrentUrl])

  return { generate, isGenerating, videoUrl, error, clearVideo }
}
