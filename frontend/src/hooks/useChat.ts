import { useState } from "react"
import { createChatCompletion, type Message } from "@/api/chatApi"
import { useTTS } from "./useTTS"

interface UseChatOptions {
  ttsConfig?: {
    audioFile: File | null
    refText: string
    speed: number
    enabled: boolean
  }
}

export function useChat(options?: UseChatOptions) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const { speak, isGenerating: isGeneratingAudio } = useTTS()

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
      if (
        ttsConfig?.enabled &&
        ttsConfig.audioFile &&
        ttsConfig.refText.trim() &&
        aiMessage.content
      ) {
        speak(aiMessage.content, {
          audioFile: ttsConfig.audioFile,
          refText: ttsConfig.refText,
          speed: ttsConfig.speed,
        }).catch(console.error)
      }
    } catch (error) {
      console.error("チャット送信エラー:", error)
      // エラー時はユーザーメッセージを削除
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
    sendMessage,
  }
}
