import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { AvatarDisplay } from "@/components/chat/AvatarDisplay"
import { ChatInput } from "@/components/chat/ChatInput"
import { ChatMessageList } from "@/components/chat/ChatMessageList"
import { LipsyncSettings } from "@/components/chat/LipsyncSettings"
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

  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [lipsyncEnabled, setLipsyncEnabled] = useState(false)
  const [bboxShift, setBboxShift] = useState(0)
  const [extraMargin, setExtraMargin] = useState(10)
  const [parsingMode, setParsingMode] = useState<"jaw" | "face">("jaw")

  const {
    messages,
    inputText,
    setInputText,
    isLoading,
    sendMessage,
    videoUrl,
    isGeneratingVideo,
  } = useChat({
    ttsConfig: {
      audioFile,
      refText,
      speed,
      enabled: ttsEnabled,
    },
    lipsyncConfig: {
      videoFile,
      enabled: lipsyncEnabled,
      bboxShift,
      extraMargin,
      parsingMode,
    },
  })

  return (
    <div className="flex h-screen">
      <div className="w-2/3 flex flex-col">
        <AvatarDisplay videoUrl={videoUrl} isGenerating={isGeneratingVideo} />
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
        <LipsyncSettings
          videoFile={videoFile}
          setVideoFile={setVideoFile}
          lipsyncEnabled={lipsyncEnabled}
          setLipsyncEnabled={setLipsyncEnabled}
          bboxShift={bboxShift}
          setBboxShift={setBboxShift}
          extraMargin={extraMargin}
          setExtraMargin={setExtraMargin}
          parsingMode={parsingMode}
          setParsingMode={setParsingMode}
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
