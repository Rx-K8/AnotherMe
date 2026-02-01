import { useCallback, useState } from "react"
import { voiceClone } from "@/api/ttsApi"

export function useTTS() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const playAudio = useCallback((audioData: string) => {
    const byteCharacters = atob(audioData)
    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)

    const blob = new Blob([byteArray], { type: "audio/wav" })
    const url = URL.createObjectURL(blob)

    const audio = new Audio(url)
    audio.play()

    audio.onended = () => URL.revokeObjectURL(url)
  }, [])

  const speak = useCallback(
    async (
      text: string,
      options: {
        audioFile: File
        refText: string
        speed?: number
      },
    ) => {
      setIsGenerating(true)
      setError(null)

      try {
        const response = await voiceClone({
          audio_file: options.audioFile,
          input: text,
          ref_text: options.refText,
          speed: options.speed || 1.0,
        })
        playAudio(response.audio_data)
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
