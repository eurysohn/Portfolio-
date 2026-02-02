import { useState, useRef, useEffect } from 'react'
import { Settings, Wrench, Zap, Send, Shield, ChevronDown, CheckCircle2, Loader2 } from 'lucide-react'
import './App.css'

interface Message {
    role: 'user' | 'agent';
    content: string;
    steps?: { title: string; status: 'done' | 'running' | 'waiting' }[];
    sources?: string[];
    confidence?: number;
}

function App() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'agent',
            content: 'Hello! I am your SCM Intelligence Agent. How can I help you today?',
        }
    ]);
    const [input, setInput] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        const agentMsg: Message = {
            role: 'agent',
            content: '',
            steps: [
                { title: 'Detecting Intent', status: 'running' },
                { title: 'Searching Knowledge Base', status: 'waiting' },
                { title: 'Generating Response', status: 'waiting' }
            ]
        };
        setMessages(prev => [...prev, agentMsg]);

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: input, api_key: apiKey }),
            });
            if (!response.ok) {
                throw new Error('Request failed');
            }

            const data = await response.json();
            const answer = typeof data?.answer === 'string' ? data.answer : '응답을 이해할 수 없어요.';
            const domain = typeof data?.domain === 'string' ? data.domain : 'UNKNOWN';
            const confidence =
                typeof data?.confidence === 'number' ? data.confidence : undefined;
            const sources = Array.isArray(data?.sources) ? data.sources : [];

            setMessages(prev => {
                const newMsgs = [...prev];
                const lastIdx = newMsgs.length - 1;
                const lastMsg = newMsgs[lastIdx];
                // Avoid mutating state directly to prevent render inconsistencies.
                newMsgs[lastIdx] = {
                    ...lastMsg,
                    content: answer,
                    steps: [
                        { title: 'Intent Detected: ' + domain, status: 'done' },
                        { title: 'Information Retrieved', status: 'done' },
                        { title: 'Response Finalized', status: 'done' }
                    ],
                    confidence,
                    sources: sources
                        .map((s: any) => s?.source)
                        .filter((source: unknown): source is string => typeof source === 'string')
                };
                return newMsgs;
            });
        } catch (error) {
            setMessages(prev => {
                const newMsgs = [...prev];
                // TODO: Surface backend error details in a safe user-friendly banner.
                newMsgs[newMsgs.length - 1].content = 'Error connecting to the agent. Please check your backend.';
                return newMsgs;
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="app-container">
            <aside className="sidebar">
                <div className="sidebar-title">
                    <Zap size={24} fill="currentColor" />
                    <span>SCM Agent AI</span>
                </div>

                <div className="config-section">
                    <label className="section-label">Configuration</label>
                    <div className="config-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Framework</span>
                            <Settings size={14} />
                        </div>
                        <div className="dropdown-mock">AgentOrch v2</div>
                    </div>
                    <div className="config-card">
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-sub)', marginBottom: '4px' }}>Model</div>
                        <div className="dropdown-mock">GPT-4o SCM-Tuned</div>
                    </div>
                </div>

                <div className="config-section">
                    <label className="section-label">Credentials</label>
                    <div className="config-card">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                            <Shield size={14} />
                            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>OpenAI API Key</span>
                        </div>
                        <input
                            type="password"
                            className="key-input"
                            placeholder="sk-..."
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                        />
                    </div>
                </div>

                <div className="config-section" style={{ marginTop: 'auto' }}>
                    <label className="section-label">Tools Active</label>
                    <div className="tool-toggle"><div className="toggle-dot checked"></div> RAG Search</div>
                    <div className="tool-toggle"><div className="toggle-dot checked"></div> SCM Calc</div>
                    <div className="tool-toggle"><div className="toggle-dot"></div> Web Fallback</div>
                </div>
            </aside>

            <main className="main-content">
                <div className="chat-container">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message-row ${msg.role}`}>
                            <div className="avatar">
                                {msg.role === 'user' ? <div className="user-icon" /> : <Zap size={18} />}
                            </div>
                            <div className="message-bubble">
                                {msg.role === 'agent' && msg.steps && (
                                    <div className="steps-container">
                                        <div className="steps-header">
                                            <span>Agent execution steps</span>
                                            <ChevronDown size={14} />
                                        </div>
                                        {msg.steps.map((step, sIdx) => (
                                            <div key={sIdx} className="step-item">
                                                {step.status === 'done' ? <CheckCircle2 size={14} color="var(--step-done)" /> :
                                                    step.status === 'running' ? <Loader2 size={14} className="spin" color="var(--step-running)" /> :
                                                        <div className="step-dot" />}
                                                <span className={`step-title ${step.status}`}>{step.title}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                <div className="message-text">{msg.content}</div>
                                {msg.confidence && (
                                    <div className="message-meta">
                                        Confidence: {(msg.confidence * 100).toFixed(1)}% | Sources: {msg.sources?.length || 0}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    <div ref={chatEndRef} />
                </div>

                <div className="input-area">
                    <div className="input-wrapper">
                        <input
                            type="text"
                            className="chat-input"
                            placeholder="Ask about OTIF, EOQ, or demand forecasting..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            disabled={isLoading}
                        />
                        <button className="send-button" onClick={handleSend} disabled={isLoading}>
                            <Send size={18} />
                        </button>
                    </div>
                </div>
            </main>
        </div>
    )
}

export default App
