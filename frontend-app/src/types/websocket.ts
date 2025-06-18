// WebSocket message types matching backend models

export enum MessageType {
  CHAT = 'chat',
  PING = 'ping'
}

export enum ResponseType {
  CONTENT = 'content',
  AUDIO = 'audio',
  LLM_COMPLETE = 'llm_complete',
  ERROR = 'error',
  PONG = 'pong'
}

// Request types
export interface ChatRequest {
  type: MessageType.CHAT;
  text: string;
  enable_tts?: boolean;
  reference_id?: string;
}

export interface PingRequest {
  type: MessageType.PING;
  timestamp?: number;
}

export type WebSocketRequest = ChatRequest | PingRequest;

// Response types
export interface ContentResponse {
  type: ResponseType.CONTENT;
  text: string;
  chunk_id?: number;
}

export interface AudioResponse {
  type: ResponseType.AUDIO;
  data: string; // Base64 encoded audio
  format: string;
  text: string;
  duration?: number;
}

export interface LLMCompleteResponse {
  type: ResponseType.LLM_COMPLETE;
  text: string;
  tts_enabled: boolean;
  token_count?: number;
}

export interface ErrorResponse {
  type: ResponseType.ERROR;
  message: string;
  error_code?: string;
  details?: any;
}

export interface PongResponse {
  type: ResponseType.PONG;
  timestamp: number;
  client_timestamp?: number;
}

export type WebSocketResponse = 
  | ContentResponse 
  | AudioResponse 
  | LLMCompleteResponse 
  | ErrorResponse 
  | PongResponse;

// Connection states
export enum ConnectionState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error'
}
