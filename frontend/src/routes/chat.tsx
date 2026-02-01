import { useState } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { AvatarDisplay } from "@/components/chat/AvatarDisplay"
import { ChatInput } from "@/components/chat/ChatInput"
import { ChatMessageList } from "@/components/chat/ChatMessageList"
import { TTSSettings } from "@/components/chat/TTSSettings"
import { useChat } from "@/hooks/useChat"

export const Route = createFileRoute("/chat")({
  component: RouteComponent,
})

function RouteComponent() {
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [refText, setRefText] = useState("")
  const [speed, setSpeed] = useState(1.0)
  const [ttsEnabled, setTtsEnabled] = useState(false)

  const { messages, inputText, setInputText, isLoading, sendMessage } = useChat({
    ttsConfig: {
      audioFile,
      refText,
      speed,
      enabled: ttsEnabled,
    },
  })

  return (
    <div className="flex h-screen">
      <div className="w-2/3 flex flex-col">
        <AvatarDisplay />
        <TTSSettings
          audioFile={audioFile}
          setAudioFile={setAudioFile}
          refText={refText}
          setRefText={setRefText}
          speed={speed}
          setSpeed={setSpeed}
          ttsEnabled={ttsEnabled}
          setTtsEnabled={setTtsEnabled}
        />
        <ChatInput
          value={inputText}
          onChange={setInputText}
          onSend={sendMessage}
          isLoading={isLoading}
        />
      </div>
      <ChatMessageList messages={messages} />
    </div>
  )
}
