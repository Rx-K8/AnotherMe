import { createFileRoute } from "@tanstack/react-router"
import { AvatarDisplay } from "@/components/chat/AvatarDisplay"
import { ChatInput } from "@/components/chat/ChatInput"
import { ChatMessageList } from "@/components/chat/ChatMessageList"
import { useChat } from "@/hooks/useChat"

export const Route = createFileRoute("/chat")({
  component: RouteComponent,
})

function RouteComponent() {
  const { messages, inputText, setInputText, isLoading, sendMessage } = useChat()

  return (
    <div className="flex h-screen">
      <div className="w-2/3 flex flex-col">
        <AvatarDisplay />
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
