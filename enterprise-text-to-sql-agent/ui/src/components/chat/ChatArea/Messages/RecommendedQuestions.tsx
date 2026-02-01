'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useStore } from '@/store'
import { useQueryState } from 'nuqs'

const RULE_BASED_QUESTIONS = [
  { text: 'Order fill rate last 30 days', badge: '⚡ Rule' },
  { text: 'On time delivery rate this month', badge: '⚡ Rule' },
  { text: 'Late ship rate last 7 days', badge: '⚡ Rule' },
  { text: 'Total revenue last month', badge: '⚡ Rule' }
]

const LLM_QUESTIONS = [
  { text: 'Total revenue for shipped orders last 30 days', badge: '🤖 LLM' },
  { text: 'How many products do we have in stock right now?', badge: '🤖 LLM' },
  { text: 'Average order value this month', badge: '🤖 LLM' }
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
          Try these questions:
        </p>
        
        {/* Rule-based questions */}
        <div className="mb-4">
          <p className="mb-2 text-xs text-tertiary">Fast & Deterministic (Rule-based):</p>
          <div className="flex flex-wrap gap-2">
            {RULE_BASED_QUESTIONS.map(({ text, badge }) => (
              <Button
                key={text}
                variant="ghost"
                size="sm"
                onClick={() => handleExampleClick(text)}
                disabled={!canSend}
                className="group relative rounded-full border border-primary/15 bg-primaryAccent px-3 py-1.5 text-xs text-primary hover:bg-primaryAccent/80 hover:scale-105 transition-all"
              >
                <span className="mr-1.5 opacity-60 group-hover:opacity-100">{badge}</span>
                {text}
              </Button>
            ))}
          </div>
        </div>

        {/* LLM questions */}
        <div>
          <p className="mb-2 text-xs text-tertiary">Smart & Flexible (LLM-powered):</p>
          <div className="flex flex-wrap gap-2">
            {LLM_QUESTIONS.map(({ text, badge }) => (
              <Button
                key={text}
                variant="ghost"
                size="sm"
                onClick={() => handleExampleClick(text)}
                disabled={!canSend}
                className="group relative rounded-full border border-primary/15 bg-primaryAccent px-3 py-1.5 text-xs text-primary hover:bg-primaryAccent/80 hover:scale-105 transition-all"
              >
                <span className="mr-1.5 opacity-60 group-hover:opacity-100">{badge}</span>
                {text}
              </Button>
            ))}
          </div>
        </div>

        {/* Usage notice */}
        <div className="mt-4 rounded-lg bg-yellow-50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-800/30 px-3 py-2">
          <p className="text-xs text-yellow-800 dark:text-yellow-200">
            ⚠️ <strong>사용 제한:</strong> 죄송합니다. 사용 비용 때문에 1인당 5회로 제한됩니다.
          </p>
        </div>
      </div>
    </div>
  )
}

export default RecommendedQuestions
