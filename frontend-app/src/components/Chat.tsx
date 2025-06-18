import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAudio } from '../hooks/useAudio';
import { ChatMessage } from '../types/chat';
import { ResponseType, AudioResponse, ContentResponse, LLMCompleteResponse, ErrorResponse } from '../types/websocket';
import './Chat.css';

interface ChatProps {
  websocketUrl?: string;
}

const Chat: React.FC<ChatProps> = ({ websocketUrl }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<ChatMessage | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    connectionState, 
    error, 
    connect, 
    disconnect, 
    sendMessage, 
    onMessage, 
    isConnected 
  } = useWebSocket(websocketUrl);
  
  const { 
    isPlaying, 
    currentText, 
    playAudio, 
    stopAudio, 
    clearQueue 
  } = useAudio();

  // Auto-connect on mount
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  // Set up WebSocket message handlers
  useEffect(() => {
    const handleContentMessage = (message: ContentResponse) => {
      setIsLoading(true);
      
      if (!currentStreamingMessage) {
        // Create new streaming message
        const newMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          sender: 'assistant',
          content: message.text,
          timestamp: new Date(),
          isComplete: false
        };
        setCurrentStreamingMessage(newMessage);
      } else {
        // Update existing streaming message
        setCurrentStreamingMessage(prev => prev ? {
          ...prev,
          content: prev.content + message.text
        } : null);
      }
    };

    const handleAudioMessage = (message: AudioResponse) => {
      console.log('🎵 Playing audio for:', message.text);
      playAudio(message.data, message.format, message.text);
      
      // Update current streaming message with audio data
      if (currentStreamingMessage) {
        setCurrentStreamingMessage(prev => prev ? {
          ...prev,
          audioData: message.data
        } : null);
      }
    };

    const handleLLMCompleteMessage = (message: LLMCompleteResponse) => {
      console.log('✅ Message complete:', message);
      setIsLoading(false);
      
      if (currentStreamingMessage) {
        // Finalize the message
        const finalMessage: ChatMessage = {
          ...currentStreamingMessage,
          content: message.text,
          isComplete: true
        };
        
        setMessages(prev => [...prev, finalMessage]);
        setCurrentStreamingMessage(null);
      }
    };

    const handleErrorMessage = (message: ErrorResponse) => {
      console.error('❌ Error:', message);
      setIsLoading(false);
      setCurrentStreamingMessage(null);
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'assistant',
        content: `❌ Error: ${message.message}`,
        timestamp: new Date(),
        isComplete: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    };

    const unsubscribe = onMessage((message) => {
      switch (message.type) {
        case ResponseType.CONTENT:
          handleContentMessage(message as ContentResponse);
          break;
        case ResponseType.AUDIO:
          handleAudioMessage(message as AudioResponse);
          break;
        case ResponseType.LLM_COMPLETE:
          handleLLMCompleteMessage(message as LLMCompleteResponse);
          break;
        case ResponseType.ERROR:
          handleErrorMessage(message as ErrorResponse);
          break;
        default:
          console.log('Unhandled message type:', message);
      }
    });

    return unsubscribe;
  }, [onMessage, currentStreamingMessage, playAudio]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamingMessage]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputText.trim() || !isConnected) return;
    
    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: inputText.trim(),
      timestamp: new Date(),
      isComplete: true
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Send message
    sendMessage(inputText.trim());
    setInputText('');
  };

  const handleStopAudio = () => {
    stopAudio();
    clearQueue();
  };

  const getConnectionStatusColor = () => {
    switch (connectionState) {
      case 'connected': return '#4CAF50';
      case 'connecting': return '#FF9800';
      case 'error': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>🤖 Waifu Assistant</h2>
        <div className="connection-status">
          <div 
            className="status-indicator" 
            style={{ backgroundColor: getConnectionStatusColor() }}
          />
          <span className="status-text">{connectionState}</span>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          ❌ {error}
          <button onClick={() => connect()}>Retry</button>
        </div>
      )}

      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-meta">
                <span className="message-time">{formatTime(message.timestamp)}</span>
                {message.audioData && (
                  <button
                    className="play-audio-btn"
                    onClick={() => playAudio(message.audioData!, 'wav', message.content)}
                    title="Play audio"
                  >
                    🔊
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {currentStreamingMessage && (
          <div className="message assistant streaming">
            <div className="message-content">
              <div className="message-text">
                {currentStreamingMessage.content}
                <span className="cursor">|</span>
              </div>
              <div className="message-meta">
                <span className="message-time">{formatTime(currentStreamingMessage.timestamp)}</span>
              </div>
            </div>
          </div>
        )}
        
        {isLoading && !currentStreamingMessage && (
          <div className="message assistant loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {isPlaying && (
        <div className="audio-status">
          <div className="audio-info">
            🎵 Playing: {currentText}
          </div>
          <button className="stop-audio-btn" onClick={handleStopAudio}>
            ⏹ Stop
          </button>
        </div>
      )}

      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={isConnected ? "Type your message..." : "Connecting..."}
          disabled={!isConnected || isLoading}
          className="message-input"
        />
        <button 
          type="submit" 
          disabled={!isConnected || !inputText.trim() || isLoading}
          className="send-button"
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  );
};

export default Chat;
