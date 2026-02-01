'use client'

import { motion } from 'framer-motion'
import React from 'react'
import { Button } from '@/components/ui/button'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useStore } from '@/store'
import { useQueryState } from 'nuqs'

const RULE_BASED_QUESTIONS = [
  { text: 'Order fill rate last 30 days', badge: '⚡ Rules' },
  { text: 'On time delivery rate this month', badge: '⚡ Rules' },
  { text: 'Late ship rate last 7 days', badge: '⚡ Rules' }
]

const HYBRID_QUESTIONS = [
  { text: 'Total revenue last month', badge: '🔄 Hybrid' },
  { text: 'Orders count last 7 days', badge: '🔄 Hybrid' },
  { text: 'Order fill rate yesterday', badge: '🔄 Hybrid' }
]

const LLM_QUESTIONS = [
  { text: 'Total revenue for shipped orders last 30 days', badge: '🤖 LLM' },
  { text: 'How many products do we have in stock right now?', badge: '🤖 LLM' },
  { text: 'Average order value this month', badge: '🤖 LLM' }
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
          transition={{ duration: 0.5, delay: 0.28 }}
          className="rounded-xl border border-primary/10 bg-accent/50 p-6"
        >
          <h2 className="text-lg font-semibold text-primary mb-4">
            🎛️ Three Generation Modes
          </h2>
          <div className="grid gap-4 text-left">
            <div className="rounded-lg border border-primary/10 bg-background/50 p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">⚡</span>
                <h3 className="font-semibold text-primary">Rules Mode</h3>
              </div>
              <p className="text-sm text-secondary leading-relaxed">
                Lightning-fast deterministic SQL generation using template matching. 
                Perfect for common KPIs like &quot;order fill rate&quot; or &quot;on time delivery rate&quot;. 
                ~5ms response time with 95%+ accuracy for standard queries.
              </p>
            </div>
            
            <div className="rounded-lg border border-primary/10 bg-background/50 p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">🔄</span>
                <h3 className="font-semibold text-primary">Hybrid Mode (Recommended)</h3>
              </div>
              <p className="text-sm text-secondary leading-relaxed">
                Best of both worlds. Tries rule-based generation first for speed, 
                then falls back to LLM for complex queries. Optimal balance of 
                performance and flexibility for production use.
              </p>
            </div>
            
            <div className="rounded-lg border border-primary/10 bg-background/50 p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">🤖</span>
                <h3 className="font-semibold text-primary">LLM Mode</h3>
              </div>
              <p className="text-sm text-secondary leading-relaxed">
                AI-powered SQL generation using GPT-4o-mini for complex, 
                ad-hoc queries. Handles natural language questions that don&apos;t 
                match templates. Higher latency (~1-2s) but maximum flexibility.
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.42 }}
          className="text-left"
        >
          <p className="mb-4 text-sm font-medium text-secondary">
            💡 Try these example questions:
          </p>
          
          {/* Rule-based questions */}
          <div className="mb-4">
            <p className="mb-2 text-xs text-tertiary font-medium">⚡ Rules - Fast & Deterministic:</p>
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

          {/* Hybrid questions */}
          <div className="mb-4">
            <p className="mb-2 text-xs text-tertiary font-medium">🔄 Hybrid - Balanced:</p>
            <div className="flex flex-wrap gap-2">
              {HYBRID_QUESTIONS.map(({ text, badge }) => (
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
          <div className="mb-4">
            <p className="mb-2 text-xs text-tertiary font-medium">🤖 LLM - Smart & Flexible:</p>
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
          <div className="rounded-lg bg-yellow-50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-800/30 px-3 py-2">
            <p className="text-xs text-yellow-800 dark:text-yellow-200">
              ⚠️ <strong>사용 제한:</strong> 죄송합니다. 사용 비용 때문에 1인당 5회로 제한됩니다.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default ChatBlankState
