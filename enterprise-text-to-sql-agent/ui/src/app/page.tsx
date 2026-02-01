'use client'
import Sidebar from '@/components/chat/Sidebar/Sidebar'
import { ChatArea } from '@/components/chat/ChatArea'
import { Suspense } from 'react'

export default function Home() {
  const hasEnvToken = false
  const envToken = ''
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="flex h-screen bg-background/80">
        <Sidebar hasEnvToken={hasEnvToken} envToken={envToken} />
        <ChatArea />
      </div>
    </Suspense>
  )
}
