import { 
  WebSocketRequest, 
  WebSocketResponse, 
  MessageType, 
  ConnectionState 
} from '../types/websocket';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private clientId: string;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers: ((message: WebSocketResponse) => void)[] = [];
  private connectionStateHandlers: ((state: ConnectionState) => void)[] = [];

  constructor(url: string = 'ws://localhost:8800') {
    this.url = url;
    this.clientId = this.generateClientId();
  }

  private generateClientId(): string {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  public connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${this.url}/ws/${this.clientId}`);
        
        this.ws.onopen = () => {
          console.log(`🔗 Connected to WebSocket server as ${this.clientId}`);
          this.reconnectAttempts = 0;
          this.notifyConnectionState(ConnectionState.CONNECTED);
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketResponse = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log(`🔌 WebSocket connection closed:`, event);
          this.notifyConnectionState(ConnectionState.DISCONNECTED);
          
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.notifyConnectionState(ConnectionState.ERROR);
          reject(error);
        };

        this.notifyConnectionState(ConnectionState.CONNECTING);
      } catch (error) {
        this.notifyConnectionState(ConnectionState.ERROR);
        reject(error);
      }
    });
  }

  private attemptReconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms...`);
    
    setTimeout(() => {
      this.connect().catch(console.error);
    }, delay);
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public sendMessage(message: WebSocketRequest): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('⚠️ WebSocket is not connected');
    }
  }

  public sendChatMessage(text: string, enableTts: boolean = true): void {
    this.sendMessage({
      type: MessageType.CHAT,
      text,
      enable_tts: enableTts
    });
  }

  public sendPing(): void {
    this.sendMessage({
      type: MessageType.PING,
      timestamp: Date.now()
    });
  }

  private handleMessage(message: WebSocketResponse): void {
    this.messageHandlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('❌ Error in message handler:', error);
      }
    });
  }

  private notifyConnectionState(state: ConnectionState): void {
    this.connectionStateHandlers.forEach(handler => {
      try {
        handler(state);
      } catch (error) {
        console.error('❌ Error in connection state handler:', error);
      }
    });
  }

  public onMessage(handler: (message: WebSocketResponse) => void): () => void {
    this.messageHandlers.push(handler);
    
    // Return unsubscribe function
    return () => {
      const index = this.messageHandlers.indexOf(handler);
      if (index > -1) {
        this.messageHandlers.splice(index, 1);
      }
    };
  }

  public onConnectionStateChange(handler: (state: ConnectionState) => void): () => void {
    this.connectionStateHandlers.push(handler);
    
    // Return unsubscribe function
    return () => {
      const index = this.connectionStateHandlers.indexOf(handler);
      if (index > -1) {
        this.connectionStateHandlers.splice(index, 1);
      }
    };
  }

  public getConnectionState(): ConnectionState {
    if (!this.ws) return ConnectionState.DISCONNECTED;
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return ConnectionState.CONNECTING;
      case WebSocket.OPEN:
        return ConnectionState.CONNECTED;
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return ConnectionState.DISCONNECTED;
      default:
        return ConnectionState.ERROR;
    }
  }

  public getClientId(): string {
    return this.clientId;
  }
}
