// WebSocket message types matching backend models

export enum MessageType {
  CHAT = 'chat',
  PING = 'ping',
  TTS_INTERRUPT = 'tts_interrupt'
}

export enum ResponseType {
  CONTENT = 'content',
  AUDIO = 'audio',
  LLM_COMPLETE = 'llm_complete',
  ERROR = 'error',
  PONG = 'pong',
  TTS_INTERRUPTED = 'tts_interrupted',
  STREAMING_TTS = 'streaming_tts'  // New: For real-time TTS sentences
}

// Request types
export interface ChatRequest {
  type: MessageType.CHAT;
  text: string;
  enable_tts?: boolean;
  skip_internal_reasoning?: boolean;
  reference_id?: string;
  reasoning_start_tag?: string;
  reasoning_end_tag?: string;
}

export interface PingRequest {
  type: MessageType.PING;
  timestamp?: number;
}

export interface TTSInterruptRequest {
  type: MessageType.TTS_INTERRUPT;
  reason?: string;
}

export type WebSocketRequest = ChatRequest | PingRequest | TTSInterruptRequest;

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

export interface TTSInterruptedResponse {
  type: ResponseType.TTS_INTERRUPTED;
  message: string;
  interrupted_count?: number;
}

export interface StreamingTTSResponse {
  type: ResponseType.STREAMING_TTS;
  sentence: string;
  sentence_id: number;
  is_final: boolean;
}

export type WebSocketResponse = 
  | ContentResponse 
  | AudioResponse 
  | LLMCompleteResponse 
  | ErrorResponse 
  | PongResponse
  | TTSInterruptedResponse
  | StreamingTTSResponse;

// Connection states
export enum ConnectionState {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error'
}
