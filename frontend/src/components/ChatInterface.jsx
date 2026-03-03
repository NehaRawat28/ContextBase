import { useState, useRef, useEffect } from "react";
import { useApi } from "../hooks/useApi";
import { UserIcon, BotIcon, ChatIcon, SendIcon, WarningIcon, ClearIcon } from "./Icons";

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  
  const { loading, error, queryKnowledgeBase, clearError } = useApi();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (error) {
      const errorMessage = {
        id: Date.now(),
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error}. Please check if the server is running and try again.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      clearError();
    }
  }, [error, clearError]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: question.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setQuestion("");

    try {
      const data = await queryKnowledgeBase(userMessage.content);
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.answer || "I couldn't generate a response. Please try again.",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      // Error handling is done in the useEffect above
      console.error('Query failed:', error);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [question]);

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div>
          <h2 className="chat-title">AI Assistant</h2>
          <p className="chat-subtitle">Ask questions about your knowledge base</p>
        </div>
        {messages.length > 0 && (
          <button onClick={clearChat} className="clear-chat-button">
            <ClearIcon size={16} />
            Clear Chat
          </button>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <ChatIcon size={48} />
            </div>
            <h3 className="empty-state-title">Start a conversation</h3>
            <p className="empty-state-subtitle">
              Ask me anything about your knowledge base and I'll help you find the information you need.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message ${message.type} ${message.isError ? 'error' : ''}`}>
              <div className="message-avatar">
                {message.type === 'user' ? (
                  <UserIcon size={20} />
                ) : message.isError ? (
                  <WarningIcon size={20} />
                ) : (
                  <BotIcon size={20} />
                )}
              </div>
              <div className="message-content">
                <div className="message-bubble">
                  {message.content}
                </div>
                <div className="message-time">
                  {formatTime(message.timestamp)}
                </div>
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="message assistant">
            <div className="message-avatar">
              <BotIcon size={20} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span>AI is thinking</span>
                <div className="typing-dots">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-container">
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your question here... (Press Enter to send, Shift+Enter for new line)"
            className="question-input"
            disabled={loading}
            rows={1}
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="send-button"
            aria-label="Send message"
          >
            <SendIcon size={18} />
          </button>
        </div>
      </form>
    </div>
  );
}