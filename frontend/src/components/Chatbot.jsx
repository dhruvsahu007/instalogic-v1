import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './Chatbot.css'

function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [quickReplies, setQuickReplies] = useState([])
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Send initial greeting
      setMessages([
        {
          type: 'bot',
          content: "👋 Hello! I'm the InstaLogic AI assistant. How can I help you today?",
          timestamp: new Date().toISOString()
        }
      ])
      setQuickReplies([
        "View Our Services",
        "Request a Demo",
        "See Case Studies",
        "Contact Sales"
      ])
    }
  }, [isOpen])

  const sendMessage = async (messageText = null) => {
    const textToSend = messageText || inputMessage.trim()
    
    if (!textToSend) return

    // Add user message to chat
    const userMessage = {
      type: 'user',
      content: textToSend,
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsTyping(true)
    setQuickReplies([])

    try {
      const response = await axios.post('/api/chat', {
        message: textToSend,
        session_id: sessionId
      })

      // Add bot response
      const botMessage = {
        type: 'bot',
        content: response.data.response,
        sources: response.data.sources,
        timestamp: response.data.timestamp
      }

      setMessages(prev => [...prev, botMessage])
      setSessionId(response.data.session_id)
      
      if (response.data.quick_replies) {
        setQuickReplies(response.data.quick_replies)
      }

    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        type: 'bot',
        content: "I apologize, but I'm having trouble connecting right now. Please try again or contact us directly.",
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleQuickReply = (reply) => {
    sendMessage(reply)
  }

  const clearChat = () => {
    setMessages([
      {
        type: 'bot',
        content: "Chat cleared. How can I help you?",
        timestamp: new Date().toISOString()
      }
    ])
    setQuickReplies([
      "View Our Services",
      "Request a Demo",
      "See Case Studies",
      "Contact Sales"
    ])
  }

  return (
    <>
      {/* Chat Button */}
      <div 
        className={`chat-button ${isOpen ? 'hidden' : ''}`}
        onClick={() => setIsOpen(true)}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span className="chat-badge">AI</span>
      </div>

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-info">
              <h3>InstaLogic AI Assistant</h3>
              <span className="chat-status">
                <span className="status-dot"></span>
                Online
              </span>
            </div>
            <div className="chat-header-actions">
              <button onClick={clearChat} className="icon-button" title="Clear chat">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="1 4 1 10 7 10"></polyline>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
                </svg>
              </button>
              <button onClick={() => setIsOpen(false)} className="icon-button" title="Close">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                <div className="message-content">
                  {message.content}
                </div>
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <strong>📚 Sources:</strong>
                    {message.sources.map((source, idx) => (
                      <a 
                        key={idx} 
                        href={source} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="source-link"
                      >
                        {source}
                      </a>
                    ))}
                  </div>
                )}
                <div className="message-time">
                  {new Date(message.timestamp).toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message bot">
                <div className="message-content typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Replies */}
          {quickReplies.length > 0 && (
            <div className="quick-replies">
              {quickReplies.map((reply, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickReply(reply)}
                  className="quick-reply-button"
                >
                  {reply}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="chat-input-container">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              rows="1"
              className="chat-input"
            />
            <button 
              onClick={() => sendMessage()}
              className="send-button"
              disabled={!inputMessage.trim()}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default Chatbot
