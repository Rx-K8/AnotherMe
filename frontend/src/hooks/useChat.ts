import { useState } from "react"
import { createChatCompletion, type Message } from "@/api/chatApi"
import { useLipsync } from "./useLipsync"
import { useTTS } from "./useTTS"

interface LipsyncConfig {
  videoFile: File | null
  enabled: boolean
  bboxShift: number
  extraMargin: number
  parsingMode: "jaw" | "face"
}

interface UseChatOptions {
  ttsConfig?: {
    audioFile: File | null
    refText: string
    speed: number
    enabled: boolean
  }
  lipsyncConfig?: LipsyncConfig
}

export function useChat(options?: UseChatOptions) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const { generateAudio, isGenerating: isGeneratingAudio } = useTTS()
  const {
    generate: generateVideo,
    isGenerating: isGeneratingVideo,
    videoUrl,
    clearVideo,
  } = useLipsync()

  const sendMessage = async () => {
    if (!inputText.trim()) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: inputText,
    }
    setMessages([...messages, userMessage])
    setInputText("")
    setIsLoading(true)

    try {
      const response = await createChatCompletion({
        messages: [...messages, userMessage],
      })

      const aiMessage: Message = {
        ...response.choices[0].message,
        id: crypto.randomUUID(),
      }
      setMessages((prev) => [...prev, aiMessage])

      const ttsConfig = options?.ttsConfig
      const lipsyncConfig = options?.lipsyncConfig
      const ttsReady =
        ttsConfig?.enabled &&
        ttsConfig.audioFile &&
        ttsConfig.refText.trim() &&
        aiMessage.content

      if (ttsReady && ttsConfig.audioFile) {
        const audioBase64 = await generateAudio(aiMessage.content, {
          audioFile: ttsConfig.audioFile,
          refText: ttsConfig.refText,
          speed: ttsConfig.speed,
        })

        if (lipsyncConfig?.enabled && lipsyncConfig.videoFile) {
          await generateVideo(audioBase64, lipsyncConfig.videoFile, {
            bbox_shift: lipsyncConfig.bboxShift,
            extra_margin: lipsyncConfig.extraMargin,
            parsing_mode: lipsyncConfig.parsingMode,
          })
        } else {
          playAudioFromBase64(audioBase64)
        }
      }
    } catch (error) {
      console.error("チャット送信エラー:", error)
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  return {
    messages,
    inputText,
    setInputText,
    isLoading,
    isGeneratingAudio,
    isGeneratingVideo,
    videoUrl,
    clearVideo,
    sendMessage,
  }
}

function playAudioFromBase64(base64: string): void {
  const byteCharacters = atob(base64)
  const byteNumbers = new Uint8Array(byteCharacters.length)
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i)
  }
  const blob = new Blob([byteNumbers], { type: "audio/wav" })
  const url = URL.createObjectURL(blob)
  const audio = new Audio(url)
  audio.play()
  audio.onended = () => URL.revokeObjectURL(url)
}
