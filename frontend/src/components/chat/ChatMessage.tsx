import type { Message } from "@/api/chatApi"
import { Card, CardContent } from "@/components/ui/card"

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user"

  return (
    <div className={`flex items-start ${isUser ? "justify-end" : "justify-start"}`}>
      <Card className={`max-w-[70%] ${isUser ? "bg-blue-500" : "bg-gray-100"}`}>
        <CardContent className="p-3">{message.content}</CardContent>
      </Card>
    </div>
  )
}
