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
  'Backlog units',
  'Total revenue last month',
  'Orders count last 7 days',
  'Inventory units',
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
          className="rounded-2xl border border-primary/15 bg-accent/60 p-6 text-left shadow-sm"
        >
          <h1 className="text-2xl font-semibold tracking-tight text-primary">
            Hello! This is a quick demo of the enterprise-text-to-sql agent.
          </h1>
          <p className="mt-3 text-sm text-secondary">
            Ask KPI questions and see how the agent performs scope checks,
            schema grounding, SQL generation, validation, and execution safely.
          </p>
          <p className="mt-2 text-sm text-secondary">
            Tip: use the suggested questions below to explore common KPIs.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.35 }}
          className="flex flex-wrap justify-center gap-2"
        >
          {EXAMPLE_QUESTIONS.map((question) => (
            <Button
              key={question}
              variant="ghost"
              size="sm"
              onClick={() => handleExampleClick(question)}
              disabled={!canSend}
              className="rounded-full border border-primary/15 bg-primaryAccent px-4 text-xs text-primary hover:bg-primaryAccent/80"
            >
              {question}
            </Button>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

export default ChatBlankState
