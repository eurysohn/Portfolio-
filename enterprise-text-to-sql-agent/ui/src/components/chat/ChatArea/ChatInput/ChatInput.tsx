'use client'
import { useState } from 'react'
import { toast } from 'sonner'
import { TextArea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useQueryState } from 'nuqs'
import Icon from '@/components/ui/icon'

const ChatInput = () => {
  const { chatInputRef } = useStore()

  const { handleStreamResponse } = useAIChatStreamHandler()
  const [selectedAgent] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [inputMessage, setInputMessage] = useState('')
  const isStreaming = useStore((state) => state.isStreaming)
  const generatorMode = useStore((state) => state.generatorMode)
  const setGeneratorMode = useStore((state) => state.setGeneratorMode)
  
  const handleSubmit = async () => {
    if (!inputMessage.trim()) return

    const currentMessage = inputMessage
    setInputMessage('')

    try:
      await handleStreamResponse(currentMessage)
    } catch (error) {
      toast.error(
        `Error in handleSubmit: ${
          error instanceof Error ? error.message : String(error)
        }`
      )
    }
  }

  return (
    <div className="relative mx-auto mb-1 flex w-full max-w-2xl flex-col items-center justify-center gap-y-2 font-geist">
      {/* Mode Selector */}
      <div className="flex w-full items-center justify-center gap-x-2 text-xs">
        <span className="text-tertiary">Mode:</span>
        <div className="flex gap-x-1 rounded-lg bg-primaryAccent p-0.5">
          <button
            onClick={() => setGeneratorMode('rule_based')}
            className={`rounded px-3 py-1 transition-colors ${
              generatorMode === 'rule_based'
                ? 'bg-primary text-primaryAccent'
                : 'text-secondary hover:text-primary'
            }`}
          >
            Rules
          </button>
          <button
            onClick={() => setGeneratorMode('hybrid')}
            className={`rounded px-3 py-1 transition-colors ${
              generatorMode === 'hybrid'
                ? 'bg-primary text-primaryAccent'
                : 'text-secondary hover:text-primary'
            }`}
          >
            Hybrid
          </button>
          <button
            onClick={() => setGeneratorMode('llm')}
            className={`rounded px-3 py-1 transition-colors ${
              generatorMode === 'llm'
                ? 'bg-primary text-primaryAccent'
                : 'text-secondary hover:text-primary'
            }`}
          >
            LLM
          </button>
        </div>
        <span className="text-xs text-tertiary">
          {generatorMode === 'rule_based' && '⚡ Fast & deterministic'}
          {generatorMode === 'hybrid' && '🎯 Smart fallback'}
          {generatorMode === 'llm' && '🤖 Full AI power'}
        </span>
      </div>
      
      {/* Input Area */}
      <div className="flex w-full items-end gap-x-2">
        <TextArea
          placeholder={'Ask anything'}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => {
            if (
              e.key === 'Enter' &&
              !e.nativeEvent.isComposing &&
              !e.shiftKey &&
              !isStreaming
            ) {
              e.preventDefault()
              handleSubmit()
            }
          }}
          className="w-full border border-accent bg-primaryAccent px-4 text-sm text-primary focus:border-accent"
          disabled={!(selectedAgent || teamId)}
          ref={chatInputRef}
        />
        <Button
          onClick={handleSubmit}
          disabled={
            !(selectedAgent || teamId) || !inputMessage.trim() || isStreaming
          }
          size="icon"
          className="rounded-xl bg-primary p-5 text-primaryAccent"
        >
          <Icon type="send" color="primaryAccent" />
        </Button>
      </div>
    </div>
  )
}

export default ChatInput
