import React, { useState, useRef, useEffect } from 'react';
import {
  invokeAgentStream,
  getOrCreateSessionId,
  resetAgentSession,
} from '../services/agent';
import type { ChatMessage } from '../types';

export const AgentChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello! I am your AI HR Assistant hosted on Amazon Bedrock AgentCore. I can search records, query employees by hire date, book leave requests, or draft and send emails to HR. How can I help you today?',
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [inputPrompt, setInputPrompt] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState(getOrCreateSessionId());

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming, activeTool]);

  const handleSend = async (promptToSend?: string) => {
    const prompt = (promptToSend || inputPrompt).trim();
    if (!prompt || isStreaming) return;

    setInputPrompt('');

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: prompt,
      timestamp: new Date().toLocaleTimeString(),
    };

    const assistantMessageId = `asst-${Date.now()}`;
    const initialAssistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      toolCalls: [],
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage, initialAssistantMessage]);
    setIsStreaming(true);
    setActiveTool(null);

    try {
      await invokeAgentStream(
        prompt,
        {
          onToken: (token) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: msg.content + token }
                  : msg
              )
            );
          },
          onToolCall: (toolName) => {
            setActiveTool(toolName);
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                      ...msg,
                      toolCalls: [...(msg.toolCalls || []), toolName],
                    }
                  : msg
              )
            );
          },
          onError: (err) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                      ...msg,
                      content:
                        msg.content +
                        `\n\n⚠️ Error during processing: ${err.message}`,
                    }
                  : msg
              )
            );
          },
          onDone: () => {
            setActiveTool(null);
          },
        },
        sessionId
      );
    } catch (err: any) {
      // Handled in onError callback
    } finally {
      setIsStreaming(false);
      setActiveTool(null);
    }
  };

  const handleResetSession = () => {
    const newId = resetAgentSession();
    setSessionId(newId);
    setMessages([
      {
        id: `reset-${Date.now()}`,
        role: 'system',
        content: `Session history reset. New session: ${newId.substring(0, 18)}...`,
        timestamp: new Date().toLocaleTimeString(),
      },
      {
        id: `welcome-${Date.now()}`,
        role: 'assistant',
        content: 'Conversation cleared! What would you like to explore next?',
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
  };

  const samplePrompts = [
    'Which employees were hired in 2024?',
    'Who works in Engineering?',
    'Draft a leave email for Ada Lovelace from 2026-05-04 to 2026-05-08 and send it to HR.',
  ];

  return (
    <div className="page-content chat-page-layout">
      <div className="chat-header-bar">
        <div>
          <h2 className="page-heading">AgentCore AI Assistant</h2>
          <p className="page-subheading">
            Live conversational runtime with autonomous tool execution over DynamoDB and SNS.
          </p>
        </div>
        <div className="session-status">
          <span className="session-pill">Session: {sessionId.substring(0, 22)}...</span>
          <button
            type="button"
            className="btn-text btn-sm"
            onClick={handleResetSession}
            disabled={isStreaming}
          >
            🔄 New Session
          </button>
        </div>
      </div>

      <div className="chat-card">
        {/* Suggestion Prompts */}
        <div className="suggestions-bar">
          <span className="suggestion-label">Try asking:</span>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="suggestion-pill"
              onClick={() => handleSend(p)}
              disabled={isStreaming}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Message Thread */}
        <div className="chat-thread">
          {messages.map((m) => {
            if (m.role === 'system') {
              return (
                <div key={m.id} className="system-bubble">
                  {m.content}
                </div>
              );
            }

            const isUser = m.role === 'user';
            return (
              <div
                key={m.id}
                className={`message-row ${isUser ? 'user-row' : 'assistant-row'}`}
              >
                <div className={`message-avatar ${isUser ? 'user-av' : 'asst-av'}`}>
                  {isUser ? '👤' : '✨'}
                </div>
                <div className="message-wrapper">
                  <div className={`message-bubble ${isUser ? 'user-bubble' : 'asst-bubble'}`}>
                    {/* Render tool pills if any were called */}
                    {m.toolCalls && m.toolCalls.length > 0 && (
                      <div className="tool-chips">
                        {m.toolCalls.map((t, idx) => (
                          <span key={idx} className="tool-chip">
                            ⚙️ tool: <code>{t}</code>
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="message-text">
                      {m.content || (isStreaming && !isUser ? 'Thinking...' : '')}
                    </div>
                  </div>
                  <span className="message-time">{m.timestamp}</span>
                </div>
              </div>
            );
          })}

          {/* Active tool indicator */}
          {activeTool && (
            <div className="active-tool-banner">
              <span className="pulse-dot"></span>
              Executing tool: <code>{activeTool}</code> against DynamoDB...
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="chat-input-bar"
        >
          <input
            type="text"
            className="input-field chat-input"
            placeholder="Ask about employees, hire dates, or request leave..."
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            disabled={isStreaming}
          />
          <button
            type="submit"
            className="btn-primary send-btn"
            disabled={isStreaming || !inputPrompt.trim()}
          >
            {isStreaming ? 'Thinking...' : 'Send →'}
          </button>
        </form>
      </div>
    </div>
  );
};

