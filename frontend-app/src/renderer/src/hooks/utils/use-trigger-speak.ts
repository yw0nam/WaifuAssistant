import { useCallback } from 'react';
import { useWebSocket } from '@/context/websocket-context';
import { useMediaCapture } from './use-media-capture';

export function useTriggerSpeak() {
  const { sendMessage } = useWebSocket();
  const { captureAllMedia } = useMediaCapture();

  const sendTriggerSignal = useCallback(
    async (actualIdleTime: number) => {
      const images = await captureAllMedia();
      sendMessage({
        type: "ai-speak-signal",
        idle_time: actualIdleTime,
        images,
      });
    },
    [sendMessage, captureAllMedia],
  );

  return {
    sendTriggerSignal,
  };
}
