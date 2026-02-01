import { useCallback, useState } from "react"
import { textToSpeech } from "@/api/ttsApi"

export function useTTS() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const playAudio = useCallback((audioData: string, format: string) => {
    const byteCharacters = atob(audioData)
    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)

    const mimeType = format === "wav" ? "audio/wav" : "audio/mpeg"

    const blob = new Blob([byteArray], { type: mimeType })
    const url = URL.createObjectURL(blob)

    const audio = new Audio(url)
    audio.play()

    audio.onended = () => URL.revokeObjectURL(url)
  }, [])

  const speak = useCallback(
    async (
      text: string,
      options?: {
        format?: "wav" | "mp3"
        speed?: number
      },
    ) => {
      setIsGenerating(true)
      setError(null)

      try {
        const response = await textToSpeech({
          input: text,
          response_format: options?.format || "mp3",
          speed: options?.speed || 1.0,
        })
        playAudio(response.audio_data, response.format)
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "音声生成に失敗しました。"
        setError(errorMessage)
        throw err
      } finally {
        setIsGenerating(false)
      }
    },
    [playAudio],
  )

  return { speak, isGenerating, error }
}
