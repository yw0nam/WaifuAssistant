// Audio utilities for handling Base64 encoded audio from TTS

export class AudioUtils {
  /**
   * Convert Base64 audio data to Audio element
   */
  static base64ToAudio(base64Data: string, format: string = 'wav'): HTMLAudioElement {
    const audio = new Audio();
    const mimeType = this.getMimeType(format);
    const dataUrl = `data:${mimeType};base64,${base64Data}`;
    audio.src = dataUrl;
    return audio;
  }

  /**
   * Get MIME type for audio format
   */
  private static getMimeType(format: string): string {
    const formatMap: { [key: string]: string } = {
      'wav': 'audio/wav',
      'mp3': 'audio/mpeg',
      'ogg': 'audio/ogg',
      'webm': 'audio/webm',
      'flac': 'audio/flac'
    };
    return formatMap[format.toLowerCase()] || 'audio/wav';
  }

  /**
   * Play audio with promise support
   */
  static async playAudio(audio: HTMLAudioElement): Promise<void> {
    return new Promise((resolve, reject) => {
      const handleEnded = () => {
        audio.removeEventListener('ended', handleEnded);
        audio.removeEventListener('error', handleError);
        resolve();
      };

      const handleError = (error: Event) => {
        audio.removeEventListener('ended', handleEnded);
        audio.removeEventListener('error', handleError);
        reject(error);
      };

      audio.addEventListener('ended', handleEnded);
      audio.addEventListener('error', handleError);

      audio.play().catch(reject);
    });
  }

  /**
   * Stop audio playback
   */
  static stopAudio(audio: HTMLAudioElement): void {
    if (!audio.paused) {
      audio.pause();
      audio.currentTime = 0;
    }
  }

  /**
   * Get audio duration (requires the audio to be loaded)
   */
  static getAudioDuration(audio: HTMLAudioElement): Promise<number> {
    return new Promise((resolve, reject) => {
      if (audio.duration) {
        resolve(audio.duration);
        return;
      }

      const handleLoadedMetadata = () => {
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audio.removeEventListener('error', handleError);
        resolve(audio.duration);
      };

      const handleError = (error: Event) => {
        audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
        audio.removeEventListener('error', handleError);
        reject(error);
      };

      audio.addEventListener('loadedmetadata', handleLoadedMetadata);
      audio.addEventListener('error', handleError);

      // Trigger loading if not already loading
      if (audio.readyState === HTMLMediaElement.HAVE_NOTHING) {
        audio.load();
      }
    });
  }
}

/**
 * Audio queue manager for handling sequential audio playback
 */
export class AudioQueue {
  private queue: Array<{ audio: HTMLAudioElement; text: string }> = [];
  private isPlaying = false;
  private currentAudio: HTMLAudioElement | null = null;
  private onPlayingStateChange?: (isPlaying: boolean) => void;
  private onCurrentTextChange?: (text: string) => void;

  constructor(
    onPlayingStateChange?: (isPlaying: boolean) => void,
    onCurrentTextChange?: (text: string) => void
  ) {
    this.onPlayingStateChange = onPlayingStateChange;
    this.onCurrentTextChange = onCurrentTextChange;
  }

  /**
   * Add audio to the queue
   */
  public enqueue(base64Data: string, format: string, text: string): void {
    const audio = AudioUtils.base64ToAudio(base64Data, format);
    this.queue.push({ audio, text });
    
    if (!this.isPlaying) {
      this.playNext();
    }
  }

  /**
   * Clear the queue and stop current playback
   */
  public clear(): void {
    this.queue = [];
    this.stop();
  }

  /**
   * Stop current playback
   */
  public stop(): void {
    if (this.currentAudio) {
      AudioUtils.stopAudio(this.currentAudio);
      this.currentAudio = null;
    }
    this.setPlayingState(false);
  }

  /**
   * Check if audio is currently playing
   */
  public getIsPlaying(): boolean {
    return this.isPlaying;
  }

  /**
   * Get current queue length
   */
  public getQueueLength(): number {
    return this.queue.length;
  }

  private async playNext(): Promise<void> {
    if (this.queue.length === 0) {
      this.setPlayingState(false);
      return;
    }

    const { audio, text } = this.queue.shift()!;
    this.currentAudio = audio;
    this.setPlayingState(true);
    
    if (this.onCurrentTextChange) {
      this.onCurrentTextChange(text);
    }

    try {
      await AudioUtils.playAudio(audio);
    } catch (error) {
      console.error('❌ Error playing audio:', error);
    } finally {
      this.currentAudio = null;
      // Continue to next audio in queue
      this.playNext();
    }
  }

  private setPlayingState(playing: boolean): void {
    if (this.isPlaying !== playing) {
      this.isPlaying = playing;
      if (this.onPlayingStateChange) {
        this.onPlayingStateChange(playing);
      }
    }
  }
}
