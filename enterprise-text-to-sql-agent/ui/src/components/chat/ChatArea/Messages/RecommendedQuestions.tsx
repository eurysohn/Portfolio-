'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useStore } from '@/store'
import { useQueryState } from 'nuqs'

const RECOMMENDED_QUESTIONS = [
  'Order fill rate last 30 days',
  'On time delivery rate this month',
  'Total revenue last month',
  'Orders count last 7 days',
  'Order fill rate yesterday',
  'On time delivery rate last 30 days'
]

const RecommendedQuestions = () => {
  const { handleStreamResponse } = useAIChatStreamHandler()
  const isStreaming = useStore((state) => state.isStreaming)
  const [agentId] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const canSend = Boolean(agentId || teamId) && !isStreaming

  const handleExampleClick = async (question: string) => {
    if (!canSend) return
    await handleStreamResponse(question)
  }

  return (
    <div className="mt-8 border-t border-primary/10 bg-gradient-to-b from-transparent to-background/50 py-6">
      <div className="mx-auto w-full max-w-2xl px-4">
        <p className="mb-3 text-sm font-semibold text-primary flex items-center gap-2">
          <span className="text-base">💡</span>
          Try another question:
        </p>
        <div className="flex flex-wrap gap-2">
          {RECOMMENDED_QUESTIONS.map((question) => (
            <Button
              key={question}
              variant="ghost"
              size="sm"
              onClick={() => handleExampleClick(question)}
              disabled={!canSend}
              className="rounded-full border border-primary/15 bg-primaryAccent px-3 py-1.5 text-xs text-primary hover:bg-primaryAccent/80 hover:scale-105 transition-all"
            >
              {question}
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RecommendedQuestions
