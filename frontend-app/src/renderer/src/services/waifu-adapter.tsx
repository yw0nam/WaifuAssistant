/**
 * Adapter for WaifuAssistant WebSocket API
 * Translates between WaifuAssistant backend messages and frontend expected format
 */

export interface WaifuMessage {
  // Incoming messages from WaifuAssistant backend
  type: 'content' | 'audio' | 'llm_complete' | 'error';
  text?: string;
  data?: string; // base64 audio data
  chunk_id?: number;
  node?: string;
  message?: string;
}

export interface WaifuOutgoingMessage {
  // Outgoing messages to WaifuAssistant backend
  type: 'chat' | 'tts_interrupt' | 'ping';
  text?: string;
  enable_tts?: boolean;
  reference_id?: string;
  reason?: string;
  timestamp?: number;
}

export class WaifuAdapter {
  private static instance: WaifuAdapter;

  static getInstance() {
    if (!WaifuAdapter.instance) {
      WaifuAdapter.instance = new WaifuAdapter();
    }
    return WaifuAdapter.instance;
  }

  /**
   * Convert WaifuAssistant message to frontend format
   */
  adaptIncomingMessage(waifuMessage: WaifuMessage): any {
    switch (waifuMessage.type) {
      case 'content':
        return {
          type: 'audio', // Frontend expects 'audio' type for streaming content
          display_text: {
            text: waifuMessage.text || '',
            name: 'Assistant',
            avatar: '/icon.png'
          },
          actions: {
            expressions: [1], // Default expression
          }
        };

      case 'audio':
        return {
          type: 'audio',
          audio: waifuMessage.data,
          display_text: {
            text: waifuMessage.text || '',
            name: 'Assistant',
            avatar: '/icon.png'
          },
          actions: {
            expressions: [1],
          }
        };

      case 'llm_complete':
        // Add the complete message to chat history
        return {
          type: 'message',
          messages: [{
            id: Date.now().toString(),
            content: waifuMessage.text || '',
            role: 'ai' as const,
            timestamp: new Date().toISOString(),
            name: 'Assistant',
            avatar: '/icon.png'
          }]
        };

      case 'error':
        return {
          type: 'error',
          message: waifuMessage.message || 'An error occurred'
        };

      default:
        return waifuMessage;
    }
  }

  /**
   * Convert frontend message to WaifuAssistant format
   */
  adaptOutgoingMessage(frontendMessage: any, options?: { referenceId?: string }): WaifuOutgoingMessage {
    switch (frontendMessage.type) {
      case 'send-message':
      case 'text-input':
        return {
          type: 'chat',
          text: frontendMessage.text || '',
          enable_tts: true,
          reference_id: options?.referenceId
        };

      case 'interrupt':
        return {
          type: 'tts_interrupt',
          reason: 'User interrupted'
        };

      case 'ping':
        return {
          type: 'ping',
          timestamp: Date.now()
        };

      default:
        // For unknown message types, return a safe default
        return {
          type: 'ping',
          timestamp: Date.now()
        };
    }
  }

  /**
   * Initialize connection - send any required setup messages
   */
  getInitializationMessages(): WaifuOutgoingMessage[] {
    return [
      {
        type: 'ping',
        timestamp: Date.now()
      }
    ];
  }

  /**
   * Mock responses for frontend features that don't exist in WaifuAssistant yet
   */
  getMockResponses() {
    return {
      backgrounds: {
        type: 'backgrounds',
        files: []
      },
      configs: {
        type: 'configs',
        configs: []
      },
      historyList: {
        type: 'history-list',
        histories: []
      },
      newHistory: {
        type: 'new-history',
        history_uid: 'default-session'
      }
    };
  }
}
