// Chat related types

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audioData?: string; // Base64 encoded audio
  isComplete?: boolean; // For streaming messages
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
