import { useState, useCallback, useRef } from 'react';
import { AudioQueue } from '../services/audioUtils';

export const useAudio = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentText, setCurrentText] = useState<string>('');
  const audioQueueRef = useRef<AudioQueue | null>(null);

  // Initialize audio queue if not already initialized
  const getAudioQueue = useCallback(() => {
    if (!audioQueueRef.current) {
      audioQueueRef.current = new AudioQueue(
        setIsPlaying,
        setCurrentText
      );
    }
    return audioQueueRef.current;
  }, []);

  const playAudio = useCallback((base64Data: string, format: string, text: string) => {
    const queue = getAudioQueue();
    queue.enqueue(base64Data, format, text);
  }, [getAudioQueue]);

  const stopAudio = useCallback(() => {
    const queue = getAudioQueue();
    queue.stop();
  }, [getAudioQueue]);

  const clearQueue = useCallback(() => {
    const queue = getAudioQueue();
    queue.clear();
  }, [getAudioQueue]);

  const getQueueLength = useCallback(() => {
    const queue = getAudioQueue();
    return queue.getQueueLength();
  }, [getAudioQueue]);

  return {
    isPlaying,
    currentText,
    playAudio,
    stopAudio,
    clearQueue,
    getQueueLength
  };
};
