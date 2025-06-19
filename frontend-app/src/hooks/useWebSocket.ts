import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketService } from '../services/websocket';
import { 
  WebSocketResponse, 
  ConnectionState 
} from '../types/websocket';

export const useWebSocket = (url?: string) => {
  const [connectionState, setConnectionState] = useState<ConnectionState>(ConnectionState.DISCONNECTED);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocketService | null>(null);
  const messageHandlersRef = useRef<((message: WebSocketResponse) => void)[]>([]);

  const connect = useCallback(async () => {
    if (wsRef.current) {
      wsRef.current.disconnect();
    }

    try {
      setError(null);
      const ws = new WebSocketService(url);
      wsRef.current = ws;

      // Set up connection state handler
      ws.onConnectionStateChange(setConnectionState);

      // Set up message routing
      ws.onMessage((message) => {
        messageHandlersRef.current.forEach(handler => {
          try {
            handler(message);
          } catch (err) {
            console.error('Error in message handler:', err);
          }
        });
      });

      await ws.connect();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
      setConnectionState(ConnectionState.ERROR);
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
    }
    setConnectionState(ConnectionState.DISCONNECTED);
  }, []);

  const sendMessage = useCallback((text: string, enableTts: boolean = true, referenceId?: string, skipInternalReasoning: boolean = true, reasoningStartTag?: string, reasoningEndTag?: string) => {
    if (wsRef.current && connectionState === ConnectionState.CONNECTED) {
      wsRef.current.sendChatMessage(text, enableTts, referenceId, skipInternalReasoning, reasoningStartTag, reasoningEndTag);
    } else {
      console.warn('WebSocket not connected');
    }
  }, [connectionState]);

  const sendPing = useCallback(() => {
    if (wsRef.current && connectionState === ConnectionState.CONNECTED) {
      wsRef.current.sendPing();
    }
  }, [connectionState]);

  const interruptTTS = useCallback((reason?: string) => {
    if (wsRef.current && connectionState === ConnectionState.CONNECTED) {
      wsRef.current.interruptTTS(reason);
    } else {
      console.warn('WebSocket not connected');
    }
  }, [connectionState]);

  const onMessage = useCallback((handler: (message: WebSocketResponse) => void) => {
    messageHandlersRef.current.push(handler);
    
    // Return cleanup function
    return () => {
      const index = messageHandlersRef.current.indexOf(handler);
      if (index > -1) {
        messageHandlersRef.current.splice(index, 1);
      }
    };
  }, []);

  const getClientId = useCallback((): string | null => {
    return wsRef.current?.getClientId() || null;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connectionState,
    error,
    connect,
    disconnect,
    sendMessage,
    sendPing,
    interruptTTS,
    onMessage,
    getClientId,
    isConnected: connectionState === ConnectionState.CONNECTED
  };
};
