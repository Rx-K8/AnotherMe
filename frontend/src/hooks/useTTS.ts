import { useCallback, useState } from "react"
import { voiceClone } from "@/api/ttsApi"

interface GenerateAudioOptions {
  audioFile: File
  refText: string
  speed?: number
}

export function useTTS() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generateAudio = useCallback(
    async (text: string, options: GenerateAudioOptions): Promise<string> => {
      setIsGenerating(true)
      setError(null)

      try {
        const response = await voiceClone({
          audio_file: options.audioFile,
          input: text,
          ref_text: options.refText,
          speed: options.speed || 1.0,
        })
        return response.audio_data
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "音声生成に失敗しました。"
        setError(errorMessage)
        throw err
      } finally {
        setIsGenerating(false)
      }
    },
    [],
  )

  return { generateAudio, isGenerating, error }
}
