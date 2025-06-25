import { useDisclosure } from '@chakra-ui/react';
import { useWebSocket } from '@/context/websocket-context';
import { useInterrupt } from '@/components/canvas/live2d';
import { useChatHistory } from '@/context/chat-history-context';

export const useSidebar = () => {
  const { open, onOpen, onClose } = useDisclosure();
  const { sendMessage } = useWebSocket();
  const { interrupt } = useInterrupt();
  const { currentHistoryUid, messages, updateHistoryList } = useChatHistory();

  const createNewHistory = (): void => {
    if (currentHistoryUid && messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      updateHistoryList(currentHistoryUid, latestMessage);
    }

    interrupt();
    sendMessage({
      type: 'create-new-history',
    });
  };

  return {
    settingsOpen: open,
    onSettingsOpen: onOpen,
    onSettingsClose: onClose,
    createNewHistory,
  };
};
