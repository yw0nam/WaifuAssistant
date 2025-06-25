import { useRef, useCallback } from 'react';
import { useChatHistory } from '@/context/chat-history-context';

export function useChatHistoryPanel() {
  const { messages } = useChatHistory();
  const messageListRef = useRef<HTMLDivElement>(null);

  const handleMessageUpdate = useCallback(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, []);

  return {
    messages,
    messageListRef,
    handleMessageUpdate,
  };
}
