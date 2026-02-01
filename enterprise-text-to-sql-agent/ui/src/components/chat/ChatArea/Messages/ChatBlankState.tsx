'use client'

import { motion } from 'framer-motion'
import React from 'react'
import { Button } from '@/components/ui/button'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useStore } from '@/store'
import { useQueryState } from 'nuqs'

const EXAMPLE_QUESTIONS = [
  'Order fill rate last 30 days',
  'Late ship rate last 7 days',
  'On time delivery rate this month',
  'Total revenue last month',
  'Orders count last 7 days',
  'Order fill rate yesterday',
  'Late ship rate last month',
  'On time delivery rate last 30 days'
]

const ChatBlankState = () => {
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
    <section className="flex flex-col items-center text-center font-geist">
      <div className="flex w-full max-w-3xl flex-col gap-y-6">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="rounded-2xl border border-primary/15 bg-gradient-to-br from-accent/80 to-accent/40 p-8 text-left shadow-lg"
        >
          <h1 className="text-3xl font-bold tracking-tight text-primary mb-4">
            👋 Welcome to Enterprise Text-to-SQL
          </h1>
          <p className="mt-3 text-base text-primary/90 leading-relaxed">
            This agent demonstrates safe, enterprise-grade SQL generation with strict validation and security controls.
          </p>
          <p className="mt-2 text-base text-primary/90 leading-relaxed">
            Ask KPI questions and watch the agent perform scope checks, schema grounding, SQL generation, validation, and execution—all with full transparency.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <div className="flex items-center gap-2 text-sm text-primary/80">
              <span className="text-lg">✅</span>
              <span>90%+ accuracy</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-primary/80">
              <span className="text-lg">🛡️</span>
              <span>15+ security rules</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-primary/80">
              <span className="text-lg">⚡</span>
              <span>Sub-20ms latency</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.35 }}
          className="text-left"
        >
          <p className="mb-3 text-sm font-medium text-secondary">
            💡 Try these example questions:
          </p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUESTIONS.map((question) => (
              <Button
                key={question}
                variant="ghost"
                size="sm"
                onClick={() => handleExampleClick(question)}
                disabled={!canSend}
                className="rounded-full border border-primary/15 bg-primaryAccent px-4 py-2 text-xs text-primary hover:bg-primaryAccent/80 hover:scale-105 transition-all"
              >
                {question}
              </Button>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default ChatBlankState
