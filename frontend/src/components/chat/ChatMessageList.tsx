import type { Message } from "@/api/chatApi"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ChatMessage } from "./ChatMessage"

interface ChatMessageListProps {
  messages: Message[]
}

export function ChatMessageList({ messages }: ChatMessageListProps) {
  return (
    <div className="w-1/3 bg-gray-500 h-screen overflow-hidden">
      <ScrollArea className="h-full">
        <div className="flex flex-col gap-4 p-4">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}
