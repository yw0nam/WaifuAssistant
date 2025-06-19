// Chat related types

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  audioData?: string; // Base64 encoded audio
  isComplete?: boolean; // For streaming messages
  ttsProcessing?: boolean; // Whether TTS is currently processing
  lastTTSSentenceId?: number; // Last sentence ID processed for TTS
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  connectionState: import('./websocket').ConnectionState;
}

export interface AudioState {
  isPlaying: boolean;
  currentAudio?: HTMLAudioElement;
  queue: string[]; // Base64 audio queue
}
