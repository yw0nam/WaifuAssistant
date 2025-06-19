import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAudio } from '../hooks/useAudio';
import { ChatMessage } from '../types/chat';
import { ResponseType, AudioResponse, ContentResponse, LLMCompleteResponse, ErrorResponse, TTSInterruptedResponse, StreamingTTSResponse } from '../types/websocket';
import './Chat.css';

interface ChatProps {
  websocketUrl?: string;
}

const Chat: React.FC<ChatProps> = ({ websocketUrl }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<ChatMessage | null>(null);
  
  // TTS Settings
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [skipInternalReasoning, setSkipInternalReasoning] = useState(true);
  const [referenceId, setReferenceId] = useState('');
  const [reasoningStartTag, setReasoningStartTag] = useState('<think>');
  const [reasoningEndTag, setReasoningEndTag] = useState('</think>');
  const [showSettings, setShowSettings] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    connectionState, 
    error, 
    connect, 
    disconnect, 
    sendMessage, 
    onMessage, 
    isConnected,
    interruptTTS
  } = useWebSocket(websocketUrl);
  
  const { 
    isPlaying, 
    currentText, 
    playAudio, 
    stopAudio, 
    clearQueue 
  } = useAudio();

  // Load TTS settings from localStorage on mount
  useEffect(() => {
    const savedTtsEnabled = localStorage.getItem('tts-enabled');
    const savedSkipReasoning = localStorage.getItem('tts-skip-reasoning');
    const savedReferenceId = localStorage.getItem('tts-reference-id');
    const savedReasoningStartTag = localStorage.getItem('tts-reasoning-start-tag');
    const savedReasoningEndTag = localStorage.getItem('tts-reasoning-end-tag');
    
    if (savedTtsEnabled !== null) {
      setTtsEnabled(JSON.parse(savedTtsEnabled));
    }
    if (savedSkipReasoning !== null) {
      setSkipInternalReasoning(JSON.parse(savedSkipReasoning));
    }
    if (savedReferenceId !== null) {
      setReferenceId(savedReferenceId);
    }
    if (savedReasoningStartTag !== null) {
      setReasoningStartTag(savedReasoningStartTag);
    }
    if (savedReasoningEndTag !== null) {
      setReasoningEndTag(savedReasoningEndTag);
    }
  }, []);

  // Save TTS settings to localStorage when they change
  useEffect(() => {
    localStorage.setItem('tts-enabled', JSON.stringify(ttsEnabled));
  }, [ttsEnabled]);

  useEffect(() => {
    localStorage.setItem('tts-skip-reasoning', JSON.stringify(skipInternalReasoning));
  }, [skipInternalReasoning]);

  useEffect(() => {
    localStorage.setItem('tts-reference-id', referenceId);
  }, [referenceId]);

  useEffect(() => {
    localStorage.setItem('tts-reasoning-start-tag', reasoningStartTag);
  }, [reasoningStartTag]);

  useEffect(() => {
    localStorage.setItem('tts-reasoning-end-tag', reasoningEndTag);
  }, [reasoningEndTag]);

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

    const handleStreamingTTSMessage = (message: StreamingTTSResponse) => {
      console.log(`🎤 Streaming TTS sentence ${message.sentence_id}:`, message.sentence);
      
      // Add visual indicator for streaming TTS (optional)
      if (currentStreamingMessage) {
        setCurrentStreamingMessage(prev => prev ? {
          ...prev,
          // Mark that TTS is processing for this sentence
          ttsProcessing: true,
          lastTTSSentenceId: message.sentence_id
        } : null);
      }
      
      // The actual TTS audio will come via AudioResponse messages
      // This message just indicates a sentence is ready for TTS processing
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

    const handleTTSInterruptedMessage = (message: TTSInterruptedResponse) => {
      console.log('🚫 TTS Interrupted:', message);
      clearQueue(); // Clear audio queue
      
      // Add interrupt notification to chat if desired
      const interruptMessage: ChatMessage = {
        id: `interrupt-${Date.now()}`,
        sender: 'system',
        content: `🚫 ${message.message}${message.interrupted_count ? ` (${message.interrupted_count} items cleared)` : ''}`,
        timestamp: new Date(),
        isComplete: true
      };
      
      setMessages(prev => [...prev, interruptMessage]);
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
        case ResponseType.TTS_INTERRUPTED:
          handleTTSInterruptedMessage(message as TTSInterruptedResponse);
          break;
        case ResponseType.STREAMING_TTS:
          handleStreamingTTSMessage(message as StreamingTTSResponse);
          break;
        default:
          console.log('Unhandled message type:', message);
      }
    });

    return unsubscribe;
  }, [onMessage, currentStreamingMessage, playAudio, clearQueue]);

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
    
    // Send message with TTS settings
    sendMessage(
      inputText.trim(), 
      ttsEnabled, 
      referenceId || undefined, 
      skipInternalReasoning,
      reasoningStartTag,
      reasoningEndTag
    );
    setInputText('');
  };

  const handleStopAudio = () => {
    stopAudio();
    clearQueue();
  };

  const handleInterruptTTS = () => {
    // Stop local audio playback
    stopAudio();
    clearQueue();
    // Send interrupt signal to backend
    interruptTTS('user_interrupt');
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
          <div className="audio-controls">
            <button className="stop-audio-btn" onClick={handleStopAudio}>
              ⏹ Stop Audio
            </button>
            <button className="interrupt-tts-btn" onClick={handleInterruptTTS}>
              🚫 Interrupt TTS
            </button>
          </div>
        </div>
      )}

      {/* TTS Settings Panel */}
      <div className="tts-settings">
        <div 
          className="tts-settings-header"
          onClick={() => setShowSettings(!showSettings)}
        >
          <div className="tts-settings-title">
            🎤 TTS Settings
          </div>
          <button 
            type="button" 
            className="tts-settings-toggle"
            aria-label={showSettings ? "Hide settings" : "Show settings"}
          >
            {showSettings ? '▼' : '▶'}
          </button>
        </div>
        
        {showSettings && (
          <div className="tts-settings-content">
            <div className="tts-setting-item">
              <label>
                <input
                  type="checkbox"
                  checked={ttsEnabled}
                  onChange={(e) => setTtsEnabled(e.target.checked)}
                  className="tts-checkbox"
                />
                Enable TTS
              </label>
              <div className={`tts-status-indicator ${!ttsEnabled ? 'disabled' : ''}`}>
                {ttsEnabled ? '🔊 ON' : '🔇 OFF'}
              </div>
            </div>
            
            <div className={`tts-setting-item ${!ttsEnabled ? 'disabled' : ''}`}>
              <label>
                <input
                  type="checkbox"
                  checked={skipInternalReasoning}
                  onChange={(e) => setSkipInternalReasoning(e.target.checked)}
                  className="tts-checkbox"
                  disabled={!ttsEnabled}
                />
                Skip Internal Reasoning
              </label>
              <div className="tts-status-indicator">
                {skipInternalReasoning ? '🧠 Filtered' : '💭 Included'}
              </div>
            </div>
            
            <div className={`tts-setting-item ${!ttsEnabled ? 'disabled' : ''}`}>
              <label htmlFor="reference-id">
                Voice Reference ID:
              </label>
              <input
                id="reference-id"
                type="text"
                value={referenceId}
                onChange={(e) => setReferenceId(e.target.value)}
                placeholder="Optional voice reference ID"
                className="tts-input"
                disabled={!ttsEnabled}
              />
            </div>
            
            <div className={`tts-setting-item ${!ttsEnabled || !skipInternalReasoning ? 'disabled' : ''}`}>
              <label htmlFor="reasoning-start-tag">
                Reasoning Start Tag:
              </label>
              <input
                id="reasoning-start-tag"
                type="text"
                value={reasoningStartTag}
                onChange={(e) => setReasoningStartTag(e.target.value)}
                placeholder="e.g., <think>"
                className="tts-input"
                disabled={!ttsEnabled || !skipInternalReasoning}
              />
            </div>
            
            <div className={`tts-setting-item ${!ttsEnabled || !skipInternalReasoning ? 'disabled' : ''}`}>
              <label htmlFor="reasoning-end-tag">
                Reasoning End Tag:
              </label>
              <input
                id="reasoning-end-tag"
                type="text"
                value={reasoningEndTag}
                onChange={(e) => setReasoningEndTag(e.target.value)}
                placeholder="e.g., </think>"
                className="tts-input"
                disabled={!ttsEnabled || !skipInternalReasoning}
              />
            </div>
          </div>
        )}
      </div>

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
