'use client'

import { useStore } from '@/store'
import { useEffect, useRef } from 'react'
import Messages from './Messages'
import ScrollToBottom from '@/components/chat/ChatArea/ScrollToBottom'

const MessageArea = () => {
  const { messages } = useStore()
  const containerRef = useRef<HTMLDivElement>(null)
  const lastUserMessageRef = useRef<HTMLDivElement>(null)
  const isAtBottom = useRef(true)

  // Scroll to user's question when a new message is added
  useEffect(() => {
    if (messages.length > 0 && lastUserMessageRef.current) {
      const lastMessage = messages[messages.length - 1]
      const secondLastMessage = messages[messages.length - 2]
      
      // If the last message is an agent response and second last is user question
      if (lastMessage.role === 'agent' && secondLastMessage?.role === 'user') {
        // Scroll to show the user's question at the top
        lastUserMessageRef.current.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        })
      }
    }
  }, [messages])

  const scrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }

  const handleScroll = () => {
    if (containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current
      isAtBottom.current = scrollTop + clientHeight >= scrollHeight - 10
    }
  }

  return (
    <div className="relative mb-4 flex max-h-[calc(100vh-64px)] min-h-0 flex-grow flex-col">
      <div 
        ref={containerRef}
        onScroll={handleScroll}
        className="flex min-h-full flex-col overflow-y-auto"
      >
        <div className="mx-auto w-full max-w-2xl space-y-9 px-4 pb-4">
          <Messages messages={messages} lastUserMessageRef={lastUserMessageRef} />
        </div>
      </div>
      <ScrollToBottom scrollToBottom={scrollToBottom} isAtBottom={isAtBottom.current} />
    </div>
  )
}

export default MessageArea
